# PDF Tools API - Azure Deployment Ready

## 📋 Overview

This is a high-performance PDF processing API built with FastAPI, ready for deployment on Azure App Service using **Code deployment** (Python 3.11 on Linux).

## 🚀 Quick Deploy to Azure

Your Azure configuration:
- **App Name**: newbackend
- **URL**: https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net
- **Runtime**: Python 3.11
- **Plan**: B1 (Basic)
- **Region**: Germany West Central

### Choose Your Deployment Method:

1. **[5 Minutes] GitHub Actions** - See `DEPLOYMENT_QUICKSTART.md`
2. **[Complete Guide] Azure CLI & More** - See `AZURE_APP_SERVICE_CODE_DEPLOYMENT.md`

## 📁 Project Structure

```
pdf-tools-api/
├── main.py                              # FastAPI application entry point
├── config.py                            # Configuration management
├── utils.py                             # PDF processing utilities
├── requirements.txt                     # Python dependencies (with gunicorn)
├── startup.txt                          # Azure startup command
├── .deployment                          # Azure build configuration
├── .gitignore                          # Git ignore rules
├── .env.example                        # Environment variables template
│
├── DEPLOYMENT_QUICKSTART.md            # ⭐ Quick 5-minute deployment guide
├── AZURE_APP_SERVICE_CODE_DEPLOYMENT.md # ⭐ Complete deployment documentation
├── README.md                           # Original project documentation
├── AZURE_DEPLOYMENT.md                 # Container deployment guide
├── CHANGELOG.md                        # Project changelog
└── replit.md                           # Project notes
```

## ✅ Azure-Ready Files

This repository includes everything needed for Azure App Service Code deployment:

### Required Files (Already Configured ✅)

1. **`requirements.txt`** - All Python dependencies including:
   - FastAPI 0.104.1
   - Uvicorn 0.24.0
   - Gunicorn 21.2.0 (production server)
   - PDF processing libraries (Pillow, PyPDF2, PyMuPDF, img2pdf)

2. **`startup.txt`** - Azure startup command:
   ```bash
   gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 300
   ```
   - Optimized for B1 plan (2 workers)
   - 5-minute timeout for large PDF processing
   - Uvicorn workers for async support

3. **`.deployment`** - Azure build configuration:
   ```ini
   [config]
   SCM_DO_BUILD_DURING_DEPLOYMENT=true
   ```

4. **`main.py`** - FastAPI application with:
   - CORS middleware configured
   - Health check endpoint (`/health`)
   - PDF processing endpoints
   - File cleanup and error handling

5. **`config.py`** - Environment-based configuration using Pydantic

6. **`utils.py`** - PDF processing utilities

## 🔧 Required Azure Configuration

After deployment, configure these **Application Settings** in Azure Portal:

| Setting | Value | Description |
|---------|-------|-------------|
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | Enable pip install during deployment |
| `WEBSITES_PORT` | `8000` | Port the app listens on |
| `CORS_ORIGINS` | `*` | CORS origins (change to your domain) |
| `WORKERS` | `2` | Gunicorn workers (2 for B1 plan) |
| `TEMP_DIR` | `/tmp/pdf_temp` | Temporary file directory |
| `MAX_FILE_SIZE_MB` | `100` | Maximum upload file size |
| `MAX_FILES_PER_REQUEST` | `50` | Maximum files per request |

**Startup Command** (in General Settings):
```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 300
```

## 🎯 API Endpoints

Once deployed, your API will have these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and status |
| `/docs` | GET | Interactive API documentation (Swagger UI) |
| `/redoc` | GET | Alternative API documentation |
| `/api/image-to-pdf` | POST | Convert images to PDF |
| `/api/merge-pdf` | POST | Merge multiple PDFs |
| `/api/compress-pdf` | POST | Compress PDF with quality settings |

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1700000000.0,
  "version": "0.1.0",
  "temp_dir_writable": true,
  "temp_dir_path": "/tmp/pdf_temp"
}
```

### 2. Interactive API Docs
Open in browser:
```
https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/docs
```

### 3. Test Image to PDF Conversion
```bash
curl -X POST \
  https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/api/image-to-pdf \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  -o result.pdf
```

### 4. Test PDF Compression
```bash
curl -X POST \
  https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/api/compress-pdf \
  -F "file=@document.pdf" \
  -F "dpi=72" \
  -F "image_quality=40" \
  -o compressed.pdf
```

## 📚 Documentation

- **Quick Start**: `DEPLOYMENT_QUICKSTART.md` - 5-minute deployment guide
- **Complete Guide**: `AZURE_APP_SERVICE_CODE_DEPLOYMENT.md` - Full documentation including:
  - 5 different deployment methods
  - Configuration details
  - Environment variables
  - Custom domains and HTTPS
  - Scaling and performance tuning
  - Monitoring and troubleshooting
  - Security best practices
  - CI/CD setup with GitHub Actions
  - Cost optimization

## 🔐 Security Recommendations

1. **Update CORS** - Change from `*` to your actual frontend domain
2. **Enable HTTPS Only** - Force all traffic through HTTPS
3. **Enable Health Check** - Configure health monitoring at `/health`
4. **Use Azure Key Vault** - Store sensitive secrets securely
5. **Enable Application Insights** - Monitor performance and errors

## 📊 Performance Tuning

### For B1 Plan (Your Current Plan)
- **Workers**: 2 (configured in startup.txt)
- **Memory**: 1.75 GB
- **vCPU**: 1
- **Suitable for**: Low to medium traffic

### Scaling Up Options
- **B2**: 2 vCPU, 3.5 GB RAM → Use 4 workers
- **B3**: 4 vCPU, 7 GB RAM → Use 4-6 workers
- **S1/S2/S3**: Auto-scaling support

## 🛠️ Troubleshooting

### View Logs
```bash
# Azure CLI
az webapp log tail --resource-group newbakend --name newbackend

# Or in Azure Portal: newbackend → Log stream
```

### Common Issues

1. **502 Bad Gateway**
   - Verify `WEBSITES_PORT=8000` is set
   - Check startup command

2. **Application Error**
   - Check logs for specific errors
   - Verify all dependencies in requirements.txt

3. **Module Not Found**
   - Ensure `SCM_DO_BUILD_DURING_DEPLOYMENT=true`
   - Trigger rebuild

See `AZURE_APP_SERVICE_CODE_DEPLOYMENT.md` for detailed troubleshooting.

## 🎓 Development vs Production

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn (development server)
uvicorn main:app --reload --port 8000

# Or use the provided startup for testing
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000
```

### Azure Production
- Uses Gunicorn as production WSGI server
- Uvicorn workers for async support
- 2 workers optimized for B1 plan
- 5-minute timeout for large file processing

## 📞 Support

- **Azure Documentation**: https://docs.microsoft.com/azure/app-service/
- **Azure Support**: https://portal.azure.com (Support + troubleshooting)
- **Project Issues**: [GitHub Issues](https://github.com/habibcommits/newpdfbackend/issues)

## 🚀 Next Steps

1. ✅ Review `DEPLOYMENT_QUICKSTART.md`
2. ✅ Choose your deployment method
3. ✅ Configure application settings in Azure
4. ✅ Deploy your app
5. ✅ Test all endpoints
6. ✅ Enable health checks
7. ✅ Set up monitoring
8. ✅ Configure custom domain (optional)

## 📝 License

[Your License Here]

---

**Ready to deploy? Start with `DEPLOYMENT_QUICKSTART.md` for a 5-minute deployment! 🚀**
