# AWS Serverless Deployment Guide

Complete guide to deploy the Granite Crate Packing Optimizer to AWS using a serverless architecture.

## 🏗️ Architecture Overview

```
┌─────────────┐
│   Users     │
└──────┬──────┘
       │
       ↓
┌──────────────────────────────────────┐
│       CloudFront (CDN)               │
│   - HTTPS                            │
│   - Global edge caching              │
│   - Custom domain (optional)         │
└──────┬───────────────────────────────┘
       │
       ├────────────────┬─────────────────┐
       │                │                 │
       ↓                ↓                 ↓
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│  S3 Bucket  │  │ API Gateway  │  │  S3 Results  │
│  (Frontend) │  │  (HTTP API)  │  │   (Optional) │
│             │  │              │  │              │
│ - React SPA │  │ - REST API   │  │ - Store logs │
│ - Static    │  │ - CORS       │  │ - Auto-clean │
└─────────────┘  └──────┬───────┘  └──────────────┘
                        │
                        ↓
                 ┌──────────────┐
                 │    Lambda    │
                 │              │
                 │ - FastAPI    │
                 │ - Python3.11 │
                 │ - 1024 MB    │
                 │ - 15s max    │
                 └──────────────┘
```

## 💰 Cost Breakdown

### Monthly Cost Estimate (Low Usage)

**Assumptions:**
- 10,000 API requests/month
- 1,000 unique users/month
- 50 GB data transfer out
- Development/MVP stage

| Service | Usage | Cost | Notes |
|---------|-------|------|-------|
| **Lambda** | 10K requests @ 1024MB, 2s avg | $0.00 | Free tier: 1M requests, 400K GB-seconds |
| **API Gateway (HTTP API)** | 10K requests | $0.01 | $1.00 per million requests |
| **S3 (Frontend)** | 1 GB storage, 10K GET requests | $0.05 | Storage: $0.023/GB, Requests: $0.0004/1K |
| **CloudFront** | 50 GB transfer, 10K requests | $4.25 | First 10TB: $0.085/GB |
| **CloudWatch Logs** | 1 GB logs, 7-day retention | $0.50 | $0.50/GB ingestion |
| **S3 (Results - Optional)** | 1 GB storage, auto-delete 7d | $0.03 | Optional feature |
| **Total (without free tier)** | | **~$5/month** | |
| **Total (with free tier)** | | **~$2-3/month** | First 12 months |

### Cost at Scale

**10x Scale (100K requests/month):**
- Lambda: $0.20
- API Gateway: $0.10
- CloudFront: $8.50
- Other: $1.00
- **Total: ~$10/month**

**100x Scale (1M requests/month):**
- Lambda: $2.00
- API Gateway: $1.00
- CloudFront: $50.00
- Other: $2.00
- **Total: ~$55/month**

**Cost Optimization Tips:**
1. Enable CloudFront caching (reduces API calls)
2. Use 7-day log retention (not 30 days)
3. Set S3 lifecycle policies (auto-delete old results)
4. Use HTTP API (not REST API - 70% cheaper)
5. Right-size Lambda memory (1024MB optimal)

## 📋 Prerequisites

### 1. Install Required Tools

**AWS CLI**
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Download installer from: https://awscli.amazonaws.com/AWSCLIV2.msi
```

**AWS SAM CLI**
```bash
# macOS
brew tap aws/tap
brew install aws-sam-cli

# Linux
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install

# Windows
# Download MSI installer from: https://github.com/aws/aws-sam-cli/releases/latest
```

**Docker** (required for SAM build)
```bash
# macOS
brew install --cask docker

# Linux
sudo apt-get install docker.io

# Windows
# Download Docker Desktop from: https://www.docker.com/products/docker-desktop
```

**Verify installations:**
```bash
aws --version
sam --version
docker --version
```

### 2. Configure AWS Credentials

```bash
# Run AWS configure
aws configure

# Enter your credentials:
AWS Access Key ID [None]: YOUR_ACCESS_KEY
AWS Secret Access Key [None]: YOUR_SECRET_KEY
Default region name [None]: us-east-1
Default output format [None]: json
```

**Create IAM User (if needed):**
1. Go to AWS Console → IAM → Users
2. Create new user with programmatic access
3. Attach policies:
   - `AdministratorAccess` (for deployment)
   - Or custom policy with permissions for:
     - Lambda, API Gateway, S3, CloudFront, CloudFormation, IAM, CloudWatch

### 3. Verify AWS Access

```bash
# Test credentials
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "AIDACKCEVSQ6C2EXAMPLE",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-username"
# }
```

## 🚀 Deployment Steps

### Step 1: Deploy Backend (Lambda + API Gateway)

```bash
# Make sure you're in the project root
cd /path/to/samci

# Run deployment script
./deploy-backend.sh

# Or manual steps:
sam build --use-container
sam deploy --guided
```

**First-time deployment prompts:**
```
Stack Name [granite-packer-stack]: <press Enter>
AWS Region [us-east-1]: <press Enter>
Parameter Environment [dev]: <press Enter>
Confirm changes before deploy [Y/n]: Y
Allow SAM CLI IAM role creation [Y/n]: Y
Disable rollback [y/N]: N
PackingOptimizerFunction may not have authorization defined, Is this okay? [y/N]: y
Save arguments to configuration file [Y/n]: Y
SAM configuration file [samconfig.toml]: <press Enter>
SAM configuration environment [default]: <press Enter>
```

**Expected output:**
```
CloudFormation outputs from deployed stack
--------------------------------------------------------------------------------
Outputs
--------------------------------------------------------------------------------
Key                 ApiUrl
Description         HTTP API Gateway endpoint URL
Value               https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev

Key                 CloudFrontUrl
Description         CloudFront Distribution URL
Value               https://d1234567890abc.cloudfront.net

Key                 FunctionName
Description         Lambda Function Name
Value               granite-packer-api-dev
--------------------------------------------------------------------------------
```

**Save the `ApiUrl` - you'll need it for the frontend!**

### Step 2: Test Backend API

```bash
# Get API URL from outputs
API_URL=$(aws cloudformation describe-stacks \
    --stack-name granite-packer-stack \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
    --output text)

echo "API URL: $API_URL"

# Test health endpoint
curl $API_URL/

# Expected: {"service":"Granite Crate Packing Optimizer","status":"operational","version":"1.0.0"}

# Test optimization
curl -X POST $API_URL/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "container": {"length": 5898, "width": 2352, "height": 2393, "max_weight": 28000},
    "crates": [
      {"id": "TestCrate", "length": 1200, "width": 1000, "height": 800, "weight": 1200, "quantity": 5, "max_stack": 2, "can_rotate": true}
    ]
  }'

# Should return packing results JSON
```

### Step 3: Deploy Frontend (S3 + CloudFront)

```bash
# Run deployment script
./deploy-frontend.sh
```

**What it does:**
1. Fetches backend API URL from CloudFormation
2. Creates `.env.production` with API URL
3. Builds React app with production config
4. Uploads to S3 bucket
5. Invalidates CloudFront cache
6. Tests deployment

**Expected output:**
```
Frontend URL: https://d1234567890abc.cloudfront.net
API URL: https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev

Open your browser to:
  https://d1234567890abc.cloudfront.net
```

### Step 4: Verify Deployment

1. **Open CloudFront URL** in browser
2. **Click "Load Example"** button
3. **Click "Optimize Packing"** button
4. **Verify 3D visualization appears**

## 🔍 Monitoring & Logs

### View Lambda Logs

```bash
# Real-time logs
aws logs tail /aws/lambda/granite-packer-api-dev --follow

# Recent logs
aws logs tail /aws/lambda/granite-packer-api-dev --since 1h

# Search for errors
aws logs filter-log-events \
    --log-group-name /aws/lambda/granite-packer-api-dev \
    --filter-pattern "ERROR"
```

### View CloudWatch Metrics

```bash
# Lambda invocations (last hour)
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=granite-packer-api-dev \
    --statistics Sum \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300

# Lambda errors
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Errors \
    --dimensions Name=FunctionName,Value=granite-packer-api-dev \
    --statistics Sum \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300
```

### AWS Console Links

- **Lambda:** https://console.aws.amazon.com/lambda/home#/functions/granite-packer-api-dev
- **API Gateway:** https://console.aws.amazon.com/apigateway/home
- **S3 Buckets:** https://console.aws.amazon.com/s3/home
- **CloudFront:** https://console.aws.amazon.com/cloudfront/home
- **CloudWatch:** https://console.aws.amazon.com/cloudwatch/home

## 🔄 Update Deployment

### Update Backend Only

```bash
# After code changes
./deploy-backend.sh

# Or manually
sam build --use-container
sam deploy --no-confirm-changeset
```

### Update Frontend Only

```bash
# After UI changes
./deploy-frontend.sh
```

### Update Both

```bash
# Deploy backend first
./deploy-backend.sh

# Then frontend
./deploy-frontend.sh
```

## ⚙️ Configuration

### Environment Variables

Edit `template.yaml` to add Lambda environment variables:

```yaml
Environment:
  Variables:
    ENVIRONMENT: !Ref Environment
    MAX_CRATES: "100"
    TIMEOUT_SECONDS: "10"
    # Add your variables here
```

### Lambda Memory/Timeout

Edit `template.yaml`:

```yaml
Globals:
  Function:
    Timeout: 30  # seconds (max 900)
    MemorySize: 2048  # MB (128 to 10240)
```

**Memory vs Cost:**
- 128 MB: Cheapest, may timeout
- 512 MB: Good for small loads
- 1024 MB: Recommended (optimal price/performance)
- 2048 MB: For large/complex packing

### CloudFront Caching

Edit `template.yaml` cache settings:

```yaml
DefaultCacheBehavior:
  DefaultTTL: 86400     # 1 day (increase for more caching)
  MaxTTL: 31536000      # 1 year
  MinTTL: 0             # No minimum
```

## 🐛 Troubleshooting

### Issue: "SAM CLI not found"
**Solution:** Install AWS SAM CLI (see prerequisites)

### Issue: "Docker not running"
**Solution:**
```bash
# Start Docker
# macOS: Open Docker Desktop
# Linux: sudo service docker start
```

### Issue: "Access Denied" during deployment
**Solution:** Check IAM permissions. User needs CloudFormation, Lambda, S3, API Gateway access.

### Issue: Lambda timeout
**Solution:** Increase timeout in `template.yaml`:
```yaml
Timeout: 30  # Increase from 15
```

### Issue: CORS errors in browser
**Solution:** Check API Gateway CORS settings in `template.yaml`. Should have:
```yaml
AllowOrigin: "'*'"
AllowMethods: "'GET,POST,OPTIONS'"
```

### Issue: CloudFront shows old version
**Solution:** Invalidate cache:
```bash
DIST_ID=$(aws cloudformation describe-stacks \
    --stack-name granite-packer-stack \
    --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomain'].OutputValue" \
    --output text | cut -d'.' -f1)

aws cloudfront create-invalidation \
    --distribution-id $DIST_ID \
    --paths "/*"
```

### Issue: Lambda cold start is slow
**Solutions:**
1. Use provisioned concurrency (costs more):
```yaml
ProvisionedConcurrencyConfig:
  ProvisionedConcurrentExecutions: 1
```

2. Optimize dependencies (remove unused packages)
3. Increase memory (faster CPU)
4. Use Lambda SnapStart (Java only, not Python yet)

## 🗑️ Cleanup (Delete All Resources)

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name granite-packer-stack

# Empty S3 buckets first (required)
FRONTEND_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name granite-packer-stack \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
    --output text)

aws s3 rm s3://$FRONTEND_BUCKET --recursive

# Delete stack
aws cloudformation delete-stack --stack-name granite-packer-stack

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name granite-packer-stack

# Verify deletion
aws cloudformation describe-stacks --stack-name granite-packer-stack
# Should return: Stack with id granite-packer-stack does not exist
```

**Cost after deletion:** $0 (all resources deleted)

## 📊 Performance Optimization

### Cold Start Optimization

**Current cold start:** ~2-3 seconds

**Reduce to <1 second:**
1. Minimize dependencies (use `requirements-lambda.txt`)
2. Use Lambda layers for large dependencies
3. Increase memory to 1536 MB (faster CPU)
4. Reduce package size (<50 MB)

### API Response Time

**Current:** 50-200ms for typical loads

**Optimize:**
1. Enable CloudFront API caching (for GET endpoints)
2. Implement result caching in S3
3. Use Lambda@Edge for regional processing

### Frontend Load Time

**Current:** 2-3 seconds initial load

**Optimize:**
1. CloudFront caching (already enabled)
2. Enable Brotli compression
3. Code splitting (lazy load components)
4. Reduce bundle size

## 🔐 Security Best Practices

### Current Security:
- ✅ HTTPS only (CloudFront + API Gateway)
- ✅ S3 bucket not public (CloudFront OAI only)
- ✅ IAM least-privilege roles
- ✅ No hardcoded secrets

### Enhanced Security (Optional):
1. **API Key authentication:**
```yaml
Auth:
  ApiKeyRequired: true
```

2. **WAF (Web Application Firewall):**
```bash
# Add WAF to CloudFront
aws wafv2 create-web-acl ...
```

3. **VPC for Lambda** (if accessing private resources)
4. **Secrets Manager** (for API keys, if needed)

## 🚀 CI/CD Pipeline (Bonus)

See `ci-cd-setup.md` for GitHub Actions and GitLab CI configurations.

## 📚 Additional Resources

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [CloudFront Pricing](https://aws.amazon.com/cloudfront/pricing/)
- [API Gateway Pricing](https://aws.amazon.com/api-gateway/pricing/)

---

**Questions?** Check the troubleshooting section or raise an issue.

**Cost concerns?** All services are pay-per-use. Estimated $2-5/month for MVP usage.
