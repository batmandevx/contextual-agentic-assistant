# Quick Reference Card

Essential commands for development and deployment.

---

## 🚀 Local Development

### Start Application
```bash
docker-compose up --build
```

### Stop Application
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Restart Services
```bash
docker-compose restart
```

### Clean Rebuild
```bash
docker-compose down -v
docker-compose up --build
```

### Access Database
```bash
docker-compose exec db psql -U postgres -d assistant
```

---

## ☁️ AWS Deployment

### Terraform Commands
```bash
cd terraform

# Initialize
terraform init

# Plan (preview changes)
terraform plan

# Apply (create resources)
terraform apply

# Destroy (delete everything)
terraform destroy

# Show outputs
terraform output
```

### ECR Login
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com
```

### Build and Push Images
```bash
# Backend
cd backend
docker build -t agentic-assistant-backend .
docker tag agentic-assistant-backend:latest \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/agentic-assistant-backend:latest
docker push \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/agentic-assistant-backend:latest

# Frontend
cd frontend
docker build -t agentic-assistant-frontend .
docker tag agentic-assistant-frontend:latest \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/agentic-assistant-frontend:latest
docker push \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/agentic-assistant-frontend:latest
```

### ECS Commands
```bash
# List clusters
aws ecs list-clusters

# Describe service
aws ecs describe-services \
  --cluster agentic-assistant-cluster \
  --services agentic-assistant-backend-service

# Update service (force new deployment)
aws ecs update-service \
  --cluster agentic-assistant-cluster \
  --service agentic-assistant-backend-service \
  --force-new-deployment

# Wait for service to stabilize
aws ecs wait services-stable \
  --cluster agentic-assistant-cluster \
  --services agentic-assistant-backend-service

# List tasks
aws ecs list-tasks \
  --cluster agentic-assistant-cluster \
  --service-name agentic-assistant-backend-service
```

### RDS Commands
```bash
# List databases
aws rds describe-db-instances

# Get endpoint
aws rds describe-db-instances \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text

# Get status
aws rds describe-db-instances \
  --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus]'
```

### CloudWatch Logs
```bash
# Tail logs
aws logs tail /ecs/agentic-assistant-backend --follow

# Get log streams
aws logs describe-log-streams \
  --log-group-name /ecs/agentic-assistant-backend

# Get specific log events
aws logs get-log-events \
  --log-group-name /ecs/agentic-assistant-backend \
  --log-stream-name <stream-name>
```

---

## 🔍 Monitoring & Debugging

### Check Application Health
```bash
# Local
curl http://localhost:8000/api/health

# Production
curl http://YOUR_ALB_URL/api/health
```

### Check AWS Resources
```bash
# Get account ID
aws sts get-caller-identity

# List all ECS clusters
aws ecs list-clusters

# List all RDS instances
aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus]'

# List all ECR repositories
aws ecr describe-repositories

# List all load balancers
aws elbv2 describe-load-balancers

# List all CloudFront distributions
aws cloudfront list-distributions
```

### Get Application URLs
```bash
# ALB URL
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[?contains(LoadBalancerName, `agentic`)].DNSName' \
  --output text

# CloudFront URL
aws cloudfront list-distributions \
  --query 'DistributionList.Items[0].DomainName' \
  --output text

# RDS Endpoint
aws rds describe-db-instances \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

---

## 🗄️ Database Operations

### Run Migrations
```bash
cd backend
alembic upgrade head
```

### Create New Migration
```bash
cd backend
alembic revision --autogenerate -m "description"
```

### Rollback Migration
```bash
cd backend
alembic downgrade -1
```

### Connect to Database
```bash
# Local
docker-compose exec db psql -U postgres -d assistant

# Production (requires bastion or VPN)
psql -h YOUR_RDS_ENDPOINT -U postgres -d assistant
```

### Common SQL Queries
```sql
-- List all tables
\dt

-- View users
SELECT * FROM users;

-- View conversations
SELECT * FROM conversations;

-- View messages
SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;

-- View memory entries
SELECT * FROM memory_entries;

-- Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM messages;
```

---

## 🔐 Secrets Management

### AWS Secrets Manager
```bash
# Get secret value
aws secretsmanager get-secret-value \
  --secret-id agentic-assistant-secrets \
  --query SecretString \
  --output text

# Update secret
aws secretsmanager update-secret \
  --secret-id agentic-assistant-secrets \
  --secret-string '{"KEY":"VALUE"}'
```

---

## 🔄 CI/CD

### Trigger Deployment
```bash
# Make a change and push
git add .
git commit -m "Update"
git push origin main
```

### View Workflow Status
```bash
# Using GitHub CLI (if installed)
gh run list
gh run view
gh run watch
```

### Manual Workflow Trigger
- Go to: GitHub → Actions → Deploy to AWS → Run workflow

---

## 🧹 Cleanup

### Stop Local Services
```bash
docker-compose down -v
```

### Delete AWS Resources
```bash
cd terraform
terraform destroy
```

### Delete S3 Terraform State
```bash
aws s3 rb s3://agentic-assistant-terraform-state-YOUR-ID --force
```

### Delete ECR Images
```bash
# Delete all images in backend repo
aws ecr batch-delete-image \
  --repository-name agentic-assistant-backend \
  --image-ids "$(aws ecr list-images --repository-name agentic-assistant-backend --query 'imageIds[*]' --output json)"

# Delete all images in frontend repo
aws ecr batch-delete-image \
  --repository-name agentic-assistant-frontend \
  --image-ids "$(aws ecr list-images --repository-name agentic-assistant-frontend --query 'imageIds[*]' --output json)"
```

---

## 📊 Cost Monitoring

### Check Current Costs
```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

### Estimate Monthly Costs
- ECS Fargate: ~$15-30/month (1 task, 0.5 vCPU, 1GB RAM)
- RDS t3.micro: ~$15/month (free tier eligible for 12 months)
- ALB: ~$20/month
- CloudFront: ~$1-5/month (low traffic)
- **Total**: ~$50-70/month (after free tier)

---

## 🆘 Emergency Commands

### Stop All AWS Services (Save Money)
```bash
# Stop ECS service
aws ecs update-service \
  --cluster agentic-assistant-cluster \
  --service agentic-assistant-backend-service \
  --desired-count 0

# Stop RDS database
aws rds stop-db-instance \
  --db-instance-identifier agentic-assistant-db
```

### Start Services Again
```bash
# Start ECS service
aws ecs update-service \
  --cluster agentic-assistant-cluster \
  --service agentic-assistant-backend-service \
  --desired-count 1

# Start RDS database
aws rds start-db-instance \
  --db-instance-identifier agentic-assistant-db
```

---

## 📱 Important URLs

### Local Development
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

### Production
- Frontend: https://YOUR_CLOUDFRONT_URL
- Backend API: http://YOUR_ALB_URL
- Health Check: http://YOUR_ALB_URL/api/health

### External Services
- Google Cloud Console: https://console.cloud.google.com/
- Google AI Studio: https://aistudio.google.com/
- AWS Console: https://console.aws.amazon.com/
- GitHub: https://github.com/
- Submission Form: https://forms.gle/VVd9r4kemkWoiQVQ8

---

## 🔑 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback
GOOGLE_API_KEY=AIza-xxx
SECRET_KEY=xxx
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📞 Support Resources

- **Documentation**: README.md, DEPLOYMENT.md
- **Step-by-Step Guide**: STEP_BY_STEP_GUIDE.md
- **Project Status**: PROJECT_STATUS.md
- **Submission Checklist**: SUBMISSION_CHECKLIST.md

---

*Keep this reference handy during development!*
