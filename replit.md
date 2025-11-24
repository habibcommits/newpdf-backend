# Overview

PDF Tools API is a high-performance FastAPI backend service with an interactive HTML frontend for PDF manipulation operations. The application provides three core functionalities: converting images to PDFs, merging multiple PDFs into a single document, and compressing PDFs with configurable quality settings. Built with asynchronous processing capabilities, the API is optimized for speed and can handle files under 10MB in under 10 seconds. The service is containerized with Docker for cloud deployment and includes built-in health monitoring endpoints.

# Recent Changes

**November 24, 2025 - Latest**
- Configured for Azure App Service Code deployment (Python 3.11 on Linux)
- Added `startup.txt` with Gunicorn command optimized for B1 plan (2 workers)
- Added `.deployment` file for Azure build configuration
- Updated `requirements.txt` to include Gunicorn for production
- Created comprehensive deployment guides:
  - `DEPLOYMENT_QUICKSTART.md` - 5-minute quick start guide
  - `AZURE_APP_SERVICE_CODE_DEPLOYMENT.md` - Complete deployment documentation
  - `README_AZURE_DEPLOYMENT.md` - Project overview and reference
- Optimized for Azure App Service B1 plan (1 vCPU, 1.75 GB RAM)

**November 23, 2025**
- Removed HTML frontend (index.html) to focus on API-only deployment
- Keep only the FastAPI backend endpoints for production use
- Implemented all three PDF endpoints (image-to-PDF, merge, compress)
- Added BackgroundTasks to all endpoints for automatic temporary file cleanup (prevents disk leaks)
- Created comprehensive Docker configuration for Azure deployment
- Added complete documentation (README.md, AZURE_DEPLOYMENT.md, .env.example)
- Verified production-ready status with architect review

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
**Decision**: FastAPI with asynchronous processing  
**Rationale**: FastAPI provides high-performance async capabilities, automatic API documentation, and built-in validation. The async processing enables handling multiple file operations concurrently without blocking.  
**Implementation**: Uses `uvicorn` as the ASGI server with configurable workers (default 4) for production deployments.

## File Processing Libraries
**Decision**: Multiple specialized libraries for different PDF operations
- `img2pdf` for image-to-PDF conversion (optimized fast conversion)
- `PyPDF2` for PDF merging (efficient stream concatenation)
- `PyMuPDF (fitz)` for PDF compression (image extraction and optimization)
- `Pillow` for image preprocessing (format conversion, resizing, and quality optimization)

**Rationale**: Each library is optimized for specific operations rather than using a single general-purpose library. This provides better performance and document integrity.

**Implementation Details**:
- Image-to-PDF: Handles RGBA/LA/P color modes, converts to RGB/JPEG as needed
- PDF Merge: Uses PyPDF2.PdfMerger for memory-efficient concatenation
- PDF Compression: Extracts embedded images, compresses them with configurable DPI/quality/color settings, and replaces them in the PDF while preserving text layers. Uses PyMuPDF's save options (garbage=4, deflate=True, clean=True) for additional optimization.

## Frontend
**Status**: Removed  
**Rationale**: Focused on API-only backend for production deployment

## File Handling Strategy
**Decision**: Temporary file storage with async upload/download and BackgroundTasks cleanup  
**Rationale**: Files are saved to a temporary directory (`./temp` by default) during processing and cleaned up afterward using FastAPI's BackgroundTasks. This prevents memory overflow with large files and ensures automatic cleanup of temporary files after responses are sent.  
**Features**: 
- Unique filename generation using timestamp + UUID
- Automatic cleanup via BackgroundTasks (prevents disk leaks)
- Configurable cleanup (can be disabled for debugging)
- File size limits (default 100MB per file)
- Request limits (default 50 files per request)

## Configuration Management
**Decision**: Environment-based configuration with sensible defaults  
**Rationale**: Uses `python-dotenv` for loading environment variables, allowing easy configuration across development, staging, and production environments without code changes.  
**Key configurations**:
- API metadata (title, version, description)
- Server settings (host, port, workers)
- File processing limits
- PDF compression defaults (DPI: 144, quality: 75%)
- Timeout settings (300 seconds default)

## CORS Configuration
**Decision**: Configurable CORS with wildcard default  
**Rationale**: Enables frontend integration from any origin by default (can be restricted via environment variable). Production deployments should specify allowed origins explicitly.

## Error Handling
**Decision**: HTTPException-based error responses  
**Rationale**: FastAPI's HTTPException provides structured error responses with appropriate status codes, making debugging easier for API consumers.

## Performance Optimizations
- Asynchronous file I/O using `aiofiles`
- Image preprocessing (RGBA/LA/P to RGB conversion) before PDF generation
- Configurable DPI and quality settings for compression
- Background task cleanup to prevent blocking responses

# External Dependencies

## Python Libraries
- **FastAPI**: Web framework and API routing
- **Uvicorn**: ASGI server for async support
- **Gunicorn**: Production WSGI server (added for Azure App Service)
- **Pillow**: Image processing and format conversion
- **img2pdf**: Optimized image-to-PDF conversion
- **PyPDF2**: PDF manipulation and merging
- **PyMuPDF (fitz)**: Advanced PDF compression and rendering
- **python-dotenv**: Environment variable management
- **aiofiles**: Asynchronous file operations

## Deployment Infrastructure

### Current Deployment: Azure App Service (Code Deployment)
- **Platform**: Azure App Service for Linux
- **Runtime**: Python 3.11
- **Server**: Gunicorn with Uvicorn workers
- **Plan**: Basic B1 (1 vCPU, 1.75 GB RAM)
- **Region**: Germany West Central
- **Workers**: 2 (optimized for B1 plan)
- **Startup**: `gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 300`

### Alternative Deployment Options
- **Docker**: Containerization for consistent deployment
- **Azure Container Instances (ACI)**: Serverless container deployment
- **Azure Kubernetes Service (AKS)**: Enterprise-scale container orchestration
- **Azure Container Registry (ACR)**: Private container image storage

## No Database Required
This application is stateless and does not persist data beyond temporary file processing. All operations are request-scoped with automatic cleanup.

## No Authentication Layer
The current implementation does not include authentication or authorization. API access is unrestricted, suitable for internal services or MVP deployments. Production deployments should add API keys or OAuth2 authentication.