# Mini ERPNext - Docker Deployment Guide

## Prerequisites

- Docker Desktop installed
- Docker Compose v2.0+

## Quick Start

### Option 1: Web API Only (Headless)

```bash
cd docker
docker-compose up api
```

Access API at: http://localhost:5000

### Option 2: Full Stack with GUI (Linux/Mac)

```bash
# Allow X11 connections
xhost +local:docker

cd docker
docker-compose up
```

### Option 3: Windows with VcXsrv

1. Install VcXsrv
2. Start VcXsrv with "Disable access control" checked
3. Set DISPLAY environment variable:
   ```powershell
   $env:DISPLAY = "host.docker.internal:0.0"
   ```
4. Run:
   ```bash
   cd docker
   docker-compose up app
   ```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Health check |
| GET | /api/{doctype} | List documents |
| GET | /api/{doctype}/{name} | Get document |
| POST | /api/{doctype} | Create document |
| PUT | /api/{doctype}/{name} | Update document |
| DELETE | /api/{doctype}/{name} | Delete document |
| POST | /api/{doctype}/{name}/submit | Submit document |
| POST | /api/{doctype}/{name}/cancel | Cancel document |

### Example: Create a Customer

```bash
curl -X POST http://localhost:5000/api/customer \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Acme Corp", "email_id": "sales@acme.com"}'
```

### Example: Create a Sales Order

```bash
curl -X POST http://localhost:5000/api/sales-order \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "CUST-001",
    "items": [{"item_code": "ITEM-001", "qty": 10, "rate": 100}]
  }'
```

### Example: Submit a Sales Order

```bash
curl -X POST http://localhost:5000/api/sales-order/SO-001/submit
```

## Volumes

| Container Path | Host Path | Purpose |
|----------------|-----------|---------|
| /app/*.db | ./*.db | SQLite databases |
| /app/logs | ./logs | Log files |
| /app/data | ./data | Data files |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DISPLAY | :0 | X11 display for GUI |
| FLASK_ENV | production | Flask environment |

## Stopping Containers

```bash
cd docker
docker-compose down
```

## Rebuilding After Code Changes

```bash
cd docker
docker-compose build --no-cache
docker-compose up
```
