import os
import io
import time
import uuid
import asyncio
from pathlib import Path
from typing import List, BinaryIO, Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import img2pdf
import PyPDF2
import fitz
from config import settings

def generate_unique_filename(extension: str = "pdf") -> str:
    timestamp = int(time.time() * 1000)
    unique_id = uuid.uuid4().hex[:8]
    return f"{timestamp}_{unique_id}.{extension}"

async def save_upload_file(upload_file: UploadFile, destination: Path) -> Path:
    try:
        content = await upload_file.read()
        with open(destination, "wb") as f:
            f.write(content)
        return destination
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

def cleanup_files(*file_paths: Optional[Path]):
    if not settings.CLEANUP_TEMP_FILES:
        return
    
    for file_path in file_paths:
        try:
            if file_path and file_path.exists():
                os.remove(file_path)
        except Exception:
            pass

async def convert_images_to_pdf(image_files: List[Path], output_path: Path) -> Path:
    temp_rgb_files = []
    try:
        valid_images = []
        
        for img_path in image_files:
            try:
                with Image.open(img_path) as img:
                    if img.mode in ("RGBA", "LA", "P"):
                        rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        
                        if img.mode in ("RGBA", "LA"):
                            try:
                                alpha = img.getchannel('A') if img.mode == "RGBA" else img.getchannel('L')
                                rgb_img.paste(img, mask=alpha)
                            except Exception:
                                rgb_img.paste(img)
                        else:
                            rgb_img.paste(img)
                        
                        temp_rgb_path = img_path.with_suffix('.temp.jpg')
                        rgb_img.save(temp_rgb_path, "JPEG", quality=95, optimize=True)
                        valid_images.append(str(temp_rgb_path))
                        temp_rgb_files.append(temp_rgb_path)
                    else:
                        valid_images.append(str(img_path))
                        
            except Exception as e:
                cleanup_files(*temp_rgb_files)
                raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
        
        if not valid_images:
            raise HTTPException(status_code=400, detail="No valid images provided")
        
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(valid_images))
        
        cleanup_files(*temp_rgb_files)
        
        return output_path
        
    except HTTPException:
        cleanup_files(*temp_rgb_files)
        raise
    except Exception as e:
        cleanup_files(*temp_rgb_files)
        raise HTTPException(status_code=500, detail=f"Image to PDF conversion failed: {str(e)}")

async def merge_pdfs(pdf_files: List[Path], output_path: Path) -> Path:
    try:
        merger = PyPDF2.PdfMerger()
        
        for pdf_path in pdf_files:
            try:
                merger.append(str(pdf_path))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid PDF file: {str(e)}")
        
        with open(output_path, "wb") as output_file:
            merger.write(output_file)
        
        merger.close()
        return output_path
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF merge failed: {str(e)}")

async def compress_pdf(
    input_path: Path,
    output_path: Path,
    dpi: int = 96,
    image_quality: int = 60,
    color_mode: str = "no-change"
) -> Path:
    try:
        doc = fitz.open(str(input_path))
        writer = fitz.open()
        
        target_dpi = min(dpi, 100)
        zoom = target_dpi / 72.0
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False, dpi=target_dpi)
            
            pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            target_width = int(pix.width * 0.7)
            target_height = int(pix.height * 0.7)
            pil_image = pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            if color_mode == "grayscale":
                pil_image = pil_image.convert("L")
            elif color_mode == "monochrome":
                pil_image = pil_image.convert("L").convert("1")
            
            img_buffer = io.BytesIO()
            
            if color_mode == "monochrome":
                pil_image.save(img_buffer, format="PNG", optimize=True, compress_level=9)
            else:
                actual_quality = min(image_quality, 50)
                pil_image.save(img_buffer, format="JPEG", quality=actual_quality, optimize=True, progressive=True)
            
            img_buffer.seek(0)
            img_bytes = img_buffer.getvalue()
            
            new_page = writer.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(page.rect, stream=img_bytes)
            
            pix = None
            pil_image = None
        
        doc.close()
        
        writer.save(
            str(output_path),
            garbage=4,
            deflate=True,
            clean=True,
            deflate_images=True,
            deflate_fonts=True
        )
        writer.close()
        
        original_size = input_path.stat().st_size
        compressed_size = output_path.stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        print(f"Compression complete: {original_size} -> {compressed_size} bytes ({compression_ratio:.1f}% reduction)")
        
        return output_path
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF compression failed: {str(e)}")
