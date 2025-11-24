# Azure App Service Code Deployment Guide

This guide provides step-by-step instructions for deploying the PDF Tools API to Azure App Service using **Code deployment** (not containers) with Python 3.11.

## Your Azure Configuration

Based on your setup:
- **Resource Group**: newbakend
- **Location**: Germany West Central
- **Web App Name**: newbackend
- **Runtime Stack**: Python 3.11
- **Operating System**: Linux
- **App Service Plan**: ASP-newbakend-bb36 (B1)
- **Default Domain**: `newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net`
- **GitHub Repository**: https://github.com/habibcommits/newpdfbackend

## Prerequisites

✅ Azure subscription (Azure for Students)
✅ GitHub repository with your code
✅ Azure CLI installed (optional, for command-line deployment)
✅ Git installed on your local machine

## Deployment Methods

You can deploy your application using any of these methods:

### Method 1: GitHub Actions (Recommended - CI/CD)
### Method 2: Local Git Deployment
### Method 3: Azure Portal (Manual Upload)
### Method 4: Azure CLI
### Method 5: VS Code Extension

---

## Method 1: GitHub Actions Deployment (Recommended)

This method automatically deploys your app whenever you push changes to GitHub.

### Step 1: Configure Deployment Center in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Web App: **newbackend**
3. In the left menu, click **Deployment Center**
4. Click **Settings** tab

### Step 2: Setup GitHub Integration

1. **Source**: Select **GitHub**
2. Click **Authorize** to connect your GitHub account
3. **Organization**: Select your GitHub username
4. **Repository**: Select **newpdfbackend**
5. **Branch**: Select **main** (or your default branch)
6. Click **Save**

Azure will automatically:
- Create a GitHub Actions workflow file (`.github/workflows/`)
- Set up deployment credentials as GitHub Secrets
- Trigger the first deployment

### Step 3: Configure Application Settings

1. In Azure Portal, go to your Web App **newbackend**
2. Click **Configuration** (under Settings)
3. Under **Application settings**, add the following:

| Name | Value | Description |
|------|-------|-------------|
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | Enable build during deployment |
| `WEBSITES_PORT` | `8000` | Port your app listens on |
| `CORS_ORIGINS` | `*` | CORS origins (update to your frontend domain) |
| `MAX_FILE_SIZE_MB` | `100` | Maximum file size |
| `MAX_FILES_PER_REQUEST` | `50` | Maximum files per request |
| `TEMP_DIR` | `/tmp/pdf_temp` | Temporary directory for file processing |
| `WORKERS` | `2` | Number of Gunicorn workers (for B1: use 2) |

4. Click **Save** and **Continue**

### Step 4: Configure Startup Command

1. Still in **Configuration**, go to **General settings** tab
2. **Startup Command**: Enter the following:
   ```
   gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 300
   ```
3. Click **Save**

### Step 5: Verify Deployment

1. Wait for GitHub Actions workflow to complete (check your GitHub repo → Actions tab)
2. Visit your app: `https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/health`
3. You should see a JSON response with status information

### Step 6: Test API Endpoints

Test your endpoints:
```bash
# Health check
curl https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/health

# API documentation
# Open in browser: https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/docs
```

---

## Method 2: Local Git Deployment

### Step 1: Enable Local Git in Azure Portal

1. Go to **Deployment Center** in your Web App
2. **Source**: Select **Local Git**
3. Click **Save**
4. Copy the **Git Clone Uri** (will look like: `https://newbackend.scm.azurewebsites.net:443/newbackend.git`)

### Step 2: Get Deployment Credentials

1. In **Deployment Center**, click **Local Git/FTPS credentials**
2. Under **Application scope**, set:
   - **Username**: Choose a username (e.g., `pdf-deploy-user`)
   - **Password**: Set a strong password
3. Click **Save**
4. Note down your credentials

### Step 3: Add Azure Remote to Your Local Repository

On your local machine:
```bash
# Navigate to your project directory
cd /path/to/newpdfbackend

# Add Azure as a remote
git remote add azure https://<username>@newbackend.scm.azurewebsites.net:443/newbackend.git

# Push to Azure
git push azure main
```

You'll be prompted for the password you set earlier.

### Step 4: Monitor Deployment

Watch the deployment logs in your terminal. Once complete, test your app.

---

## Method 3: Azure Portal Manual Upload

### Step 1: Prepare Your Application

On your local machine:
```bash
# Create a zip file of your project
zip -r app.zip . -x "*.git*" "*.pyc" "__pycache__/*" "venv/*" "temp/*"
```

### Step 2: Upload via Azure Portal

1. Go to **Deployment Center** → **FTPS credentials**
2. Note the **FTPS endpoint** and credentials
3. Use an FTP client (FileZilla, WinSCP) or Azure CLI:

```bash
az webapp deployment source config-zip \
  --resource-group newbakend \
  --name newbackend \
  --src app.zip
```

---

## Method 4: Azure CLI Deployment

### Step 1: Install Azure CLI

```bash
# Windows (using winget)
winget install -e --id Microsoft.AzureCLI

# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Step 2: Login to Azure

```bash
az login
```

### Step 3: Deploy from GitHub

```bash
# Configure GitHub deployment
az webapp deployment source config \
  --name newbackend \
  --resource-group newbakend \
  --repo-url https://github.com/habibcommits/newpdfbackend \
  --branch main \
  --manual-integration
```

### Step 4: Configure App Settings via CLI

```bash
az webapp config appsettings set \
  --resource-group newbakend \
  --name newbackend \
  --settings \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    WEBSITES_PORT=8000 \
    CORS_ORIGINS="*" \
    MAX_FILE_SIZE_MB=100 \
    MAX_FILES_PER_REQUEST=50 \
    TEMP_DIR="/tmp/pdf_temp" \
    WORKERS=2
```

### Step 5: Set Startup Command via CLI

```bash
az webapp config set \
  --resource-group newbakend \
  --name newbackend \
  --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 300"
```

---

## Method 5: VS Code Extension

### Step 1: Install Azure Extension

1. Open VS Code
2. Install **Azure App Service** extension
3. Sign in to Azure

### Step 2: Deploy

1. Right-click your project folder
2. Select **Deploy to Web App**
3. Choose your subscription → **newbackend**
4. Confirm deployment

---

## Important Configuration Details

### Required Files in Your Repository

Your repository must contain:

✅ `main.py` - Main FastAPI application
✅ `requirements.txt` - Python dependencies
✅ `startup.txt` - Startup command (backup)
✅ `.deployment` - Azure deployment config
✅ `config.py` - Configuration settings
✅ `utils.py` - Utility functions

### Startup Command Explanation

```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 300
```

- `gunicorn`: Production WSGI server
- `-w 2`: 2 worker processes (suitable for B1 plan: 1.75 GB RAM, 1 vCPU)
- `-k uvicorn.workers.UvicornWorker`: Use Uvicorn worker class for async support
- `main:app`: Module and app variable
- `--bind=0.0.0.0:8000`: Listen on all interfaces, port 8000
- `--timeout 300`: 5-minute timeout for long PDF processing tasks

### Worker Count Recommendations

| App Service Plan | vCPU | RAM | Recommended Workers |
|------------------|------|-----|---------------------|
| B1 (Your plan)   | 1    | 1.75 GB | 2 |
| B2               | 2    | 3.5 GB  | 4 |
| B3               | 4    | 7 GB    | 4 |
| S1               | 1    | 1.75 GB | 2 |
| S2               | 2    | 3.5 GB  | 4 |
| P1v2             | 1    | 3.5 GB  | 2-4 |

Formula: `Workers = (2 × vCPU) + 1` but not exceeding available RAM.

---

## Environment Variables Reference

Create a `.env` file locally (DO NOT commit to Git):

```env
API_TITLE=PDF Tools API
API_VERSION=0.1.0
API_DESCRIPTION=High-performance PDF processing API

HOST=0.0.0.0
PORT=8000
WORKERS=2

CORS_ORIGINS=*
MAX_FILE_SIZE_MB=100
MAX_FILES_PER_REQUEST=50

TEMP_DIR=/tmp/pdf_temp
CLEANUP_TEMP_FILES=true

DEFAULT_DPI=72
DEFAULT_IMAGE_QUALITY=40
DEFAULT_COLOR_MODE=no-change

ASYNC_PROCESSING=true
PROCESS_TIMEOUT_SECONDS=300
```

In Azure, set these via **Configuration** → **Application settings**.

---

## Health Check Configuration (Recommended)

### Step 1: Enable Health Check in Azure

1. Go to **Health check** (under Monitoring)
2. **Enable**: Yes
3. **Path**: `/health`
4. **Interval**: 30 seconds
5. Click **Save**

This ensures Azure automatically restarts your app if it becomes unhealthy.

---

## Monitoring and Troubleshooting

### View Application Logs

#### Option 1: Azure Portal
1. Go to **Log stream** (under Monitoring)
2. See real-time logs

#### Option 2: Azure CLI
```bash
az webapp log tail \
  --resource-group newbakend \
  --name newbackend
```

#### Option 3: Download Logs
```bash
az webapp log download \
  --resource-group newbakend \
  --name newbackend \
  --log-file logs.zip
```

### Enable Application Insights (Recommended)

1. In Azure Portal, go to **Application Insights** (under Monitoring)
2. Click **Turn on Application Insights**
3. **Create new resource** or use existing
4. Click **Apply**

This provides:
- Performance monitoring
- Request tracking
- Error logging
- Dependency tracking

### Common Issues and Solutions

#### Issue 1: "Application Error"

**Solution**: Check logs for specific errors
```bash
az webapp log tail --resource-group newbakend --name newbackend
```

#### Issue 2: "502 Bad Gateway"

**Causes**:
- App not listening on correct port
- Startup command incorrect
- Python dependencies not installed

**Solution**:
1. Verify `WEBSITES_PORT=8000` is set
2. Check startup command is correct
3. Ensure `requirements.txt` is complete

#### Issue 3: "Module not found" errors

**Solution**: Rebuild the app
```bash
az webapp deployment source sync \
  --resource-group newbakend \
  --name newbackend
```

#### Issue 4: Slow cold starts

**Solution**: Keep app always on (requires Basic or higher plan)
```bash
az webapp config set \
  --resource-group newbakend \
  --name newbackend \
  --always-on true
```

#### Issue 5: Out of Memory

**Causes**:
- Too many workers
- Large file processing
- Memory leaks

**Solutions**:
1. Reduce workers to 1-2
2. Limit `MAX_FILE_SIZE_MB`
3. Scale up to B2 or B3 plan

#### Issue 6: Timeout errors

**Solution**: Increase timeout in startup command
```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 600
```

---

## Custom Domain and HTTPS

### Add Custom Domain

1. Go to **Custom domains** in Azure Portal
2. Click **Add custom domain**
3. Enter your domain (e.g., `api.yourdomain.com`)
4. Follow DNS configuration instructions
5. Click **Validate** and **Add**

### Enable HTTPS with Free Managed Certificate

1. After adding custom domain, go to **TLS/SSL settings**
2. Click **Private Key Certificates (.pfx)**
3. Click **Create App Service Managed Certificate**
4. Select your custom domain
5. Click **Create**
6. Go to **Bindings** → **Add TLS/SSL Binding**
7. Select your domain and the managed certificate
8. **TLS/SSL Type**: SNI SSL
9. Click **Add Binding**

### Force HTTPS Only

```bash
az webapp update \
  --resource-group newbakend \
  --name newbackend \
  --https-only true
```

---

## Scaling and Performance

### Manual Scaling (Scale Up - Vertical)

Upgrade your plan for more resources:
```bash
# Scale up to B2 (2 vCPU, 3.5 GB RAM)
az appservice plan update \
  --resource-group newbakend \
  --name ASP-newbakend-bb36 \
  --sku B2
```

### Manual Scaling (Scale Out - Horizontal)

Add more instances:
```bash
# Scale out to 2 instances
az appservice plan update \
  --resource-group newbakend \
  --name ASP-newbakend-bb36 \
  --number-of-workers 2
```

### Auto-Scaling (Requires Standard S1 or higher)

```bash
# Upgrade to Standard plan first
az appservice plan update \
  --resource-group newbakend \
  --name ASP-newbakend-bb36 \
  --sku S1

# Enable autoscale
az monitor autoscale create \
  --resource-group newbakend \
  --resource newbackend \
  --resource-type Microsoft.Web/sites \
  --name autoscale-cpu \
  --min-count 1 \
  --max-count 5 \
  --count 1

# Add scale-out rule (CPU > 70%)
az monitor autoscale rule create \
  --resource-group newbakend \
  --autoscale-name autoscale-cpu \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1

# Add scale-in rule (CPU < 30%)
az monitor autoscale rule create \
  --resource-group newbakend \
  --autoscale-name autoscale-cpu \
  --condition "Percentage CPU < 30 avg 5m" \
  --scale in 1
```

---

## CI/CD with GitHub Actions (Advanced)

If Azure didn't auto-create the workflow, manually create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure App Service

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'newbackend'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
        package: .
```

To get the publish profile:
1. In Azure Portal, go to your Web App
2. Click **Get publish profile** (top toolbar)
3. Copy the XML content
4. In GitHub: Settings → Secrets → Actions → New repository secret
5. Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
6. Paste the XML content

---

## Security Best Practices

### 1. Update CORS Settings

In production, change `CORS_ORIGINS` from `*` to your actual frontend domain:
```bash
az webapp config appsettings set \
  --resource-group newbakend \
  --name newbackend \
  --settings CORS_ORIGINS="https://yourdomain.com"
```

### 2. Enable Azure AD Authentication (Optional)

1. Go to **Authentication** in Azure Portal
2. Click **Add identity provider**
3. Choose **Microsoft**
4. Configure and save

### 3. Use Azure Key Vault for Secrets

Store sensitive data in Key Vault:
```bash
# Create Key Vault
az keyvault create \
  --name pdftools-vault \
  --resource-group newbakend \
  --location germanywestcentral

# Add secret
az keyvault secret set \
  --vault-name pdftools-vault \
  --name ApiKey \
  --value "your-secret-key"

# Grant app access
az webapp identity assign \
  --resource-group newbakend \
  --name newbackend

# Get app's identity
IDENTITY=$(az webapp identity show \
  --resource-group newbakend \
  --name newbackend \
  --query principalId -o tsv)

# Grant access
az keyvault set-policy \
  --name pdftools-vault \
  --object-id $IDENTITY \
  --secret-permissions get list
```

Reference in app settings:
```bash
az webapp config appsettings set \
  --resource-group newbakend \
  --name newbackend \
  --settings API_KEY="@Microsoft.KeyVault(SecretUri=https://pdftools-vault.vault.azure.net/secrets/ApiKey/)"
```

---

## Cost Optimization

### Current Costs (B1 Plan)
- **B1 Plan**: ~$13.14/month (in Germany West Central)

### Tips to Reduce Costs

1. **Use Free Tier for Development**:
   ```bash
   az appservice plan update \
     --resource-group newbakend \
     --name ASP-newbakend-bb36 \
     --sku F1  # Free tier
   ```
   Note: Free tier has limitations (60 CPU minutes/day, no custom domains, no always-on)

2. **Stop app when not in use**:
   ```bash
   az webapp stop --resource-group newbakend --name newbackend
   ```

3. **Delete when done testing**:
   ```bash
   az webapp delete --resource-group newbakend --name newbackend
   ```

4. **Monitor usage**:
   - Go to **Cost Management + Billing** in Azure Portal
   - Set up budget alerts

---

## Testing Your Deployment

### 1. Health Check
```bash
curl https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1700000000,
  "version": "0.1.0",
  "temp_dir_writable": true,
  "temp_dir_path": "/tmp/pdf_temp"
}
```

### 2. API Documentation
Open in browser:
```
https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/docs
```

### 3. Test Image to PDF Conversion

Using curl:
```bash
curl -X POST \
  https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/api/image-to-pdf \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  -o output.pdf
```

### 4. Load Testing (Optional)

Using Apache Bench:
```bash
ab -n 100 -c 10 https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net/health
```

---

## Quick Reference Commands

### Start/Stop App
```bash
# Stop
az webapp stop --resource-group newbakend --name newbackend

# Start
az webapp start --resource-group newbakend --name newbackend

# Restart
az webapp restart --resource-group newbakend --name newbackend
```

### View Configuration
```bash
# List all app settings
az webapp config appsettings list \
  --resource-group newbakend \
  --name newbackend

# Show general config
az webapp config show \
  --resource-group newbakend \
  --name newbackend
```

### Deployment
```bash
# Trigger redeployment
az webapp deployment source sync \
  --resource-group newbakend \
  --name newbackend

# List deployments
az webapp deployment list \
  --resource-group newbakend \
  --name newbackend
```

---

## Support and Resources

- **Azure Documentation**: https://docs.microsoft.com/azure/app-service/
- **Azure Status**: https://status.azure.com/
- **Pricing Calculator**: https://azure.microsoft.com/pricing/calculator/
- **Azure Support**: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade

---

## Next Steps

1. ✅ Deploy your application using one of the methods above
2. ✅ Test all API endpoints
3. ✅ Enable health checks
4. ✅ Set up Application Insights
5. ✅ Configure custom domain (if needed)
6. ✅ Enable HTTPS
7. ✅ Set up CI/CD with GitHub Actions
8. ✅ Monitor and optimize

---

## Summary

Your PDF Tools API is now ready for Azure App Service Code deployment. Choose the deployment method that works best for you:

- **Quick & Automated**: Method 1 (GitHub Actions)
- **Command Line**: Method 4 (Azure CLI)
- **Visual Interface**: Method 3 (Azure Portal)
- **Development**: Method 5 (VS Code)

Your app will be available at:
**https://newbackend-e6hrb7fsgye6dkgz.germanywestcentral-01.azurewebsites.net**

Good luck with your deployment! 🚀
