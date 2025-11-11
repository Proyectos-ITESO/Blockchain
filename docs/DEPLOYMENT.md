# Deployment Guide

## Production Deployment Checklist

### 1. Environment Configuration

Create a production `.env` file with secure values:

```bash
# Database - Use managed PostgreSQL service
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT - Generate a strong secret key
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Blockchain - Use production RPC and deployed contract
BLOCKCHAIN_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
CONTRACT_ADDRESS=0x...
BLOCKCHAIN_PRIVATE_KEY=0x...

# CORS - Restrict to your frontend domain
CORS_ORIGINS=["https://yourdomain.com"]
```

### 2. Database Setup

**Using managed PostgreSQL (recommended):**
- Supabase
- Neon
- AWS RDS
- DigitalOcean Managed Database

**Initialize database:**
```bash
# Run migrations
python init_db.py

# Or use Alembic
alembic upgrade head
```

### 3. Smart Contract Deployment

**Deploy to Mainnet/Production Testnet:**
```bash
cd contracts
npm install

# Deploy to Sepolia testnet
npx hardhat run scripts/deploy.js --network sepolia

# Save the contract address to .env
# CONTRACT_ADDRESS=0x...
```

**Verify contract on Etherscan:**
```bash
npx hardhat verify --network sepolia CONTRACT_ADDRESS
```

### 4. Backend Deployment

#### Option A: Render

1. Create new Web Service
2. Connect GitHub repository
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env`

#### Option B: Railway

1. Create new project
2. Deploy from GitHub
3. Add PostgreSQL service
4. Configure environment variables

#### Option C: DigitalOcean App Platform

1. Create new app from GitHub
2. Add managed PostgreSQL database
3. Configure environment variables
4. Deploy

#### Option D: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Deploy with Docker:**
```bash
# Build
docker build -t encrypted-messaging-api .

# Run
docker run -d -p 8000:8000 --env-file .env encrypted-messaging-api
```

### 5. Frontend Deployment (Week 4)

**Recommended platforms:**
- Vercel (recommended for React)
- Netlify
- Cloudflare Pages

**Environment variables for frontend:**
```
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_WS_URL=wss://api.yourdomain.com/ws
```

### 6. Security Hardening

**Backend:**
- [ ] Use HTTPS/TLS certificates (Let's Encrypt)
- [ ] Enable CORS only for your frontend domain
- [ ] Implement rate limiting (e.g., slowapi)
- [ ] Add request validation and sanitization
- [ ] Use environment variables for all secrets
- [ ] Enable SQL injection protection (SQLAlchemy handles this)
- [ ] Add logging and monitoring

**Database:**
- [ ] Use strong passwords
- [ ] Restrict database access to backend IP only
- [ ] Enable SSL connections
- [ ] Regular backups
- [ ] Monitor for suspicious activity

**Blockchain:**
- [ ] Store private key in secure vault (AWS Secrets Manager, HashiCorp Vault)
- [ ] Use separate wallet for production
- [ ] Monitor gas prices and transaction failures
- [ ] Implement retry logic for failed transactions

### 7. Monitoring

**Backend Monitoring:**
- Health check endpoint: `/health`
- Logging: Configure structured logging (JSON)
- Error tracking: Sentry, Rollbar
- Uptime monitoring: UptimeRobot, Pingdom

**Blockchain Monitoring:**
- Transaction confirmations
- Gas prices
- Failed notarizations
- Contract events

### 8. Backup Strategy

**Database:**
- Automated daily backups
- Point-in-time recovery
- Test restore procedures

**Configuration:**
- Version control for all config files
- Document environment variables
- Backup private keys securely

### 9. CI/CD Pipeline

**GitHub Actions example:**

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          # Trigger deploy
```

### 10. Performance Optimization

- [ ] Enable database connection pooling
- [ ] Implement caching (Redis) for frequently accessed data
- [ ] Use CDN for static assets
- [ ] Compress responses (gzip)
- [ ] Optimize database queries (indexes)
- [ ] WebSocket connection limits

### 11. Scaling Considerations

**Horizontal Scaling:**
- Load balancer (Nginx, Cloudflare)
- Multiple backend instances
- Sticky sessions for WebSocket connections

**Database Scaling:**
- Read replicas
- Connection pooling
- Query optimization

**Blockchain:**
- Multiple RPC endpoints (failover)
- Transaction queue management
- Gas price optimization

### 12. Cost Estimates

**Monthly costs (estimated):**
- Backend hosting: $7-25 (Render, Railway)
- Database: $15-25 (managed PostgreSQL)
- Frontend hosting: $0 (Vercel free tier)
- Blockchain RPC: $0-50 (Infura, Alchemy free tier)
- Gas fees: Variable (depends on usage)

**Total: ~$25-100/month for MVP**

### 13. Post-Deployment

- [ ] Test all endpoints in production
- [ ] Verify WebSocket connections
- [ ] Test blockchain integration
- [ ] Run end-to-end tests
- [ ] Monitor logs for errors
- [ ] Set up alerts for critical issues

### 14. Rollback Plan

- [ ] Keep previous version available
- [ ] Database migration rollback scripts
- [ ] Document rollback procedures
- [ ] Test rollback in staging

---

## Production URLs Structure

```
Frontend:  https://app.yourdomain.com
Backend:   https://api.yourdomain.com
WebSocket: wss://api.yourdomain.com/ws
Docs:      https://api.yourdomain.com/docs
```

---

## Support & Maintenance

- Regular security updates
- Monitor blockchain gas prices
- Database maintenance windows
- User support channels
- Incident response procedures
