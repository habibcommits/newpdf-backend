# Azure Container Instances Deployment

Deploy your PDF Tools API to Azure Container Instances - the simplest and cheapest option.

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

### 3. Deploy Container Instance
```bash
az container create \
  --resource-group pdf-tools-rg \
  --name pdf-tools-api \
  --image habibhassan123/pdfwandler-backend:latest \
  --cpu 2 \
  --memory 4 \
  --dns-name-label pdfwandler-api-unique123 \
  --ports 8000 \
  --environment-variables \
    CORS_ORIGINS=* \
    MAX_FILE_SIZE_MB=100 \
    WORKERS=4
```

**Important:** Replace `pdfwandler-api-unique123` with a unique DNS label.

## Access Your API

Your API will be available at:
```
http://pdfwandler-api-unique123.eastus.azurecontainer.io:8000
```

Get the FQDN:
```bash
az container show \
  --resource-group pdf-tools-rg \
  --name pdf-tools-api \
  --query ipAddress.fqdn -o tsv
```

Test it:
```bash
curl http://pdfwandler-api-unique123.eastus.azurecontainer.io:8000/health
```

## Add HTTPS with Application Gateway

Container Instances don't support HTTPS directly. You need Application Gateway.

### 1. Create Virtual Network
```bash
az network vnet create \
  --resource-group pdf-tools-rg \
  --name pdf-vnet \
  --address-prefix 10.0.0.0/16 \
  --subnet-name appgw-subnet \
  --subnet-prefix 10.0.1.0/24
```

### 2. Create Public IP
```bash
az network public-ip create \
  --resource-group pdf-tools-rg \
  --name appgw-pip \
  --sku Standard \
  --dns-name pdfwandler-gw
```

### 3. Get Container IP
```bash
CONTAINER_IP=$(az container show \
  --resource-group pdf-tools-rg \
  --name pdf-tools-api \
  --query ipAddress.ip -o tsv)
```

### 4. Create Application Gateway
```bash
az network application-gateway create \
  --resource-group pdf-tools-rg \
  --name pdf-tools-appgw \
  --location eastus \
  --vnet-name pdf-vnet \
  --subnet appgw-subnet \
  --public-ip-address appgw-pip \
  --http-settings-port 8000 \
  --http-settings-protocol Http \
  --frontend-port 443 \
  --sku Standard_v2 \
  --capacity 1 \
  --servers $CONTAINER_IP
```

### 5. Add SSL Certificate
```bash
az network application-gateway ssl-cert create \
  --resource-group pdf-tools-rg \
  --gateway-name pdf-tools-appgw \
  --name ssl-cert \
  --cert-file /path/to/cert.pfx \
  --cert-password yourpassword
```

## Monitoring

### View Container Logs
```bash
az container logs --resource-group pdf-tools-rg --name pdf-tools-api
```

### Follow Logs in Real-time
```bash
az container logs --resource-group pdf-tools-rg --name pdf-tools-api --follow
```

### Check Container Status
```bash
az container show \
  --resource-group pdf-tools-rg \
  --name pdf-tools-api \
  --query instanceView.state
```

## Update Container

To deploy a new version:

### 1. Delete Old Container
```bash
az container delete \
  --resource-group pdf-tools-rg \
  --name pdf-tools-api \
  --yes
```

### 2. Create New Container
```bash
az container create \
  --resource-group pdf-tools-rg \
  --name pdf-tools-api \
  --image habibhassan123/pdfwandler-backend:latest \
  --cpu 2 \
  --memory 4 \
  --dns-name-label pdfwandler-api-unique123 \
  --ports 8000 \
  --environment-variables \
    CORS_ORIGINS=* \
    MAX_FILE_SIZE_MB=100 \
    WORKERS=4
```

## Resource Configuration

### CPU and Memory Options
- `--cpu 1 --memory 1.5` - Minimal (~$36/month)
- `--cpu 2 --memory 4` - Recommended (~$73/month)
- `--cpu 4 --memory 8` - High performance (~$146/month)

### Restart Policy
```bash
az container create \
  ... \
  --restart-policy OnFailure
```

Options: `Always`, `OnFailure`, `Never`

## Cleanup (Delete Everything)

```bash
az group delete --name pdf-tools-rg --yes --no-wait
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
az container logs --resource-group pdf-tools-rg --name pdf-tools-api

# Check events
az container show \
  --resource-group pdf-tools-rg \
  --name pdf-tools-api \
  --query instanceView.events
```

### Can't Access API
- Verify port 8000 is exposed: `--ports 8000`
- Check firewall/network rules
- Verify DNS name is unique

### Out of Memory
```bash
# Increase memory
az container delete --resource-group pdf-tools-rg --name pdf-tools-api --yes
az container create ... --memory 8
```

## Limitations

- **No Auto-scaling** - Manual scaling only
- **No HTTPS** - Requires Application Gateway
- **Single Instance** - No built-in redundancy
- **Restarts** - Container restarts on crashes

## When to Use ACI vs App Service

**Use Container Instances if:**
- Simple deployment needs
- Low to medium traffic
- Cost-sensitive
- Don't need auto-scaling

**Use App Service if:**
- Production workload
- Need auto-scaling
- Need built-in HTTPS
- Need zero-downtime deployments

## Cost Estimate

**Container Instances:**
- 2 vCPU, 4 GB RAM: ~$73/month
- Pay only when running

**Application Gateway (for HTTPS):**
- Standard_v2: ~$175/month + data processing

**Total with HTTPS**: ~$250/month

## Alternative: Use App Service Instead

For built-in HTTPS and better management, consider App Service:
```bash
# See AZURE_APP_SERVICE.md for full guide
```

App Service B1 plan is cheaper ($13/month) and includes HTTPS.
