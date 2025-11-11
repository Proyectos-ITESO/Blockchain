# Quick Start Guide

Get the encrypted messaging system running in 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Git

## Step 1: Clone & Setup

```bash
# Clone repository
git clone <repository-url>
cd Blockchain

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

## Step 2: Database Setup

```bash
# Create PostgreSQL database
createdb encrypted_chat

# Or using psql
psql -U postgres -c "CREATE DATABASE encrypted_chat;"
```

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
# At minimum, set:
# - DATABASE_URL (PostgreSQL connection string)
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - BLOCKCHAIN_RPC_URL (get free from Infura or Alchemy)
```

## Step 4: Initialize Database

```bash
# Create database tables
python init_db.py
```

## Step 5: Deploy Smart Contract (Optional)

```bash
# Install Hardhat dependencies
cd contracts
npm install

# Deploy to testnet (requires funded wallet)
npx hardhat run scripts/deploy.js --network sepolia

# Copy contract address to .env
# CONTRACT_ADDRESS=0x...
```

## Step 6: Start Backend

```bash
# Return to project root
cd ..

# Run development server
./run_dev.sh

# Or manually:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

## Step 7: Setup Frontend

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Step 8: Test the System

1. **Register Account**
   - Navigate to http://localhost:3000/register
   - Create a username and password
   - Keys are generated automatically

2. **Create Second Account**
   - Open incognito window
   - Register another user

3. **Add Contact**
   - In first account, click "+" icon
   - Search for second user
   - Click "Add"

4. **Send Message**
   - Select contact from list
   - Type message and send
   - Message is encrypted end-to-end
   - Hash is registered on blockchain (if configured)

5. **Verify Message**
   - Click shield icon on message
   - Check blockchain verification status

## Troubleshooting

### Backend won't start

```bash
# Check database connection
psql -U postgres -d encrypted_chat -c "SELECT 1;"

# Check if port 8000 is available
lsof -i :8000

# Check logs
tail -f app.log
```

### Frontend won't connect

```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify .env configuration
cat frontend/.env

# Check browser console for errors
```

### Database errors

```bash
# Drop and recreate database
dropdb encrypted_chat
createdb encrypted_chat
python init_db.py
```

### WebSocket not connecting

- Ensure backend is running on correct port
- Check CORS settings in backend
- Verify WebSocket URL in frontend .env

## Production Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for full production setup.

Quick options:
- **Backend**: Render, Railway, DigitalOcean
- **Frontend**: Vercel, Netlify, Cloudflare Pages
- **Database**: Supabase, Neon, AWS RDS

## Next Steps

- Deploy smart contract to mainnet
- Configure production environment variables
- Set up monitoring and logging
- Implement key backup/restore UI
- Add group chat functionality
- Implement file sharing

## Support

- Documentation: [README.md](README.md)
- API Docs: [docs/API.md](docs/API.md)
- Deployment: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- Issues: GitHub Issues

## Security Notes

⚠️ **Important**:
- Never commit `.env` file
- Keep private keys secure
- Use strong passwords
- Backup encryption keys
- Use HTTPS in production
- Enable rate limiting
- Monitor for suspicious activity

Enjoy secure messaging! 🔐
