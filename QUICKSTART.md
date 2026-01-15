# Quick Start Guide

Get the Contextual Agentic AI Assistant running in 5 minutes.

## For Evaluators (harisankar@sentellent.com)

### Option 1: Test Live Deployment (Recommended)

If the application is already deployed:

1. Visit the live URL (provided in submission)
2. Click "Sign in with Google"
3. Use your email: `harisankar@sentellent.com`
4. Start chatting with the AI assistant!

### Option 2: Run Locally with Docker

**Prerequisites**: Docker and Docker Compose installed

```bash
# 1. Clone the repository
git clone <repository-url>
cd contextual-agentic-assistant

# 2. Create environment file
cp backend/.env.example backend/.env

# 3. Add credentials to backend/.env
# (Google OAuth and Google Gemini API key - provided separately)

# 4. Start the application
docker-compose up --build

# 5. Visit http://localhost:3000
```

## For Developers

### Local Development Setup

```bash
# 1. Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# 2. Configure credentials
# Edit backend/.env with:
# - GOOGLE_CLIENT_ID (from Google Cloud Console)
# - GOOGLE_CLIENT_SECRET (from Google Cloud Console)
# - GOOGLE_API_KEY (from Google AI Studio)

# 3. Start services
docker-compose up --build

# 4. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials
3. Add redirect URI: `http://localhost:8000/api/auth/callback`
4. **Add test user**: `harisankar@sentellent.com`
5. Copy Client ID and Secret to `.env`

### AWS Deployment

```bash
# 1. Configure Terraform variables
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit with your credentials

# 2. Deploy infrastructure
cd terraform
terraform init
terraform apply

# 3. Configure GitHub secrets
# Add AWS credentials and app secrets

# 4. Push to trigger CI/CD
git push origin main
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## Testing the Application

### 1. Authentication
- Click "Sign in with Google"
- Authorize the application
- You should be redirected to the chat interface

### 2. Chat Functionality
Try these prompts:
- "Hello, who are you?"
- "What can you help me with?"
- "Tell me about your capabilities"

### 3. Health Check
```bash
curl http://localhost:8000/api/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-15T12:00:00.000000",
  "service": "Contextual Agentic AI Assistant"
}
```

## Project Structure

```
.
├── backend/              # Python FastAPI backend
│   ├── main.py          # Application entry point
│   ├── auth.py          # OAuth authentication
│   ├── chat.py          # Chat endpoints
│   ├── agent.py         # LangGraph agent
│   ├── database.py      # Database models
│   └── requirements.txt # Python dependencies
│
├── frontend/            # React/Next.js frontend
│   ├── pages/          # Next.js pages
│   ├── components/     # React components
│   └── lib/            # Utilities
│
├── terraform/          # Infrastructure as Code
│   ├── main.tf        # AWS resources
│   ├── variables.tf   # Input variables
│   └── outputs.tf     # Output values
│
├── .github/
│   └── workflows/
│       └── deploy.yml  # CI/CD pipeline
│
├── docker-compose.yml  # Local development
├── README.md          # Project overview
├── DEPLOYMENT.md      # Deployment guide
└── PROJECT_STATUS.md  # Current status
```

## Key Features

### ✅ Implemented (Phase 1)
- Google OAuth 2.0 authentication
- Real-time chat interface
- LangGraph-based AI agent
- PostgreSQL database with migrations
- Docker containerization
- Complete Terraform AWS infrastructure
- GitHub Actions CI/CD pipeline

### 🔄 In Progress (Phase 2 & 3)
- Gmail integration
- Calendar integration
- Dynamic memory learning
- Email drafting

## Troubleshooting

### Docker Issues
```bash
# Clean rebuild
docker-compose down -v
docker-compose up --build
```

### Database Connection
```bash
# Check database is running
docker-compose ps

# View logs
docker-compose logs db
```

### OAuth Errors
- Verify redirect URI matches exactly
- Check test user is added in Google Console
- Ensure credentials are correct in `.env`

### Port Conflicts
```bash
# Change ports in docker-compose.yml if needed
# Default: 3000 (frontend), 8000 (backend), 5432 (database)
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/assistant
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Monitoring

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Database
```bash
# Connect to database
docker-compose exec db psql -U postgres -d assistant

# List tables
\dt

# View users
SELECT * FROM users;
```

## Performance

- **Backend**: FastAPI with async support
- **Frontend**: Next.js with SSR
- **Database**: PostgreSQL with connection pooling
- **Caching**: CloudFront CDN for static assets

## Security

- OAuth 2.0 for authentication
- Token encryption at rest
- HTTPS in production
- Secrets Manager for credentials
- Security groups for network isolation
- Rate limiting (configured)

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Review documentation: README.md, DEPLOYMENT.md
3. Check GitHub Issues
4. Review CloudWatch logs (production)

## Next Steps

1. **Test locally** with Docker Compose
2. **Deploy to AWS** using Terraform
3. **Configure CI/CD** with GitHub Actions
4. **Add test user** in Google Cloud Console
5. **Submit** with screenshots and live URL

---

**Quick Links**:
- [Full Documentation](README.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Project Status](PROJECT_STATUS.md)
- [Submission Form](https://forms.gle/VVd9r4kemkWoiQVQ8)

---

*Built for the Sentellent Hiring Challenge*
