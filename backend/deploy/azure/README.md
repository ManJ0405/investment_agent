# Azure Demo Deployment Checklist

Use this path for a low-cost production-like demo on Azure.

## 1) Core resources

- Azure Container Registry (ACR)
- Azure Container Apps (or App Service for Containers)
- Log Analytics workspace
- Key Vault for secrets

## 2) Build and push image

```bash
az acr login --name <acr_name>
docker build -t <acr_name>.azurecr.io/investment-agent:latest .
docker push <acr_name>.azurecr.io/investment-agent:latest
```

## 3) Deploy container app

Configure:

- Image: `<acr_name>.azurecr.io/investment-agent:latest`
- Port: `8000`
- Health probe path: `/healthz`
- Min replicas: `1` for stable demo
- Max replicas: `2`

## 4) Runtime env vars

Set these in Container App / App Service settings:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- any LLM/model provider keys if you switch from local Ollama

Store secret values in Key Vault and reference from app settings.

## 5) Production baseline

- Enable request logs + application logs
- Add alerts for:
  - p95 latency
  - 5xx error rate
  - container restart count
- Add budget alert for subscription spend
- Keep at least one smoke test hitting `/healthz` and one trend endpoint call

