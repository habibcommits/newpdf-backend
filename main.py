import os
import time
from pathlib import Path
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from utils import (
    generate_unique_filename,
    save_upload_file,
    cleanup_files,
    convert_images_to_pdf,
    merge_pdfs,
    compress_pdf
)

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False if settings.CORS_ORIGINS == "*" else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    temp_dir = Path(settings.TEMP_DIR)
    temp_dir_writable = os.access(temp_dir, os.W_OK) if temp_dir.exists() else False
    
    return {
        "status": "healthy" if temp_dir_writable else "degraded",
        "timestamp": time.time(),
        "version": settings.API_VERSION,
        "temp_dir_writable": temp_dir_writable,
        "temp_dir_path": str(temp_dir)
    }

@app.post("/api/image-to-pdf")
async def image_to_pdf(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > settings.MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {settings.MAX_FILES_PER_REQUEST} files allowed"
        )
    
    temp_files = []
    
    try:
        for upload_file in files:
            if not upload_file.content_type or not upload_file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {upload_file.filename} is not an image"
                )
            
            file_ext = upload_file.filename.split('.')[-1] if upload_file.filename else "tmp"
            temp_path = Path(settings.TEMP_DIR) / f"upload_{generate_unique_filename(file_ext)}"
            await save_upload_file(upload_file, temp_path)
            temp_files.append(temp_path)
        
        output_filename = generate_unique_filename("pdf")
        output_path = Path(settings.TEMP_DIR) / output_filename
        
        await convert_images_to_pdf(temp_files, output_path)
        
        cleanup_files(*temp_files)
        
        background_tasks.add_task(cleanup_files, output_path)
        
        return FileResponse(
            path=output_path,
            filename=f"converted_{output_filename}",
            media_type="application/pdf",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except HTTPException:
        cleanup_files(*temp_files)
        raise
    except Exception as e:
        cleanup_files(*temp_files)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/api/merge-pdf")
async def merge_pdf_endpoint(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 PDF files required for merging")
    
    if len(files) > settings.MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {settings.MAX_FILES_PER_REQUEST} files allowed"
        )
    
    temp_files = []
    
    try:
        for upload_file in files:
            if not upload_file.content_type or upload_file.content_type != "application/pdf":
                raise HTTPException(
                    status_code=400,
                    detail=f"File {upload_file.filename} is not a PDF"
                )
            
            temp_path = Path(settings.TEMP_DIR) / f"upload_{generate_unique_filename('pdf')}"
            await save_upload_file(upload_file, temp_path)
            temp_files.append(temp_path)
        
        output_filename = generate_unique_filename("pdf")
        output_path = Path(settings.TEMP_DIR) / output_filename
        
        await merge_pdfs(temp_files, output_path)
        
        cleanup_files(*temp_files)
        
        background_tasks.add_task(cleanup_files, output_path)
        
        return FileResponse(
            path=output_path,
            filename=f"merged_{output_filename}",
            media_type="application/pdf",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except HTTPException:
        cleanup_files(*temp_files)
        raise
    except Exception as e:
        cleanup_files(*temp_files)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/api/compress-pdf")
async def compress_pdf_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    dpi: int = Query(default=72, ge=72, le=300),
    image_quality: int = Query(default=40, ge=1, le=100),
    color_mode: str = Query(default="no-change")
):
    if not file.content_type or file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    if color_mode not in ["no-change", "grayscale", "monochrome"]:
        raise HTTPException(
            status_code=400,
            detail="color_mode must be one of: no-change, grayscale, monochrome"
        )
    
    temp_input_path = None
    output_path = None
    
    try:
        temp_input_path = Path(settings.TEMP_DIR) / f"input_{generate_unique_filename('pdf')}"
        await save_upload_file(file, temp_input_path)
        
        output_filename = generate_unique_filename("pdf")
        output_path = Path(settings.TEMP_DIR) / output_filename
        
        await compress_pdf(
            temp_input_path,
            output_path,
            dpi=dpi,
            image_quality=image_quality,
            color_mode=color_mode
        )
        
        cleanup_files(temp_input_path)
        
        background_tasks.add_task(cleanup_files, output_path)
        
        return FileResponse(
            path=output_path,
            filename=f"compressed_{output_filename}",
            media_type="application/pdf",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except HTTPException:
        cleanup_files(temp_input_path, output_path)
        raise
    except Exception as e:
        cleanup_files(temp_input_path, output_path)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=False
    )
