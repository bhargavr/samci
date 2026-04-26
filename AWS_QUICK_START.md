# AWS Deployment - Quick Start

Get your app running on AWS in 10 minutes.

## ⚡ Prerequisites (5 minutes)

```bash
# Install AWS CLI
brew install awscli                    # macOS
# Or: https://aws.amazon.com/cli/

# Install SAM CLI
brew tap aws/tap
brew install aws-sam-cli

# Install Docker (required for SAM build)
brew install --cask docker

# Configure AWS
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Output (json)
```

## 🚀 Deploy (3 commands)

```bash
# 1. Deploy backend (Lambda + API Gateway)
./deploy-backend.sh

# 2. Deploy frontend (S3 + CloudFront)
./deploy-frontend.sh

# 3. Open CloudFront URL in browser
# URL printed in terminal output
```

## 📋 First-Time Deployment Prompts

When running `./deploy-backend.sh` for the first time:

```
Stack Name: <press Enter>                    # Use default
AWS Region: <press Enter>                    # Use us-east-1
Parameter Environment: <press Enter>         # Use dev
Confirm changes before deploy: Y             # Review changes
Allow SAM CLI IAM role creation: Y           # Required
Disable rollback: N                          # Keep rollback
Authorization not defined: y                 # Public API
Save arguments to config file: Y             # Save for next time
```

## 💰 Cost

- **MVP (10K requests/month):** $2-5/month
- **Medium (100K requests/month):** ~$10/month
- **High (1M requests/month):** ~$55/month

**Free tier:** First 12 months include 1M Lambda requests, 1TB CloudFront

## 📊 What Gets Created

```
AWS Resources:
├── Lambda Function (granite-packer-api-dev)
├── API Gateway (HTTP API)
├── S3 Bucket (Frontend)
├── S3 Bucket (Results - Optional)
├── CloudFront Distribution
├── CloudWatch Log Group
└── IAM Roles (auto-created)
```

## 🔍 Test Deployment

```bash
# Get API URL
API_URL=$(aws cloudformation describe-stacks \
    --stack-name granite-packer-stack \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
    --output text)

# Test health endpoint
curl $API_URL/

# Expected: {"service":"Granite Crate Packing Optimizer",...}
```

## 🔄 Update After Code Changes

```bash
# Backend changes
./deploy-backend.sh

# Frontend changes
./deploy-frontend.sh

# Both
./deploy-backend.sh && ./deploy-frontend.sh
```

## 👀 View Logs

```bash
# Real-time
aws logs tail /aws/lambda/granite-packer-api-dev --follow

# Recent errors
aws logs filter-log-events \
    --log-group-name /aws/lambda/granite-packer-api-dev \
    --filter-pattern "ERROR"
```

## 💸 View Costs

```bash
# Current month
aws ce get-cost-and-usage \
    --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
    --granularity MONTHLY \
    --metrics "UnblendedCost" \
    --group-by Type=SERVICE
```

## 🗑️ Delete Everything

```bash
# Delete stack (removes all resources)
aws cloudformation delete-stack --stack-name granite-packer-stack

# Empty S3 buckets first if needed
aws s3 rm s3://BUCKET_NAME --recursive
```

## 🐛 Common Issues

### "SAM CLI not found"
```bash
brew tap aws/tap
brew install aws-sam-cli
```

### "AccessDenied" errors
```bash
# Check credentials
aws sts get-caller-identity

# Reconfigure if needed
aws configure
```

### "Docker not running"
```bash
# Start Docker Desktop
open -a Docker
```

### Lambda timeout
```yaml
# Edit template.yaml
Timeout: 30  # Increase from 15
```

## 🤖 CI/CD (Optional)

### GitHub Actions
1. Add secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
2. Push to main: `git push origin main`
3. Auto-deploys in ~5 minutes

### GitLab CI
1. Add variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
2. Push to main: `git push origin main`
3. Auto-deploys in ~5 minutes

## 📚 Full Documentation

- **AWS_DEPLOYMENT.md** - Complete guide (20+ pages)
- **AWS_SUMMARY.md** - Architecture overview
- **CI_CD_SETUP.md** - Automated pipelines
- **COST_OPTIMIZATION.md** - Reduce costs

## ✅ Success Checklist

After deployment:
- [ ] API endpoint returns 200 OK
- [ ] Frontend loads in browser
- [ ] Can click "Load Example"
- [ ] Can click "Optimize Packing"
- [ ] 3D visualization appears
- [ ] Check CloudWatch logs (no errors)
- [ ] Verify costs in AWS Cost Explorer

## 🎯 Next Steps

1. **Set up billing alerts** (AWS Console → Billing → Budgets)
2. **Monitor logs** for errors
3. **Test with real data**
4. **Configure CI/CD** for auto-deployments
5. **Add custom domain** (optional)

## 📞 Help

- **Deployment issues:** Check `AWS_DEPLOYMENT.md`
- **Cost questions:** Check `COST_OPTIMIZATION.md`
- **CI/CD setup:** Check `CI_CD_SETUP.md`

---

**Time to deploy:** 10 minutes  
**Cost:** $2-5/month (MVP)  
**Scaling:** Automatic (1 to 1M requests)

**Ready?** Run `./deploy-backend.sh` to start! 🚀
