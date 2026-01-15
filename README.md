# Contextual Agentic AI Assistant

A cloud-hosted Personal Agentic AI Assistant that acts as a "Chief of Staff" - integrating with Google Workspace (Gmail and Calendar) to help manage your day with dynamic memory and contextual intelligence.

## 🎯 Project Overview

This application is built for the Sentellent Hiring Challenge and demonstrates:
- **Cloud-Native Architecture**: Fully containerized deployment on AWS
- **Dynamic Memory System**: Learns from both explicit user instructions and implicit data extraction
- **Google Workspace Integration**: Seamless Gmail and Calendar access
- **LangGraph Agent**: Stateful, multi-step conversational AI
- **Infrastructure as Code**: Complete Terraform setup for AWS
- **CI/CD Pipeline**: Automated deployment with GitHub Actions

## 🏗️ Architecture

### Tech Stack
- **Frontend**: React.js with Next.js and TypeScript
- **Backend**: Python with FastAPI
- **AI Framework**: LangChain / LangGraph with OpenAI GPT-4
- **Database**: PostgreSQL (AWS RDS) with pgvector for embeddings
- **Cloud**: AWS (ECS Fargate, RDS, CloudFront, API Gateway)
- **DevOps**: Docker, Terraform, GitHub Actions

### Key Features
1. **Authentication**: Google OAuth 2.0 for secure login
2. **Conversational Agent**: Natural language chat interface
3. **Gmail Integration**: Read emails, extract information, draft responses
4. **Calendar Integration**: View events, check availability
5. **Dynamic Memory**: 
   - Learns preferences from chat ("I hate 9 AM meetings")
   - Extracts context from emails ("Project X is delayed")
   - Applies learned context to all actions
6. **Security**: Token encryption, HTTPS, rate limiting, CORS

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- AWS Account (for deployment)
- Google Cloud Console project (for OAuth)
- OpenAI API key

## 📚 Documentation

**New to this project? Start here:**
- 🎯 **[START_HERE.md](START_HERE.md)** - Your complete guide to all documentation
- 📖 **[STEP_BY_STEP_GUIDE.md](STEP_BY_STEP_GUIDE.md)** - Complete walkthrough (4-6 hours)
- ⚡ **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Essential commands
- 🔧 **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- ☁️ **[DEPLOYMENT.md](DEPLOYMENT.md)** - AWS deployment guide
- ✅ **[SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)** - Pre-submission checklist
- 📊 **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Current status and completion

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd contextual-agentic-assistant
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Environment Variables**
Create `backend/.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/assistant
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key_for_encryption
FRONTEND_URL=http://localhost:3000
```

4. **Run Database Migrations**
```bash
cd backend
alembic upgrade head
```

5. **Start Backend**
```bash
uvicorn main:app --reload --port 8000
```

6. **Frontend Setup**
```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

7. **Start Frontend**
```bash
npm run dev
```

Visit `http://localhost:3000`

### Docker Development

```bash
docker-compose up --build
```

## 🔧 Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API and Calendar API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:8000/api/auth/callback` (local)
   - `https://your-domain.com/api/auth/callback` (production)
6. **IMPORTANT**: Add `harisankar@sentellent.com` as a test user
7. Copy Client ID and Client Secret to your `.env` file

## ☁️ AWS Deployment

### Prerequisites
- AWS CLI configured with credentials
- Terraform installed

### Deploy Infrastructure

1. **Configure Terraform Variables**
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

2. **Initialize Terraform**
```bash
terraform init
```

3. **Plan Deployment**
```bash
terraform plan
```

4. **Apply Infrastructure**
```bash
terraform apply
```

5. **Configure GitHub Secrets**
Add these secrets to your GitHub repository:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `OPENAI_API_KEY`
- `SECRET_KEY`

6. **Push to Main Branch**
```bash
git push origin main
```

The CI/CD pipeline will automatically build, test, and deploy.

## 📁 Project Structure

```
.
├── backend/                 # Python FastAPI backend
│   ├── main.py             # FastAPI application entry
│   ├── auth.py             # OAuth authentication
│   ├── chat.py             # Chat endpoints
│   ├── agent.py            # LangGraph agent
│   ├── memory.py           # Memory system
│   ├── google_integration.py  # Gmail/Calendar APIs
│   ├── database.py         # Database models
│   ├── config.py           # Configuration
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend container
│   └── tests/              # Backend tests
├── frontend/               # React/Next.js frontend
│   ├── pages/              # Next.js pages
│   ├── components/         # React components
│   ├── lib/                # Utilities
│   ├── package.json        # Node dependencies
│   └── Dockerfile          # Frontend container
├── terraform/              # Infrastructure as Code
│   ├── main.tf             # Main Terraform config
│   ├── modules/            # Terraform modules
│   └── variables.tf        # Input variables
├── .github/
│   └── workflows/
│       └── deploy.yml      # CI/CD pipeline
├── docker-compose.yml      # Local development
└── README.md               # This file
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Property-Based Tests
```bash
cd backend
pytest tests/ -v -m property
```

## 📊 Monitoring

- **Health Check**: `GET /api/health`
- **AWS CloudWatch**: Metrics and logs
- **Application Logs**: Structured JSON logging

## 🔒 Security Features

- OAuth 2.0 authentication
- Token encryption at rest
- HTTPS/TLS everywhere
- Rate limiting
- CORS configuration
- Input validation
- Security event logging

## 📝 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎓 Development Phases

### Phase 1: Foundation (Submission Ready)
- ✅ Project setup
- ✅ Backend core with FastAPI
- ✅ Database setup with PostgreSQL
- ✅ Google OAuth authentication
- ✅ Basic LangGraph agent
- ✅ Chat API endpoints
- ✅ Frontend with Next.js
- ✅ Docker configuration
- ✅ Terraform infrastructure
- ✅ CI/CD pipeline

### Phase 2: Google Workspace Integration
- ✅ MCP server setup
- ✅ Gmail integration
- ✅ Calendar integration
- ✅ Email drafting

### Phase 3: Dynamic Memory System
- ✅ Memory storage and retrieval
- ✅ Chat-based learning
- ✅ Data-based extraction
- ✅ Memory application to actions

## 🤝 Contributing

This is a hiring challenge submission. For questions, contact the repository owner.

## 📄 License

This project is created for the Sentellent Hiring Challenge.

## 🙏 Acknowledgments

- Sentellent for the challenge opportunity
- LangChain/LangGraph for the agent framework
- OpenAI for GPT-4 API
- Google for Workspace APIs

## 📞 Support

For issues or questions:
1. Check the troubleshooting guide in `/docs/troubleshooting.md`
2. Review AWS CloudWatch logs
3. Check GitHub Actions workflow runs

## 🎯 Submission Checklist

- [x] GitHub repository with code
- [x] Live application URL
- [x] AWS Console screenshots
- [x] CI/CD pipeline screenshots
- [x] Test user configured: harisankar@sentellent.com
- [x] Documentation complete

---

**Built with ❤️ for the Sentellent Hiring Challenge**
\ n # #   D e p l o y e d ! 
 
 #   P i p e l i n e   T e s t 
 
 

## Trigger Pipeline Test (Public)



# Final trigger test after re-enabling Actions
