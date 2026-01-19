# Docker Configuration - Phase 4

Docker Compose configurations for running Evolution Todo locally.

## Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Local development |
| `docker-compose.prod.yml` | Production-like setup |
| `.env.example` | Environment template |

## Quick Start

```bash
# Copy environment file
cp .env.example .env

# Edit with your values
nano .env

# Start services (development)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Development Mode

```bash
# Build and start
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
```

## Production Mode

```bash
# Use production config
docker-compose -f docker-compose.prod.yml up -d

# With specific tag
TAG=v1.0.0 docker-compose -f docker-compose.prod.yml up -d
```

## Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Backend readiness (with DB)
curl http://localhost:8000/ready

# Frontend
curl http://localhost:3000
```

## Troubleshooting

### Backend won't start
1. Check DATABASE_URL is correct
2. Ensure Neon database is accessible
3. Check logs: `docker-compose logs backend`

### Frontend can't reach backend
1. Ensure backend is healthy first
2. Check NEXT_PUBLIC_API_URL
3. Verify network connectivity: `docker network inspect phase-4_todo-network`

### Build failures
```bash
# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```
