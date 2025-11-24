# Azure Deployment Guide with SSL/HTTPS

This guide provides step-by-step instructions for deploying the PDF Tools API to Azure with SSL/HTTPS enabled.

## Deployment Options

You have three main options for deploying to Azure:

1. **Azure Container Instances (ACI)** - Simplest, good for low-to-medium traffic
2. **Azure App Service** - Managed platform with built-in SSL, best for production
3. **Azure Kubernetes Service (AKS)** - Scalable, complex, best for enterprise

## Option 1: Azure Container Instances (Recommended for Getting Started)

### Prerequisites
- Azure CLI installed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
- Docker installed locally
- Azure subscription

### Step 1: Login to Azure
```bash
az login
```

### Step 2: Create a Resource Group
```bash
az group create --name pdf-tools-rg --location eastus
```

### Step 3: Create Azure Container Registry (ACR)
```bash
# Create registry
az acr create --resource-group pdf-tools-rg \
  --name pdftools<uniqueid> \
  --sku Basic

# Login to ACR
az acr login --name pdftools<uniqueid>
```

### Step 4: Build and Push Docker Image
```bash
# Tag your image
docker tag pdf-tools-api pdftools<uniqueid>.azurecr.io/pdf-tools-api:latest

# Push to ACR
docker push pdftools<uniqueid>.azurecr.io/pdf-tools-api:latest
```

### Step 5: Deploy to Azure Container Instances
```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name pdftools<uniqueid> --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name pdftools<uniqueid> --query "passwords[0].value" -o tsv)

# Deploy container
az container create \
  --resource-group pdf-tools-rg \
  --name pdf-tools-api \
  --image pdftools<uniqueid>.azurecr.io/pdf-tools-api:latest \
  --cpu 2 \
  --memory 4 \
  --registry-login-server pdftools<uniqueid>.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --dns-name-label pdf-tools-api-<uniqueid> \
  --ports 8000 \
  --environment-variables \
    CORS_ORIGINS=https://yourfrontend.com \
    MAX_FILE_SIZE_MB=100 \
    WORKERS=4
```

### Step 6: Get the Public IP
```bash
az container show --resource-group pdf-tools-rg \
  --name pdf-tools-api \
  --query ipAddress.fqdn -o tsv
```

Your API will be available at: `http://pdf-tools-api-<uniqueid>.eastus.azurecontainer.io:8000`

### Step 7: Add SSL/HTTPS with Azure Application Gateway

For production HTTPS, add an Application Gateway:

```bash
# Create virtual network
az network vnet create \
  --resource-group pdf-tools-rg \
  --name pdf-vnet \
  --address-prefix 10.0.0.0/16 \
  --subnet-name appgw-subnet \
  --subnet-prefix 10.0.1.0/24

# Create public IP
az network public-ip create \
  --resource-group pdf-tools-rg \
  --name appgw-pip \
  --sku Standard \
  --dns-name pdf-tools-gw

# Create Application Gateway with SSL
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
  --capacity 2 \
  --servers <your-container-ip>
```

Then add your SSL certificate:
```bash
az network application-gateway ssl-cert create \
  --resource-group pdf-tools-rg \
  --gateway-name pdf-tools-appgw \
  --name ssl-cert \
  --cert-file /path/to/cert.pfx \
  --cert-password <password>
```

## Option 2: Azure App Service (Recommended for Production)

### Step 1: Create App Service Plan
```bash
az appservice plan create \
  --name pdf-tools-plan \
  --resource-group pdf-tools-rg \
  --is-linux \
  --sku B2
```

### Step 2: Create Web App
```bash
az webapp create \
  --resource-group pdf-tools-rg \
  --plan pdf-tools-plan \
  --name pdf-tools-api-<uniqueid> \
  --deployment-container-image-name pdftools<uniqueid>.azurecr.io/pdf-tools-api:latest
```

### Step 3: Configure Container Registry
```bash
az webapp config container set \
  --name pdf-tools-api-<uniqueid> \
  --resource-group pdf-tools-rg \
  --docker-custom-image-name pdftools<uniqueid>.azurecr.io/pdf-tools-api:latest \
  --docker-registry-server-url https://pdftools<uniqueid>.azurecr.io \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD
```

### Step 4: Configure Environment Variables
```bash
az webapp config appsettings set \
  --resource-group pdf-tools-rg \
  --name pdf-tools-api-<uniqueid> \
  --settings \
    CORS_ORIGINS=https://yourfrontend.com \
    MAX_FILE_SIZE_MB=100 \
    WORKERS=4 \
    WEBSITES_PORT=8000
```

### Step 5: Enable HTTPS (Managed Certificate)
```bash
# Map custom domain (optional but recommended)
az webapp config hostname add \
  --webapp-name pdf-tools-api-<uniqueid> \
  --resource-group pdf-tools-rg \
  --hostname api.yourdomain.com

# Enable HTTPS with managed certificate
az webapp config ssl create \
  --resource-group pdf-tools-rg \
  --name pdf-tools-api-<uniqueid> \
  --hostname api.yourdomain.com
```

### Step 6: Force HTTPS
```bash
az webapp update \
  --resource-group pdf-tools-rg \
  --name pdf-tools-api-<uniqueid> \
  --https-only true
```

Your API will be available at: `https://pdf-tools-api-<uniqueid>.azurewebsites.net`

## Option 3: Azure Kubernetes Service (For Enterprise Scale)

### Step 1: Create AKS Cluster
```bash
az aks create \
  --resource-group pdf-tools-rg \
  --name pdf-tools-aks \
  --node-count 2 \
  --enable-managed-identity \
  --attach-acr pdftools<uniqueid>
```

### Step 2: Get AKS Credentials
```bash
az aks get-credentials \
  --resource-group pdf-tools-rg \
  --name pdf-tools-aks
```

### Step 3: Create Kubernetes Deployment

Create `k8s-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pdf-tools-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pdf-tools-api
  template:
    metadata:
      labels:
        app: pdf-tools-api
    spec:
      containers:
      - name: pdf-tools-api
        image: pdftools<uniqueid>.azurecr.io/pdf-tools-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: CORS_ORIGINS
          value: "https://yourfrontend.com"
        - name: WORKERS
          value: "4"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
---
apiVersion: v1
kind: Service
metadata:
  name: pdf-tools-service
spec:
  type: LoadBalancer
  selector:
    app: pdf-tools-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

### Step 4: Deploy to Kubernetes
```bash
kubectl apply -f k8s-deployment.yaml
```

### Step 5: Install NGINX Ingress Controller with SSL
```bash
# Install ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Install cert-manager for SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

Create `ingress.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pdf-tools-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: pdf-tools-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: pdf-tools-service
            port:
              number: 80
```

Apply ingress:
```bash
kubectl apply -f ingress.yaml
```

## SSL Certificate Options

### 1. Azure Managed Certificate (Easiest)
- Automatically provisioned and renewed
- Available for App Service and Application Gateway
- Free
- Requires custom domain

### 2. Let's Encrypt (Free)
- Use cert-manager for Kubernetes
- Use certbot for other services
- Auto-renewal
- Requires domain validation

### 3. Commercial SSL Certificate
- Purchase from CA (DigiCert, Sectigo, etc.)
- Upload to Azure Key Vault
- Reference in Application Gateway or App Service

## Monitoring and Logging

### Enable Application Insights
```bash
# Create Application Insights
az monitor app-insights component create \
  --app pdf-tools-insights \
  --location eastus \
  --resource-group pdf-tools-rg

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app pdf-tools-insights \
  --resource-group pdf-tools-rg \
  --query instrumentationKey -o tsv)

# Add to app settings
az webapp config appsettings set \
  --resource-group pdf-tools-rg \
  --name pdf-tools-api-<uniqueid> \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

## Performance Tuning for Azure

### 1. Scaling
```bash
# Auto-scale based on CPU
az monitor autoscale create \
  --resource-group pdf-tools-rg \
  --resource pdf-tools-api-<uniqueid> \
  --resource-type Microsoft.Web/sites \
  --name autoscale-cpu \
  --min-count 2 \
  --max-count 10 \
  --count 2

az monitor autoscale rule create \
  --resource-group pdf-tools-rg \
  --autoscale-name autoscale-cpu \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 2
```

### 2. CDN for Static Assets (if needed)
```bash
az cdn profile create \
  --resource-group pdf-tools-rg \
  --name pdf-tools-cdn \
  --sku Standard_Microsoft
```

## Security Best Practices

1. **Use Managed Identity**: Avoid storing credentials
2. **Enable HTTPS Only**: Force SSL/TLS
3. **Configure CORS**: Restrict to your frontend domain
4. **Use Azure Key Vault**: Store secrets securely
5. **Enable Azure DDoS Protection**: For production
6. **Set up Azure Firewall**: Control inbound/outbound traffic
7. **Regular Updates**: Keep containers updated

## Cost Optimization

- **Use Reserved Instances**: Save up to 72%
- **Right-size your resources**: Monitor and adjust
- **Use auto-scaling**: Scale down during low traffic
- **Clean up unused resources**: Delete test deployments

## Troubleshooting

### View Container Logs
```bash
# ACI
az container logs --resource-group pdf-tools-rg --name pdf-tools-api

# App Service
az webapp log tail --resource-group pdf-tools-rg --name pdf-tools-api-<uniqueid>

# AKS
kubectl logs -l app=pdf-tools-api
```

### Common Issues

1. **Container won't start**: Check logs, verify image exists
2. **502 Bad Gateway**: Container port mismatch, check WEBSITES_PORT
3. **High latency**: Increase CPU/memory, enable auto-scaling
4. **Out of memory**: Increase container memory limit

## Next Steps

1. Set up CI/CD with GitHub Actions or Azure DevOps
2. Configure monitoring and alerts
3. Set up backup and disaster recovery
4. Implement rate limiting
5. Add authentication if needed

## Support

For Azure-specific issues, consult:
- Azure Documentation: https://docs.microsoft.com/azure
- Azure Support: https://azure.microsoft.com/support
