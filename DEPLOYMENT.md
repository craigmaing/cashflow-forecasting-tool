# Cash Flow Forecasting Tool - Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker Desktop installed
- Git installed
- 8GB+ RAM recommended

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/craigmaing/cashflow-forecasting-tool.git
cd cashflow-forecasting-tool
```

2. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

### Services Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React/Next)  │───▶│   (FastAPI)     │───▶│  (TimescaleDB)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │     Cache       │
                       │    (Redis)      │
                       │   Port: 6379    │
                       └─────────────────┘
```

## Manual Setup (Without Docker)

### Backend Setup

1. **Python Environment**
```bash
cd development/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Database Setup**
```bash
# Install PostgreSQL with TimescaleDB extension
# Create database and run schema.sql
```

3. **Start Backend**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Node.js Environment**
```bash
cd development/frontend
npm install
```

2. **Start Frontend**
```bash
npm run dev
```

## Production Deployment

### AWS Deployment (Recommended)

1. **Infrastructure Setup**
- RDS PostgreSQL with TimescaleDB
- ElastiCache Redis
- ECS Fargate for containers
- Application Load Balancer
- Route 53 for DNS

2. **Environment Variables**
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/cashflow_db
REDIS_URL=redis://elasticache-endpoint:6379/0
SECRET_KEY=your-production-secret-key
```

3. **Deployment Commands**
```bash
# Build images
docker build -t cashflow-backend ./development/backend
docker build -t cashflow-frontend ./development/frontend

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ECR_URI
docker tag cashflow-backend:latest ECR_URI/cashflow-backend:latest
docker push ECR_URI/cashflow-backend:latest
```

### Azure Deployment

1. **Azure Container Instances**
```bash
az container create \
  --resource-group cashflow-rg \
  --name cashflow-backend \
  --image cashflow-backend:latest \
  --ports 8000
```

### Google Cloud Deployment

1. **Cloud Run**
```bash
gcloud run deploy cashflow-backend \
  --image gcr.io/PROJECT_ID/cashflow-backend \
  --platform managed \
  --region us-central1
```

## Monitoring & Maintenance

### Health Checks
- Backend: `GET /health`
- Database: Connection pool monitoring
- Redis: Memory usage monitoring

### Logging
- Application logs: Structured JSON logging
- Access logs: Nginx/Load balancer logs
- Error tracking: Sentry integration

### Backup Strategy
- Database: Daily automated backups
- File storage: S3 cross-region replication
- Configuration: Infrastructure as Code (Terraform)

### Scaling Considerations
- Horizontal scaling: Load balancer + multiple instances
- Database scaling: Read replicas for reporting
- Cache scaling: Redis cluster mode
- CDN: CloudFront for static assets

## Security Checklist

- [ ] HTTPS enforced in production
- [ ] Database credentials in secrets manager
- [ ] API rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers implemented
- [ ] Regular security updates
- [ ] Backup encryption enabled
- [ ] Access logging configured

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
```bash
docker-compose logs postgres
# Check connection string and credentials
```

2. **Frontend Build Errors**
```bash
cd development/frontend
npm run build
# Check for TypeScript errors
```

3. **API Timeout Issues**
```bash
# Check backend logs
docker-compose logs backend
# Verify database performance
```

### Performance Optimization

1. **Database Optimization**
- Index optimization
- Query performance monitoring
- Connection pool tuning

2. **API Optimization**
- Response caching
- Database query optimization
- Background job processing

3. **Frontend Optimization**
- Code splitting
- Image optimization
- CDN implementation

## Support

For deployment issues:
1. Check logs: `docker-compose logs [service]`
2. Verify environment variables
3. Review GitHub Issues
4. Contact support team
