# Azure App Service Deployment

Deploy your PDF Tools API to Azure App Service with managed SSL.

## Prerequisites
- Azure CLI installed
- Azure subscription
- Docker image on Docker Hub: `habibhassan123/pdfwandler-backend:latest`

## Deployment Steps

### 1. Login to Azure
```bash
az login
```

### 2. Create Resource Group
```bash
az group create --name pdf-tools-rg --location eastus
```

### 3. Create App Service Plan
```bash
az appservice plan create \
  --name pdf-tools-plan \
  --resource-group pdf-tools-rg \
  --is-linux \
  --sku B1
```

**SKU Options:**
- `B1` - Basic ($13/month) - Good for testing
- `B2` - Basic ($25/month) - Better performance
- `S1` - Standard ($70/month) - Production recommended

### 4. Create Web App
```bash
az webapp create \
  --resource-group pdf-tools-rg \
  --plan pdf-tools-plan \
  --name pdfwandler-api \
  --deployment-container-image-name habibhassan123/pdfwandler-backend:latest
```

**Note:** Replace `pdfwandler-api` with a unique name if taken.

### 5. Configure App Settings
```bash
az webapp config appsettings set \
  --resource-group pdf-tools-rg \
  --name pdfwandler-api \
  --settings \
    WEBSITES_PORT=8000 \
    CORS_ORIGINS=* \
    MAX_FILE_SIZE_MB=100 \
    WORKERS=4
```

### 6. Enable HTTPS Only
```bash
az webapp update \
  --resource-group pdf-tools-rg \
  --name pdfwandler-api \
  --https-only true
```

## Access Your API

Your API will be available at:
```
https://pdfwandler-api.azurewebsites.net
```

Test it:
```bash
curl https://pdfwandler-api.azurewebsites.net/health
```

## Update Your Image

When you push a new image to Docker Hub:

```bash
az webapp restart --resource-group pdf-tools-rg --name pdfwandler-api
```

Or enable continuous deployment:
```bash
az webapp deployment container config \
  --resource-group pdf-tools-rg \
  --name pdfwandler-api \
  --enable-cd true
```

## Add Custom Domain (Optional)

### 1. Map Domain
```bash
az webapp config hostname add \
  --webapp-name pdfwandler-api \
  --resource-group pdf-tools-rg \
  --hostname api.yourdomain.com
```

### 2. Enable Managed SSL
```bash
az webapp config ssl create \
  --resource-group pdf-tools-rg \
  --name pdfwandler-api \
  --hostname api.yourdomain.com
```

## Monitoring

### View Logs
```bash
az webapp log tail --resource-group pdf-tools-rg --name pdfwandler-api
```

### Enable Application Insights
```bash
az monitor app-insights component create \
  --app pdf-tools-insights \
  --location eastus \
  --resource-group pdf-tools-rg

INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app pdf-tools-insights \
  --resource-group pdf-tools-rg \
  --query instrumentationKey -o tsv)

az webapp config appsettings set \
  --resource-group pdf-tools-rg \
  --name pdfwandler-api \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

## Scaling

### Manual Scale
```bash
az appservice plan update \
  --resource-group pdf-tools-rg \
  --name pdf-tools-plan \
  --number-of-workers 3
```

### Auto-scale
```bash
az monitor autoscale create \
  --resource-group pdf-tools-rg \
  --resource pdfwandler-api \
  --resource-type Microsoft.Web/sites \
  --name autoscale-cpu \
  --min-count 1 \
  --max-count 5 \
  --count 1

az monitor autoscale rule create \
  --resource-group pdf-tools-rg \
  --autoscale-name autoscale-cpu \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1
```

## Cleanup (Delete Everything)

```bash
az group delete --name pdf-tools-rg --yes --no-wait
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
az webapp log tail --resource-group pdf-tools-rg --name pdfwandler-api

# Verify image exists
docker pull habibhassan123/pdfwandler-backend:latest
```

### 502 Bad Gateway
- Check `WEBSITES_PORT=8000` is set correctly
- Verify container exposes port 8000
- Check logs for startup errors

### High Response Times
- Upgrade to higher SKU (B2 or S1)
- Enable auto-scaling
- Check Application Insights for bottlenecks

## Cost Estimate

- **B1 Plan**: ~$13/month
- **B2 Plan**: ~$25/month
- **S1 Plan**: ~$70/month
- **Application Insights**: Free tier available

## Next Steps

1. Set up CI/CD with GitHub Actions
2. Configure custom domain
3. Set up monitoring alerts
4. Implement rate limiting
5. Add authentication if needed
