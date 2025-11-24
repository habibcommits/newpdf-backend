# Quick Deployment Guide - Azure App Service

## 🚀 Quick Start (5 Minutes)

Your app is ready for Azure! Here's the fastest way to deploy:

### Your App Details
- **URL**: https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net
- **Runtime**: Python 3.11
- **Plan**: B1 (Basic)
- **Region**: Germany West Central

---

## Option 1: GitHub Actions (Recommended)

### Setup Steps:
1. **Go to Azure Portal** → Your Web App (**newbackend**)
2. Click **Deployment Center** (left menu)
3. Select **GitHub** as source
4. Authorize and select:
   - Repository: `habibcommits/newpdfbackend`
   - Branch: `main`
5. Click **Save**

### Configure App Settings:
1. Go to **Configuration** → **Application settings**
2. Add these settings:

```
SCM_DO_BUILD_DURING_DEPLOYMENT = true
WEBSITES_PORT = 8000
CORS_ORIGINS = *
WORKERS = 2
TEMP_DIR = /tmp/pdf_temp
```

3. Go to **General settings** tab
4. Set **Startup Command**:
```
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 300
```

5. Click **Save** → **Continue**

### Test:
Visit: `https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/health`

✅ Done! Your app auto-deploys on every `git push`.

---

## Option 2: Azure CLI (Command Line)

### Install Azure CLI:
```bash
# Windows
winget install Microsoft.AzureCLI

# Mac
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Deploy:
```bash
# Login
az login

# Configure settings
az webapp config appsettings set \
  --resource-group newbakend \
  --name newbackend \
  --settings \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    WEBSITES_PORT=8000 \
    CORS_ORIGINS="*" \
    WORKERS=2 \
    TEMP_DIR="/tmp/pdf_temp"

# Set startup command
az webapp config set \
  --resource-group newbakend \
  --name newbackend \
  --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 300"

# Deploy from GitHub
az webapp deployment source config \
  --name newbackend \
  --resource-group newbakend \
  --repo-url https://github.com/habibcommits/newpdfbackend \
  --branch main \
  --manual-integration
```

---

## Important Files in This Repository

✅ `main.py` - FastAPI application
✅ `requirements.txt` - Python dependencies (includes gunicorn)
✅ `startup.txt` - Startup command for Azure
✅ `.deployment` - Azure build configuration
✅ `config.py` - App configuration
✅ `utils.py` - PDF processing utilities

---

## Testing Your Deployment

### 1. Health Check
```bash
curl https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/health
```

### 2. API Docs
Open in browser:
```
https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/docs
```

### 3. Test Image to PDF
```bash
curl -X POST \
  https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/api/image-to-pdf \
  -F "files=@image.jpg" \
  -o output.pdf
```

---

## Troubleshooting

### View Logs
```bash
# Azure CLI
az webapp log tail --resource-group newbakend --name newbackend

# Or in Azure Portal
Go to: newbackend → Log stream
```

### Common Issues

**"Application Error"**
- Check logs for specific errors

**"502 Bad Gateway"**
- Verify `WEBSITES_PORT=8000` is set
- Check startup command is correct

**"Module not found"**
- Rebuild: `az webapp deployment source sync --resource-group newbakend --name newbackend`

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |
| `/api/image-to-pdf` | POST | Convert images to PDF |
| `/api/merge-pdf` | POST | Merge multiple PDFs |
| `/api/compress-pdf` | POST | Compress PDF file |

---

## Enable HTTPS Only (Recommended)

```bash
az webapp update \
  --resource-group newbakend \
  --name newbackend \
  --https-only true
```

---

## Need More Details?

📖 See **AZURE_APP_SERVICE_CODE_DEPLOYMENT.md** for complete documentation including:
- All deployment methods
- Advanced configuration
- Custom domains and SSL
- Scaling and performance
- Security best practices
- CI/CD setup
- Monitoring and troubleshooting

---

## Quick Commands

```bash
# Restart app
az webapp restart --resource-group newbakend --name newbackend

# View settings
az webapp config appsettings list --resource-group newbakend --name newbackend

# Stop app
az webapp stop --resource-group newbakend --name newbackend

# Start app
az webapp start --resource-group newbakend --name newbackend
```

---

**Your app is ready! Choose your deployment method above and get started. 🚀**
