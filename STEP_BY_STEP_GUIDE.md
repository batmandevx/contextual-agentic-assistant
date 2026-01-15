# Complete Step-by-Step Development Guide

This guide will walk you through every step from setup to submission.

---

## 📋 Phase 0: Prerequisites Setup (30 minutes)

### Step 1: Install Required Software

#### On Windows:
```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install tools
choco install git docker-desktop python nodejs terraform awscli -y

# Restart your terminal after installation
```

#### On Mac:
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install tools
brew install git docker python node terraform awscli
```

#### On Linux:
```bash
# Update package manager
sudo apt update

# Install tools
sudo apt install git docker.io docker-compose python3 python3-pip nodejs npm -y

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Step 2: Verify Installations

```bash
# Check all tools are installed
git --version
docker --version
python --version  # Should be 3.11+
node --version    # Should be 18+
terraform --version
aws --version
```

**✅ Checkpoint**: All commands should return version numbers without errors.

---

## 📋 Phase 1: Google Cloud Console Setup (20 minutes)

### Step 3: Create Google Cloud Project

1. **Go to Google Cloud Console**:
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project**:
   - Click "Select a project" dropdown at the top
   - Click "NEW PROJECT"
   - Project name: `agentic-assistant`
   - Click "CREATE"
   - Wait for project creation (30 seconds)

3. **Select Your Project**:
   - Click "Select a project" dropdown
   - Choose `agentic-assistant`

### Step 4: Enable Required APIs

1. **Enable Gmail API**:
   - Go to: https://console.cloud.google.com/apis/library/gmail.googleapis.com
   - Click "ENABLE"
   - Wait for confirmation

2. **Enable Calendar API**:
   - Go to: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com
   - Click "ENABLE"
   - Wait for confirmation

3. **Enable Google+ API** (for user info):
   - Go to: https://console.cloud.google.com/apis/library/plus.googleapis.com
   - Click "ENABLE"
   - Wait for confirmation

### Step 5: Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen**:
   - Navigate to: APIs & Services → OAuth consent screen
   - Or visit: https://console.cloud.google.com/apis/credentials/consent

2. **Choose User Type**:
   - Select "External"
   - Click "CREATE"

3. **Fill App Information**:
   - App name: `Contextual Agentic AI Assistant`
   - User support email: Your email
   - Developer contact: Your email
   - Click "SAVE AND CONTINUE"

4. **Scopes** (Step 2):
   - Click "ADD OR REMOVE SCOPES"
   - Search and add these scopes:
     - `userinfo.email`
     - `userinfo.profile`
     - `gmail.readonly`
     - `gmail.compose`
     - `calendar.readonly`
   - Click "UPDATE"
   - Click "SAVE AND CONTINUE"

5. **Test Users** (Step 3) - **CRITICAL**:
   - Click "ADD USERS"
   - Enter: `harisankar@sentellent.com`
   - Enter your own email for testing
   - Click "ADD"
   - Click "SAVE AND CONTINUE"

6. **Summary** (Step 4):
   - Review information
   - Click "BACK TO DASHBOARD"

### Step 6: Create OAuth Credentials

1. **Go to Credentials**:
   - Navigate to: APIs & Services → Credentials
   - Or visit: https://console.cloud.google.com/apis/credentials

2. **Create OAuth Client ID**:
   - Click "CREATE CREDENTIALS"
   - Select "OAuth client ID"

3. **Configure OAuth Client**:
   - Application type: "Web application"
   - Name: `Agentic Assistant Web Client`
   
4. **Add Authorized Redirect URIs**:
   - Click "ADD URI" under "Authorized redirect URIs"
   - Add: `http://localhost:8000/api/auth/callback`
   - Click "ADD URI" again
   - Add: `http://localhost:8000/api/auth/callback` (we'll add production later)
   - Click "CREATE"

5. **Save Credentials**:
   - A popup will show your Client ID and Client Secret
   - **IMPORTANT**: Copy both and save them securely
   - Click "OK"

**✅ Checkpoint**: You should have:
- Google Client ID (looks like: `xxxxx.apps.googleusercontent.com`)
- Google Client Secret (looks like: `GOCSPX-xxxxx`)
- Test user `harisankar@sentellent.com` added

---

## 📋 Phase 2: Get OpenAI API Key (10 minutes)

### Step 7: Create OpenAI Account and Get API Key

1. **Sign Up for OpenAI**:
   - Visit: https://platform.openai.com/signup
   - Create account or sign in

2. **Add Payment Method**:
   - Go to: https://platform.openai.com/account/billing
   - Add a payment method (required for API access)
   - Add at least $5 credit

3. **Create API Key**:
   - Go to: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Name: `Agentic Assistant`
   - Click "Create secret key"
   - **IMPORTANT**: Copy the key (starts with `sk-`)
   - You won't be able to see it again!

**✅ Checkpoint**: You should have your OpenAI API key saved securely.

---

## 📋 Phase 3: Local Development Setup (30 minutes)

### Step 8: Clone and Setup Project

```bash
# Navigate to your projects directory
cd ~/projects  # or wherever you keep projects

# If you haven't initialized git yet
git init
git add .
git commit -m "Initial commit"

# Create GitHub repository (do this on github.com)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/contextual-agentic-assistant.git
git branch -M main
git push -u origin main
```

### Step 9: Configure Environment Variables

1. **Backend Environment**:
```bash
# Copy example file
cp backend/.env.example backend/.env

# Edit backend/.env with your favorite editor
# On Windows: notepad backend/.env
# On Mac/Linux: nano backend/.env
```

2. **Fill in these values in backend/.env**:
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/assistant

# Paste your Google OAuth credentials
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback

# Paste your OpenAI API key
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Generate a random secret key (or use this command)
# On Mac/Linux: openssl rand -hex 32
# On Windows: Use any random 32+ character string
SECRET_KEY=your-generated-secret-key-here

FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO
DEBUG=False
```

3. **Frontend Environment**:
```bash
# Copy example file
cp frontend/.env.example frontend/.env.local

# Edit frontend/.env.local
# On Windows: notepad frontend/.env.local
# On Mac/Linux: nano frontend/.env.local
```

4. **Fill in frontend/.env.local**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**✅ Checkpoint**: Both `.env` files are configured with your credentials.

### Step 10: Test Local Development

1. **Start Docker Desktop**:
   - Open Docker Desktop application
   - Wait for it to fully start (whale icon should be steady)

2. **Build and Start Services**:
```bash
# From project root directory
docker-compose up --build
```

This will:
- Build backend Docker image
- Build frontend Docker image
- Start PostgreSQL database
- Start all services

**Expected output**:
```
✔ Container contextual-agentic-assistant-db-1       Created
✔ Container contextual-agentic-assistant-backend-1  Created
✔ Container contextual-agentic-assistant-frontend-1 Created
Attaching to backend-1, db-1, frontend-1
```

3. **Wait for Services to Start** (2-3 minutes):
   - Watch the logs
   - Look for: `Application startup complete` (backend)
   - Look for: `ready - started server` (frontend)

4. **Test the Application**:

Open new terminal and run:
```bash
# Test backend health
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","timestamp":"...","service":"Contextual Agentic AI Assistant"}
```

5. **Open in Browser**:
   - Frontend: http://localhost:3000
   - Backend API Docs: http://localhost:8000/docs

6. **Test OAuth Flow**:
   - Click "Sign in with Google"
   - You should be redirected to Google
   - Sign in with your test account
   - Authorize the application
   - You should be redirected back to chat interface

**✅ Checkpoint**: Application runs locally and OAuth works!

---

## 📋 Phase 4: AWS Account Setup (20 minutes)

### Step 11: Create AWS Account

1. **Sign Up for AWS**:
   - Visit: https://aws.amazon.com/
   - Click "Create an AWS Account"
   - Follow the signup process
   - **Note**: You'll need a credit card, but we'll use free tier services

2. **Complete Account Setup**:
   - Verify email
   - Add payment method
   - Verify phone number
   - Choose "Basic Support - Free"

### Step 12: Create IAM User for Deployment

1. **Go to IAM Console**:
   - Visit: https://console.aws.amazon.com/iam/
   - Click "Users" in left sidebar
   - Click "Create user"

2. **User Details**:
   - User name: `terraform-deploy`
   - Click "Next"

3. **Set Permissions**:
   - Select "Attach policies directly"
   - Search and select these policies:
     - `AmazonEC2ContainerRegistryFullAccess`
     - `AmazonECS_FullAccess`
     - `AmazonRDSFullAccess`
     - `AmazonS3FullAccess`
     - `CloudFrontFullAccess`
     - `IAMFullAccess`
     - `AmazonVPCFullAccess`
     - `SecretsManagerReadWrite`
   - Click "Next"
   - Click "Create user"

4. **Create Access Keys**:
   - Click on the user you just created
   - Click "Security credentials" tab
   - Scroll to "Access keys"
   - Click "Create access key"
   - Choose "Command Line Interface (CLI)"
   - Check "I understand..."
   - Click "Next"
   - Description: `Terraform deployment`
   - Click "Create access key"
   - **IMPORTANT**: Copy both:
     - Access key ID
     - Secret access key
   - Click "Done"

### Step 13: Configure AWS CLI

```bash
# Configure AWS CLI
aws configure

# Enter when prompted:
AWS Access Key ID: <paste your access key>
AWS Secret Access Key: <paste your secret key>
Default region name: us-east-1
Default output format: json
```

**Test AWS CLI**:
```bash
# This should list your AWS account info
aws sts get-caller-identity
```

**✅ Checkpoint**: AWS CLI is configured and working.

---

## 📋 Phase 5: Terraform Infrastructure Deployment (45 minutes)

### Step 14: Prepare Terraform Configuration

1. **Create S3 Bucket for Terraform State**:
```bash
# Create bucket (use a unique name)
aws s3 mb s3://agentic-assistant-terraform-state-YOUR-UNIQUE-ID --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket agentic-assistant-terraform-state-YOUR-UNIQUE-ID \
  --versioning-configuration Status=Enabled
```

2. **Update Terraform Backend Configuration**:

Edit `terraform/provider.tf` and update the bucket name:
```hcl
backend "s3" {
  bucket = "agentic-assistant-terraform-state-YOUR-UNIQUE-ID"  # Change this
  key    = "terraform.tfstate"
  region = "us-east-1"
  encrypt = true
}
```

3. **Create Terraform Variables File**:
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

4. **Edit terraform.tfvars**:
```bash
# On Windows: notepad terraform.tfvars
# On Mac/Linux: nano terraform.tfvars
```

Fill in:
```hcl
aws_region  = "us-east-1"
environment = "production"
project_name = "agentic-assistant"

# Paste your Google OAuth credentials
google_client_id     = "your-client-id.apps.googleusercontent.com"
google_client_secret = "GOCSPX-your-secret"

# Paste your OpenAI API key
openai_api_key = "sk-your-key"

# Generate a secure secret key (32+ characters)
secret_key = "your-secure-secret-key-at-least-32-characters"

# Database credentials
db_username = "postgres"
db_password = "ChangeThisToASecurePassword123!"

# Leave empty for now
frontend_domain = ""
```

### Step 15: Initialize and Deploy Terraform

1. **Initialize Terraform**:
```bash
cd terraform
terraform init
```

**Expected output**:
```
Initializing the backend...
Initializing provider plugins...
Terraform has been successfully initialized!
```

2. **Validate Configuration**:
```bash
terraform validate
```

**Expected output**:
```
Success! The configuration is valid.
```

3. **Plan Deployment** (see what will be created):
```bash
terraform plan
```

This will show you all resources that will be created. Review the output.

4. **Apply Infrastructure** (this takes 10-15 minutes):
```bash
terraform apply
```

- Type `yes` when prompted
- Wait for completion
- **IMPORTANT**: Save the outputs!

```bash
# Save outputs to file
terraform output > ../terraform-outputs.txt
```

**✅ Checkpoint**: Terraform has created all AWS resources.

### Step 16: Verify Infrastructure

```bash
# Check ECS cluster
aws ecs list-clusters

# Check RDS database
aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus]'

# Check ECR repositories
aws ecr describe-repositories
```

---

## 📋 Phase 6: Build and Push Docker Images (20 minutes)

### Step 17: Get ECR Repository URLs

```bash
# Get backend repository URL
aws ecr describe-repositories --repository-names agentic-assistant-backend --query 'repositories[0].repositoryUri' --output text

# Get frontend repository URL
aws ecr describe-repositories --repository-names agentic-assistant-frontend --query 'repositories[0].repositoryUri' --output text

# Save these URLs!
```

### Step 18: Login to ECR

```bash
# Get your AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

**Expected output**:
```
Login Succeeded
```

### Step 19: Build and Push Backend Image

```bash
# Navigate to backend directory
cd ../backend

# Build image
docker build -t agentic-assistant-backend .

# Tag image
docker tag agentic-assistant-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/agentic-assistant-backend:latest

# Push image
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/agentic-assistant-backend:latest
```

### Step 20: Build and Push Frontend Image

```bash
# Navigate to frontend directory
cd ../frontend

# Build image
docker build -t agentic-assistant-frontend .

# Tag image
docker tag agentic-assistant-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/agentic-assistant-frontend:latest

# Push image
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/agentic-assistant-frontend:latest
```

**✅ Checkpoint**: Docker images are in ECR.

---

## 📋 Phase 7: Database Migration (10 minutes)

### Step 21: Run Database Migrations

1. **Get RDS Endpoint**:
```bash
aws rds describe-db-instances --query 'DBInstances[0].Endpoint.Address' --output text
```

2. **Update DATABASE_URL** in backend/.env temporarily:
```env
DATABASE_URL=postgresql://postgres:YOUR_DB_PASSWORD@YOUR_RDS_ENDPOINT:5432/assistant
```

3. **Run Migrations**:
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
```

**Expected output**:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial schema
```

**✅ Checkpoint**: Database schema is created.

---

## 📋 Phase 8: Update ECS Service (15 minutes)

### Step 22: Force New Deployment

```bash
# Update backend service
aws ecs update-service \
  --cluster agentic-assistant-cluster \
  --service agentic-assistant-backend-service \
  --force-new-deployment

# Wait for service to stabilize (5-10 minutes)
aws ecs wait services-stable \
  --cluster agentic-assistant-cluster \
  --services agentic-assistant-backend-service
```

### Step 23: Get Application URLs

```bash
# Get ALB URL
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[?contains(LoadBalancerName, `agentic`)].DNSName' \
  --output text

# Get CloudFront URL
aws cloudfront list-distributions \
  --query 'DistributionList.Items[0].DomainName' \
  --output text
```

**Save these URLs!**

---

## 📋 Phase 9: Update Google OAuth Redirect URI (5 minutes)

### Step 24: Add Production Redirect URI

1. **Go to Google Cloud Console**:
   - Visit: https://console.cloud.google.com/apis/credentials

2. **Edit OAuth Client**:
   - Click on your OAuth client
   - Under "Authorized redirect URIs"
   - Click "ADD URI"
   - Add: `http://YOUR_ALB_URL/api/auth/callback`
   - Click "SAVE"

**✅ Checkpoint**: Production OAuth is configured.

---

## 📋 Phase 10: Test Production Deployment (15 minutes)

### Step 25: Test Backend

```bash
# Test health endpoint
curl http://YOUR_ALB_URL/api/health
```

**Expected response**:
```json
{"status":"healthy","timestamp":"...","service":"Contextual Agentic AI Assistant"}
```

### Step 26: Test Frontend

1. **Open CloudFront URL** in browser:
   - Visit: `https://YOUR_CLOUDFRONT_URL`

2. **Test OAuth Flow**:
   - Click "Sign in with Google"
   - Sign in with `harisankar@sentellent.com` or your test account
   - Authorize the application
   - You should see the chat interface

3. **Test Chat**:
   - Send a message: "Hello, who are you?"
   - Verify you get a response
   - Send another message to test conversation history

**✅ Checkpoint**: Production application is working!

---

## 📋 Phase 11: Setup CI/CD Pipeline (20 minutes)

### Step 27: Configure GitHub Secrets

1. **Go to Your GitHub Repository**:
   - Visit: `https://github.com/YOUR_USERNAME/contextual-agentic-assistant`

2. **Navigate to Settings**:
   - Click "Settings" tab
   - Click "Secrets and variables" → "Actions"

3. **Add Repository Secrets**:
   Click "New repository secret" for each:

   - Name: `AWS_ACCESS_KEY_ID`
     Value: Your AWS access key

   - Name: `AWS_SECRET_ACCESS_KEY`
     Value: Your AWS secret key

   - Name: `GOOGLE_CLIENT_ID`
     Value: Your Google client ID

   - Name: `GOOGLE_CLIENT_SECRET`
     Value: Your Google client secret

   - Name: `OPENAI_API_KEY`
     Value: Your OpenAI API key

   - Name: `SECRET_KEY`
     Value: Your application secret key

### Step 28: Test CI/CD Pipeline

1. **Make a Small Change**:
```bash
# Edit README.md
echo "\n## Deployed!" >> README.md

# Commit and push
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin main
```

2. **Watch Pipeline**:
   - Go to: `https://github.com/YOUR_USERNAME/contextual-agentic-assistant/actions`
   - Click on the latest workflow run
   - Watch the jobs: test → build-and-push → deploy

3. **Wait for Completion** (10-15 minutes)

**✅ Checkpoint**: CI/CD pipeline is working!

---

## 📋 Phase 12: Take Screenshots (30 minutes)

### Step 29: AWS Console Screenshots

Take screenshots of:

1. **ECS Cluster**:
   - Go to: ECS → Clusters → agentic-assistant-cluster
   - Screenshot showing: Running services, task count

2. **ECS Service**:
   - Click on: agentic-assistant-backend-service
   - Screenshot showing: Desired/Running tasks, deployments

3. **RDS Database**:
   - Go to: RDS → Databases
   - Screenshot showing: agentic-assistant-db status (Available)

4. **ECR Repositories**:
   - Go to: ECR → Repositories
   - Screenshot showing: Both repositories with images

5. **CloudFront Distribution**:
   - Go to: CloudFront → Distributions
   - Screenshot showing: Status (Deployed), domain name

6. **Load Balancer**:
   - Go to: EC2 → Load Balancers
   - Screenshot showing: Active state, target groups

### Step 30: CI/CD Pipeline Screenshots

1. **GitHub Actions Workflow**:
   - Go to: Repository → Actions
   - Screenshot showing: Latest successful run

2. **Job Details**:
   - Click on the workflow run
   - Screenshot showing: All three jobs passed (test, build-and-push, deploy)

3. **Deploy Job Details**:
   - Click on "deploy" job
   - Screenshot showing: Successful deployment steps

### Step 31: Application Screenshots

1. **Login Page**:
   - Visit your CloudFront URL
   - Screenshot of login page

2. **OAuth Consent**:
   - Click "Sign in with Google"
   - Screenshot of Google consent screen

3. **Chat Interface**:
   - After logging in
   - Screenshot of chat interface

4. **Message Exchange**:
   - Send a message and get response
   - Screenshot showing conversation

**✅ Checkpoint**: All screenshots captured!

---

## 📋 Phase 13: Prepare Submission (20 minutes)

### Step 32: Organize Screenshots

1. **Create Screenshots Folder**:
```bash
mkdir submission-screenshots
cd submission-screenshots
```

2. **Organize Files**:
```
submission-screenshots/
├── aws-console/
│   ├── 1-ecs-cluster.png
│   ├── 2-ecs-service.png
│   ├── 3-rds-database.png
│   ├── 4-ecr-repositories.png
│   ├── 5-cloudfront.png
│   └── 6-load-balancer.png
├── cicd-pipeline/
│   ├── 1-workflow-overview.png
│   ├── 2-all-jobs-passed.png
│   └── 3-deploy-details.png
└── application/
    ├── 1-login-page.png
    ├── 2-oauth-consent.png
    ├── 3-chat-interface.png
    └── 4-conversation.png
```

3. **Create PDF** (optional but recommended):
   - Combine all screenshots into a single PDF
   - Name it: `sentellent-submission-YOUR_NAME.pdf`

### Step 33: Final Checklist

Go through SUBMISSION_CHECKLIST.md and verify:

- [ ] GitHub repository is public or evaluator has access
- [ ] All code is pushed to main branch
- [ ] README.md is complete
- [ ] Live application URL works
- [ ] Test user `harisankar@sentellent.com` can log in
- [ ] All screenshots are clear and labeled
- [ ] CI/CD pipeline is green

### Step 34: Fill Out Submission Form

1. **Go to Submission Form**:
   - Visit: https://forms.gle/VVd9r4kemkWoiQVQ8

2. **Fill Out Form**:
   - Name: Your full name
   - Email: Your email
   - GitHub Repository URL: `https://github.com/YOUR_USERNAME/contextual-agentic-assistant`
   - Live Application URL: Your CloudFront URL
   - Backend API URL: Your ALB URL
   - Upload AWS Console screenshots
   - Upload CI/CD pipeline screenshots
   - Additional notes: Mention any special features or challenges

3. **Review Everything**:
   - Double-check all URLs work
   - Verify screenshots are attached
   - Read through your submission

4. **Submit**! 🎉

**✅ Checkpoint**: Submission complete!

---

## 🎯 Post-Submission

### Step 35: Monitor Your Application

```bash
# Check ECS service status
aws ecs describe-services \
  --cluster agentic-assistant-cluster \
  --services agentic-assistant-backend-service

# View logs
aws logs tail /ecs/agentic-assistant-backend --follow

# Check costs
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

### Step 36: Prepare for Interview

Review these topics:
- Your architecture decisions
- How you implemented OAuth
- How Terraform provisions resources
- How CI/CD pipeline works
- Challenges you faced and how you solved them
- What you would improve given more time

---

## 🆘 Troubleshooting Common Issues

### Issue: Docker won't start
**Solution**:
```bash
# Restart Docker Desktop
# On Windows: Restart Docker Desktop app
# On Mac: Restart Docker Desktop app
# On Linux:
sudo systemctl restart docker
```

### Issue: Terraform apply fails
**Solution**:
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check Terraform state
terraform state list

# If needed, destroy and retry
terraform destroy
terraform apply
```

### Issue: ECS tasks won't start
**Solution**:
```bash
# Check CloudWatch logs
aws logs tail /ecs/agentic-assistant-backend --follow

# Common issues:
# - Wrong environment variables
# - Database connection failed
# - Secrets not accessible
```

### Issue: OAuth not working
**Solution**:
- Verify redirect URI matches exactly
- Check test user is added
- Verify credentials in Secrets Manager
- Check CORS settings

### Issue: CI/CD pipeline fails
**Solution**:
- Check GitHub secrets are set correctly
- Verify AWS credentials have correct permissions
- Check ECR repository names match
- Review workflow logs for specific error

---

## 📞 Need Help?

1. **Check Documentation**:
   - README.md
   - DEPLOYMENT.md
   - PROJECT_STATUS.md

2. **Check Logs**:
   - Local: `docker-compose logs`
   - AWS: CloudWatch Logs

3. **Common Commands**:
```bash
# Restart local services
docker-compose restart

# View specific service logs
docker-compose logs -f backend

# Check AWS resources
aws ecs list-services --cluster agentic-assistant-cluster
aws rds describe-db-instances
aws ecr describe-repositories
```

---

## 🎉 Congratulations!

You've successfully:
- ✅ Built a full-stack AI application
- ✅ Deployed to AWS with Terraform
- ✅ Set up automated CI/CD
- ✅ Implemented OAuth authentication
- ✅ Created production-ready infrastructure
- ✅ Submitted your project

**Good luck with your interview!** 🚀

---

*Estimated Total Time: 4-6 hours*
*Difficulty: Intermediate to Advanced*
*Technologies: Python, React, Docker, Terraform, AWS, OAuth*
