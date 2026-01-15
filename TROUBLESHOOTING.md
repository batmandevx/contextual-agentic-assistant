# Troubleshooting Guide

Common issues and their solutions.

---

## 🐳 Docker Issues

### Issue: "Cannot connect to Docker daemon"
**Symptoms**: `docker-compose up` fails with connection error

**Solutions**:
1. **Start Docker Desktop**:
   - Windows/Mac: Open Docker Desktop application
   - Linux: `sudo systemctl start docker`

2. **Check Docker is running**:
   ```bash
   docker ps
   ```

3. **Restart Docker**:
   - Windows/Mac: Restart Docker Desktop
   - Linux: `sudo systemctl restart docker`

### Issue: "Port already in use"
**Symptoms**: `Error: bind: address already in use`

**Solutions**:
1. **Find process using port**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   
   # Mac/Linux
   lsof -i :8000
   kill -9 <PID>
   ```

2. **Change ports in docker-compose.yml**:
   ```yaml
   ports:
     - "8001:8000"  # Change 8000 to 8001
   ```

### Issue: "No space left on device"
**Symptoms**: Docker build fails with disk space error

**Solutions**:
1. **Clean Docker**:
   ```bash
   docker system prune -a --volumes
   ```

2. **Remove unused images**:
   ```bash
   docker image prune -a
   ```

---

## 🔐 Authentication Issues

### Issue: "OAuth redirect URI mismatch"
**Symptoms**: After Google login, error about redirect URI

**Solutions**:
1. **Check redirect URI in Google Console**:
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click your OAuth client
   - Verify redirect URI matches EXACTLY:
     - Local: `http://localhost:8000/api/auth/callback`
     - Production: `http://YOUR_ALB_URL/api/auth/callback`
   - Note: http vs https matters!

2. **Check GOOGLE_REDIRECT_URI in .env**:
   ```env
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback
   ```

### Issue: "Test user not authorized"
**Symptoms**: "Access blocked: This app's request is invalid"

**Solutions**:
1. **Add test user in Google Console**:
   - Go to: OAuth consent screen
   - Scroll to "Test users"
   - Add: `harisankar@sentellent.com`
   - Add your own email for testing

2. **Verify OAuth consent screen is configured**:
   - User type should be "External"
   - Required scopes should be added

### Issue: "Invalid client ID or secret"
**Symptoms**: OAuth fails immediately

**Solutions**:
1. **Verify credentials in .env**:
   ```bash
   cat backend/.env | grep GOOGLE
   ```

2. **Check for extra spaces or quotes**:
   - Remove any quotes around values
   - Remove trailing spaces

3. **Regenerate credentials**:
   - Go to Google Cloud Console
   - Create new OAuth client
   - Update .env with new credentials

---

## 🗄️ Database Issues

### Issue: "Connection refused" to database
**Symptoms**: Backend can't connect to PostgreSQL

**Solutions**:
1. **Check database is running**:
   ```bash
   docker-compose ps db
   ```

2. **Check DATABASE_URL format**:
   ```env
   # Correct format
   DATABASE_URL=postgresql://postgres:postgres@db:5432/assistant
   
   # For production
   DATABASE_URL=postgresql://postgres:PASSWORD@RDS_ENDPOINT:5432/assistant
   ```

3. **Restart database**:
   ```bash
   docker-compose restart db
   ```

### Issue: "Database does not exist"
**Symptoms**: Error about missing database

**Solutions**:
1. **Create database**:
   ```bash
   docker-compose exec db psql -U postgres -c "CREATE DATABASE assistant;"
   ```

2. **Run migrations**:
   ```bash
   cd backend
   alembic upgrade head
   ```

### Issue: "Migration failed"
**Symptoms**: Alembic migration errors

**Solutions**:
1. **Check database connection**:
   ```bash
   docker-compose exec db psql -U postgres -d assistant -c "SELECT 1;"
   ```

2. **Reset migrations** (CAUTION: Deletes data):
   ```bash
   # Drop all tables
   docker-compose exec db psql -U postgres -d assistant -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
   
   # Run migrations again
   cd backend
   alembic upgrade head
   ```

---

## ☁️ AWS Deployment Issues

### Issue: Terraform "Error: creating S3 Bucket"
**Symptoms**: Terraform fails to create resources

**Solutions**:
1. **Check AWS credentials**:
   ```bash
   aws sts get-caller-identity
   ```

2. **Verify IAM permissions**:
   - User needs: S3, ECS, RDS, VPC, IAM, CloudFront permissions

3. **Use unique bucket name**:
   - S3 bucket names must be globally unique
   - Add random suffix to bucket name

### Issue: "ECS task failed to start"
**Symptoms**: ECS service shows 0 running tasks

**Solutions**:
1. **Check CloudWatch logs**:
   ```bash
   aws logs tail /ecs/agentic-assistant-backend --follow
   ```

2. **Common causes**:
   - **Wrong environment variables**: Check Secrets Manager
   - **Database connection failed**: Check security groups
   - **Image pull failed**: Check ECR repository
   - **Insufficient memory**: Increase task memory

3. **Check task definition**:
   ```bash
   aws ecs describe-task-definition \
     --task-definition agentic-assistant-backend
   ```

4. **Check security groups**:
   ```bash
   # ECS tasks should allow outbound to RDS
   aws ec2 describe-security-groups \
     --filters "Name=group-name,Values=*ecs*"
   ```

### Issue: "Cannot pull image from ECR"
**Symptoms**: ECS task fails with image pull error

**Solutions**:
1. **Verify image exists**:
   ```bash
   aws ecr describe-images \
     --repository-name agentic-assistant-backend
   ```

2. **Check ECR permissions**:
   - ECS execution role needs ECR pull permissions

3. **Re-push image**:
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin \
     $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com
   
   # Push image
   docker push YOUR_ECR_URL:latest
   ```

### Issue: "RDS database not accessible"
**Symptoms**: Backend can't connect to RDS

**Solutions**:
1. **Check security groups**:
   - RDS security group should allow inbound from ECS security group
   - Port 5432 should be open

2. **Check RDS status**:
   ```bash
   aws rds describe-db-instances \
     --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus]'
   ```

3. **Verify connection string**:
   ```bash
   # Get RDS endpoint
   aws rds describe-db-instances \
     --query 'DBInstances[0].Endpoint.Address' \
     --output text
   ```

4. **Check Secrets Manager**:
   ```bash
   aws secretsmanager get-secret-value \
     --secret-id agentic-assistant-secrets \
     --query SecretString \
     --output text
   ```

---

## 🔄 CI/CD Issues

### Issue: "GitHub Actions workflow fails"
**Symptoms**: Pipeline shows red X

**Solutions**:
1. **Check workflow logs**:
   - Go to: Repository → Actions → Click failed run
   - Review each job's logs

2. **Verify GitHub secrets**:
   - Go to: Repository → Settings → Secrets
   - Ensure all required secrets are set:
     - AWS_ACCESS_KEY_ID
     - AWS_SECRET_ACCESS_KEY
     - GOOGLE_CLIENT_ID
     - GOOGLE_CLIENT_SECRET
     - OPENAI_API_KEY
     - SECRET_KEY

3. **Common failures**:
   - **Test job fails**: Fix code errors
   - **Build job fails**: Check Dockerfile syntax
   - **Deploy job fails**: Check AWS permissions

### Issue: "AWS credentials not working in GitHub Actions"
**Symptoms**: Deploy job fails with auth error

**Solutions**:
1. **Regenerate AWS access keys**:
   - Go to IAM → Users → Your user → Security credentials
   - Create new access key
   - Update GitHub secrets

2. **Check IAM permissions**:
   - User needs: ECS, ECR, CloudWatch permissions

---

## 🌐 Frontend Issues

### Issue: "Frontend shows blank page"
**Symptoms**: White screen, no errors in console

**Solutions**:
1. **Check API URL**:
   ```env
   # frontend/.env.local
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

2. **Check backend is running**:
   ```bash
   curl http://localhost:8000/api/health
   ```

3. **Check browser console**:
   - Open DevTools (F12)
   - Look for CORS or network errors

4. **Rebuild frontend**:
   ```bash
   docker-compose down
   docker-compose up --build frontend
   ```

### Issue: "CORS error in browser"
**Symptoms**: "Access-Control-Allow-Origin" error

**Solutions**:
1. **Check CORS_ORIGINS in backend/.env**:
   ```env
   CORS_ORIGINS=["http://localhost:3000"]
   ```

2. **Verify CORS middleware in main.py**:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=settings.CORS_ORIGINS,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **For production, add CloudFront URL**:
   ```env
   CORS_ORIGINS=["http://localhost:3000","https://YOUR_CLOUDFRONT_URL"]
   ```

---

## 🤖 Agent/LLM Issues

### Issue: "OpenAI API error"
**Symptoms**: Chat doesn't respond or shows API error

**Solutions**:
1. **Verify API key**:
   ```bash
   # Test API key
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```

2. **Check API quota**:
   - Go to: https://platform.openai.com/account/usage
   - Verify you have credits

3. **Check rate limits**:
   - Free tier: 3 requests/minute
   - Paid tier: Higher limits

4. **Use different model**:
   ```env
   # In backend/.env
   OPENAI_MODEL=gpt-3.5-turbo  # Cheaper alternative
   ```

### Issue: "Agent not responding"
**Symptoms**: Messages send but no response

**Solutions**:
1. **Check backend logs**:
   ```bash
   docker-compose logs -f backend
   ```

2. **Verify LangGraph is working**:
   - Look for errors in agent.py
   - Check LangChain/LangGraph versions

3. **Test with simple message**:
   - Send: "Hello"
   - Should get basic response

---

## 💰 Cost Issues

### Issue: "AWS bill is too high"
**Symptoms**: Unexpected charges

**Solutions**:
1. **Check current costs**:
   ```bash
   aws ce get-cost-and-usage \
     --time-period Start=2026-01-01,End=2026-01-31 \
     --granularity MONTHLY \
     --metrics BlendedCost
   ```

2. **Stop services temporarily**:
   ```bash
   # Stop ECS service
   aws ecs update-service \
     --cluster agentic-assistant-cluster \
     --service agentic-assistant-backend-service \
     --desired-count 0
   
   # Stop RDS
   aws rds stop-db-instance \
     --db-instance-identifier agentic-assistant-db
   ```

3. **Use smaller instances**:
   - RDS: Use db.t3.micro (free tier)
   - ECS: Use 0.25 vCPU, 512 MB memory

4. **Delete unused resources**:
   ```bash
   # Delete old ECR images
   aws ecr batch-delete-image \
     --repository-name agentic-assistant-backend \
     --image-ids imageDigest=sha256:xxx
   ```

---

## 🔍 Debugging Tips

### Enable Debug Logging

1. **Backend**:
   ```env
   # backend/.env
   LOG_LEVEL=DEBUG
   DEBUG=True
   ```

2. **View detailed logs**:
   ```bash
   docker-compose logs -f backend | grep ERROR
   ```

### Test Individual Components

1. **Test database connection**:
   ```bash
   docker-compose exec backend python -c "from database import engine; print(engine.connect())"
   ```

2. **Test OAuth flow**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login
   ```

3. **Test chat endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/chat/message \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"message":"Hello"}'
   ```

### Common Log Patterns

**Look for these in logs**:
- `ERROR`: Something failed
- `WARNING`: Potential issue
- `INFO`: Normal operation
- `DEBUG`: Detailed information

**Useful grep commands**:
```bash
# Find errors
docker-compose logs backend | grep ERROR

# Find database queries
docker-compose logs backend | grep "SELECT\|INSERT\|UPDATE"

# Find API calls
docker-compose logs backend | grep "POST\|GET"
```

---

## 📞 Getting Help

### Before Asking for Help

1. **Check logs**:
   ```bash
   docker-compose logs -f
   ```

2. **Verify configuration**:
   - Check all .env files
   - Verify credentials are correct
   - Check URLs and endpoints

3. **Try clean restart**:
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

### Information to Provide

When asking for help, include:
- Error message (full text)
- Relevant logs
- What you were trying to do
- What you've already tried
- Your environment (OS, Docker version, etc.)

### Useful Diagnostic Commands

```bash
# System info
docker version
docker-compose version
python --version
node --version

# Service status
docker-compose ps
aws ecs describe-services --cluster agentic-assistant-cluster --services agentic-assistant-backend-service

# Network connectivity
curl http://localhost:8000/api/health
ping YOUR_RDS_ENDPOINT

# Resource usage
docker stats
aws cloudwatch get-metric-statistics --namespace AWS/ECS --metric-name CPUUtilization
```

---

## 🆘 Emergency Procedures

### Complete Reset (Local)

```bash
# Stop everything
docker-compose down -v

# Remove all containers
docker container prune -f

# Remove all images
docker image prune -a -f

# Remove all volumes
docker volume prune -f

# Start fresh
docker-compose up --build
```

### Complete Reset (AWS)

```bash
# Destroy all infrastructure
cd terraform
terraform destroy

# Delete S3 state bucket
aws s3 rb s3://agentic-assistant-terraform-state-YOUR-ID --force

# Delete ECR images
aws ecr batch-delete-image --repository-name agentic-assistant-backend --image-ids "$(aws ecr list-images --repository-name agentic-assistant-backend --query 'imageIds[*]' --output json)"
aws ecr batch-delete-image --repository-name agentic-assistant-frontend --image-ids "$(aws ecr list-images --repository-name agentic-assistant-frontend --query 'imageIds[*]' --output json)"

# Start over
terraform init
terraform apply
```

---

*Remember: Most issues can be solved by checking logs and verifying configuration!*
