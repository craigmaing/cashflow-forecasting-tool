# Environment Configuration Guide

## Quick Start

1. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your specific values, especially:
   - `SECRET_KEY`: Generate a secure 32+ character key for production
   - Database credentials if different from defaults
   - External API keys if using integrations

3. For Docker development:
   ```bash
   docker-compose up -d
   ```

## Configuration Files

### `.env.example`
Template for environment variables. Never commit actual `.env` files to version control.

### `docker-compose.yml`
Main Docker Compose configuration for development environment.

### `docker-compose.override.yml.example`
Optional overrides for local development. Copy to `docker-compose.override.yml` for custom local settings.

## Environment Variables

### Required Variables
- `SECRET_KEY`: JWT signing key (min 32 chars)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

### Security Variables
- `JWT_ALGORITHM`: Algorithm for JWT tokens (default: HS256)
- `JWT_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `CORS_ORIGINS`: Allowed CORS origins
- `ALLOWED_HOSTS`: Allowed host headers

### Performance Variables
- `DATABASE_POOL_SIZE`: Database connection pool size
- `DATABASE_MAX_OVERFLOW`: Maximum overflow connections
- `CACHE_TTL`: Cache time-to-live in seconds
- `RATE_LIMIT_REQUESTS`: Request limit per window
- `RATE_LIMIT_WINDOW`: Rate limit window in seconds

## Docker Services

### PostgreSQL (TimescaleDB)
- Port: 5432
- Database: cashflow_db
- User: cashflow_user
- Password: cashflow_password

### Redis
- Port: 6379
- Database: 0

### Backend (FastAPI)
- Port: 8000
- Auto-reload enabled in development

### Frontend (Next.js)
- Port: 3000
- Connected to backend at http://localhost:8000

## Security Considerations

1. **Never use default secrets in production**
2. **Use environment-specific .env files**
3. **Keep .env files out of version control**
4. **Rotate secrets regularly**
5. **Use strong passwords for databases**

## Troubleshooting

### Container Issues
- Check logs: `docker-compose logs <service>`
- Restart services: `docker-compose restart <service>`
- Rebuild: `docker-compose build --no-cache`

### Database Connection Issues
- Verify PostgreSQL is running: `docker-compose ps postgres`
- Check connection string format
- Ensure database migrations are run

### Network Issues
- Backend should use `postgres` and `redis` as hostnames within Docker
- Frontend uses `localhost` for external access
- Check CORS settings if frontend can't connect
