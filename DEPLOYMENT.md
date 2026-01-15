# Deployment Guide

This guide will help you deploy the Contextual Agentic AI Assistant to AWS.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Terraform** installed (v1.0+)
4. **Docker** installed
5. **Google Cloud Console** project with OAuth credentials
6. **Google Gemini API Key**

## Step 1: Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable APIs:
   - Gmail API
   - Google Calendar API
   - Google+ API
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8000/api/auth/callback` (for local testing)
     - `https://your-alb-url/api/auth/callback` (will get this after deployment)
5. **CRITICAL**: Add `harisankar@sentellent.com` as a test user:
   - Go to "OAuth consent screen"
   - Scroll to "Test users"
   - Click "Add Users"
   - Add: `harisankar@sentellent.com`
6. Copy your Client ID and Client Secret

## Step 2: Prepare Environment Variables

1. Copy the example file:
```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

2. Edit `terraform/terraform.tfvars` with your values:
```hcl
google_client_id     = "your-google-client-id"
google_client_secret = "your-google-client-secret"
google_api_key       = "AIza-your-gemini-api-key"
secret_key           = "generate-a-random-32-character-string"
db_password          = "your-secure-database-password"
```

## Step 3: Create S3 Bucket for Terraform State

```bash
aws s3 mb s3://agentic-assistant-terraform-state --region us-east-1
aws s3api put-bucket-versioning \
  --bucket agentic-assistant-terraform-state \
  --versioning-configuration Status=Enabled
```

## Step 4: Deploy Infrastructure with Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the infrastructure
terraform apply

# Save the outputs
terraform output > ../outputs.txt
```

This will create:
- VPC with public/private subnets
- RDS PostgreSQL database
- ECS Fargate cluster
- ECR repositories
- Application Load Balancer
- CloudFront distribution
- Security groups and IAM roles

## Step 5: Build and Push Docker Images

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd backend
docker build -t agentic-assistant-backend .
docker tag agentic-assistant-backend:latest <ecr-backend-url>:latest
docker push <ecr-backend-url>:latest

# Build and push frontend
cd ../frontend
docker build -t agentic-assistant-frontend .
docker tag agentic-assistant-frontend:latest <ecr-frontend-url>:latest
docker push <ecr-frontend-url>:latest
```

## Step 6: Run Database Migrations

```bash
# Connect to ECS task or run locally with RDS endpoint
cd backend
export DATABASE_URL="postgresql://postgres:your-password@your-rds-endpoint:5432/assistant"
alembic upgrade head
```

## Step 7: Update Google OAuth Redirect URI

1. Get your ALB URL from Terraform outputs
2. Go back to Google Cloud Console
3. Add the production redirect URI:
   - `https://your-alb-url/api/auth/callback`

## Step 8: Setup GitHub Actions CI/CD

1. Go to your GitHub repository settings
2. Navigate to "Secrets and variables" > "Actions"
3. Add the following secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_API_KEY`
   - `SECRET_KEY`

4. Push to main branch to trigger deployment:
```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

## Step 9: Verify Deployment

1. Check ECS service status:
```bash
aws ecs describe-services \
  --cluster agentic-assistant-cluster \
  --services agentic-assistant-backend-service
```

2. Check CloudWatch logs:
```bash
aws logs tail /ecs/agentic-assistant-backend --follow
```

3. Test the application:
   - Frontend: `https://your-cloudfront-url`
   - Backend health: `http://your-alb-url/api/health`

## Step 10: Take Screenshots for Submission

1. **AWS Console Screenshots**:
   - ECS Cluster showing running services
   - RDS Database instance
   - CloudFront distribution
   - ECR repositories with images

2. **CI/CD Pipeline Screenshots**:
   - GitHub Actions workflow run (successful)
   - All jobs passing (test, build-and-push, deploy)

## Troubleshooting

### ECS Task Won't Start
- Check CloudWatch logs for errors
- Verify secrets in Secrets Manager
- Check security group rules

### Database Connection Issues
- Verify RDS security group allows ECS tasks
- Check DATABASE_URL format
- Ensure database is in same VPC

### OAuth Errors
- Verify redirect URI matches exactly
- Check test user is added
- Ensure client ID/secret are correct

### Frontend Not Loading
- Check CloudFront distribution status
- Verify S3 bucket permissions
- Check browser console for errors

## Monitoring

- **CloudWatch Logs**: `/ecs/agentic-assistant-backend`
- **ECS Service Metrics**: CPU, Memory, Task count
- **RDS Metrics**: Connections, CPU, Storage
- **ALB Metrics**: Request count, Response time

## Scaling

To scale the application:

```bash
aws ecs update-service \
  --cluster agentic-assistant-cluster \
  --service agentic-assistant-backend-service \
  --desired-count 2
```

## Cost Optimization

- Use t3.micro for RDS (free tier eligible)
- Use Fargate Spot for non-production
- Enable S3 lifecycle policies
- Set CloudWatch log retention to 7 days

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

**Note**: This will delete everything including the database!

## Support

For issues:
1. Check CloudWatch logs
2. Review ECS task definitions
3. Verify environment variables
4. Check security group rules

---

**Submission Checklist**:
- [ ] GitHub repository with code
- [ ] Live application URL
- [ ] AWS Console screenshots
- [ ] CI/CD pipeline screenshots
- [ ] Test user configured: harisankar@sentellent.com
