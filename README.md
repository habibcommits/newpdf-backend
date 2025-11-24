# PDF Tools API

A high-performance FastAPI backend for PDF operations including image-to-PDF conversion, PDF merging, and PDF compression. Optimized for speed with processing times under 10 seconds for files under 100MB.

## Features

- **Image to PDF Conversion**: Convert multiple images (JPEG, PNG, etc.) into a single PDF
- **PDF Merging**: Combine multiple PDF files into one document
- **PDF Compression**: Reduce PDF file size with configurable DPI, image quality, and color mode
  - Renders pages at specified DPI and re-encodes with quality settings (fixed in v0.1.1)
  - Note: Converts pages to images for compression
  - Compression metrics logging for monitoring
- **High Performance**: Async processing with optimized libraries
- **File Size Validation**: Prevents processing of files exceeding configured limits
- **Docker Support**: Production-ready containerization for Azure deployment
- **CORS Enabled**: Properly configured wildcard or specific origins
- **Health Checks**: Built-in health monitoring with temp directory validation
- **Pydantic Settings**: Type-safe configuration management
- **Cache Control**: Proper HTTP headers to prevent stale cached responses

## API Endpoints

### Root Endpoint
```
GET /
```
Returns API information and available endpoints.

### Health Check
```
GET /health
```
Returns API health status, version, and temp directory status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1700000000.0,
  "version": "0.1.0",
  "temp_dir_writable": true,
  "temp_dir_path": "./temp"
}
```

### Image to PDF
```
POST /api/image-to-pdf
```
Convert multiple images to a single PDF.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `files` (array of image files)

**Response:**
- Content-Type: `application/pdf`
- Returns the generated PDF file

### Merge PDFs
```
POST /api/merge-pdf
```
Merge multiple PDF files into one.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `files` (array of PDF files, minimum 2 required)

**Response:**
- Content-Type: `application/pdf`
- Returns the merged PDF file

### Compress PDF
```
POST /api/compress-pdf?dpi=144&image_quality=75&color_mode=no-change
```
Compress a PDF file with advanced options.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (single PDF file)
- Query Parameters:
  - `dpi`: Integer (72-300, default: 144)
  - `image_quality`: Integer (1-100, default: 75)
  - `color_mode`: String (`no-change`, `grayscale`, `monochrome`, default: `no-change`)

**Response:**
- Content-Type: `application/pdf`
- Returns the compressed PDF file

## Quick Start

### Local Development

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd pdf-tools-api
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create .env file:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application:**
```bash
python main.py
# Or use uvicorn directly:
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

6. **Access the API:**
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Docker Deployment

1. **Build the Docker image:**
```bash
docker build -t pdf-tools-api .
```

2. **Run with Docker Compose:**
```bash
docker-compose up -d
```

3. **Check logs:**
```bash
docker-compose logs -f
```

4. **Stop the service:**
```bash
docker-compose down
```

## Environment Variables

Configuration uses Pydantic Settings for type-safe environment variable management.

Key variables:
- `CORS_ORIGINS`: Use "*" for all origins, or comma-separated list (default: "*")
- `MAX_FILE_SIZE_MB`: Maximum file size in megabytes (default: 100)
- `MAX_FILES_PER_REQUEST`: Maximum number of files per request (default: 50)
- `WORKERS`: Number of uvicorn workers for production (default: 4)
- `TEMP_DIR`: Directory for temporary file storage (default: "./temp")
- `CLEANUP_TEMP_FILES`: Auto-cleanup temp files (default: true)
- `PROCESS_TIMEOUT_SECONDS`: Max processing time per request (default: 300)

See `.env.example` for all available configuration options.

## Performance Optimization

This API is optimized for speed:

1. **Async Processing**: All file operations use async/await for non-blocking I/O
2. **Efficient Libraries**: 
   - `img2pdf` for fast image-to-PDF conversion
   - `PyPDF2` for efficient PDF merging
   - `PyMuPDF (fitz)` for advanced PDF compression
3. **Multi-worker Support**: Uvicorn with multiple workers for concurrent requests
4. **Smart File Cleanup**: Automatic temporary file management
5. **Image Optimization**: Automatic format conversion and compression

## Azure Deployment

See [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) for detailed instructions on deploying to Azure with SSL/HTTPS.

## Project Structure

```
pdf-tools-api/
├── main.py                 # FastAPI application
├── config.py              # Configuration management
├── utils.py               # PDF processing utilities
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container configuration
├── docker-compose.yml    # Docker Compose configuration
├── .env.example          # Environment variables template
├── .dockerignore         # Docker ignore file
├── .gitignore           # Git ignore file
├── README.md            # This file
└── AZURE_DEPLOYMENT.md  # Azure deployment guide
```

## API Response Codes

- `200`: Success - Returns PDF file
- `400`: Bad Request - Invalid file type or parameters
- `422`: Validation Error - Missing or invalid request data
- `500`: Internal Server Error - Processing failed

## Testing the API

### Using cURL

**Image to PDF:**
```bash
curl -X POST "http://localhost:8000/api/image-to-pdf" \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  -o output.pdf
```

**Merge PDFs:**
```bash
curl -X POST "http://localhost:8000/api/merge-pdf" \
  -F "files=@file1.pdf" \
  -F "files=@file2.pdf" \
  -o merged.pdf
```

**Compress PDF:**
```bash
curl -X POST "http://localhost:8000/api/compress-pdf?dpi=144&image_quality=75" \
  -F "file=@input.pdf" \
  -o compressed.pdf
```

### Using the Interactive Docs

Visit http://localhost:8000/docs for an interactive Swagger UI where you can test all endpoints directly in your browser.

## Security Notes

- File uploads are validated by content type
- Temporary files are automatically cleaned up on success and failure
- Maximum file size configurable via MAX_FILE_SIZE_MB setting
- CORS is properly configured for wildcard (*) or specific origins
- Credentials disabled when using wildcard CORS for security
- Improved error handling prevents temporary file leaks

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue in the repository.
