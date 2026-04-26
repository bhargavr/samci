# CI/CD Pipeline Setup

Automated deployment pipelines for GitHub Actions and GitLab CI.

## 🎯 Overview

The CI/CD pipeline automatically:
1. **Builds** the backend (Lambda function)
2. **Deploys** backend to AWS (Lambda + API Gateway)
3. **Tests** API health
4. **Builds** frontend (React app)
5. **Deploys** frontend to S3 + CloudFront
6. **Invalidates** CloudFront cache

**Trigger:** Push to `main` or `develop` branches

**Duration:** ~5-7 minutes

## 🔧 GitHub Actions Setup

### 1. Add AWS Credentials to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | IAM user secret key |

### 2. Create IAM User for CI/CD

**Option A: Use existing admin user** (quick, less secure)

**Option B: Create dedicated CI/CD user** (recommended)

```bash
# Create IAM user
aws iam create-user --user-name github-actions-deployer

# Attach policies
aws iam attach-user-policy \
    --user-name github-actions-deployer \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Or create custom policy with minimum permissions:
# - CloudFormation full access
# - Lambda full access
# - S3 full access
# - API Gateway full access
# - CloudFront full access
# - IAM role creation
# - CloudWatch Logs

# Create access key
aws iam create-access-key --user-name github-actions-deployer

# Output will contain AccessKeyId and SecretAccessKey
# Add these to GitHub Secrets
```

### 3. Verify Workflow File

The workflow file is already created at `.github/workflows/deploy.yml`.

**To customize:**
- Edit `AWS_REGION` (default: us-east-1)
- Edit `STACK_NAME` (default: granite-packer-stack)
- Add/modify deployment stages

### 4. Test Pipeline

```bash
# Commit and push
git add .
git commit -m "Setup CI/CD pipeline"
git push origin main

# View workflow
# Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

### 5. Monitor Deployment

1. Go to **Actions** tab in GitHub
2. Click on the latest workflow run
3. View logs for each job:
   - `deploy-backend`
   - `deploy-frontend`

**Expected output:**
```
✅ deploy-backend: Success
   - SAM Build completed
   - SAM Deploy completed
   - API health check passed

✅ deploy-frontend: Success
   - React build completed
   - S3 sync completed
   - CloudFront invalidation created
```

### 6. Workflow Features

**Automatic environment detection:**
- `main` branch → `prod` environment
- `develop` branch → `dev` environment

**Caching:**
- Python dependencies cached
- Node modules cached
- SAM build cache

**Parallel jobs:**
- Backend and frontend tested in parallel
- Frontend waits for backend API URL

**Failure handling:**
- API health check fails → deployment stops
- Build fails → no deployment

## 🦊 GitLab CI Setup

### 1. Add AWS Credentials to GitLab CI/CD Variables

1. Go to your GitLab project
2. Click **Settings** → **CI/CD**
3. Expand **Variables**
4. Add the following variables:

| Variable Name | Value | Protected | Masked | Description |
|---------------|-------|-----------|--------|-------------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | ✅ | ✅ | IAM access key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | ✅ | ✅ | IAM secret key |
| `AWS_DEFAULT_REGION` | us-east-1 | ❌ | ❌ | AWS region |

### 2. Verify Pipeline File

The pipeline file is already created at `.gitlab-ci.yml`.

**Pipeline stages:**
1. `build` - Build backend with SAM
2. `deploy-backend` - Deploy Lambda + API Gateway
3. `deploy-frontend` - Build and deploy React app

### 3. Test Pipeline

```bash
# Commit and push
git add .
git commit -m "Setup GitLab CI/CD"
git push origin main

# View pipeline
# Go to: https://gitlab.com/YOUR_USERNAME/YOUR_REPO/-/pipelines
```

### 4. Monitor Pipeline

1. Go to **CI/CD** → **Pipelines**
2. Click on the latest pipeline
3. View logs for each stage

### 5. Pipeline Features

**Caching:**
- SAM build cache
- Node modules cache
- Shared between pipeline runs

**Artifacts:**
- Backend build artifacts passed to deploy stage
- Frontend build artifacts passed to deploy stage
- Environment variables passed between jobs

**Only triggers:**
- Runs only on `main` and `develop` branches
- Skip for other branches (e.g., feature branches)

## 🔒 Security Best Practices

### 1. Least Privilege IAM Policy

Instead of `AdministratorAccess`, use custom policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "lambda:*",
        "apigateway:*",
        "s3:*",
        "cloudfront:*",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:GetRole",
        "iam:PassRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2. Separate Environments

Create separate stacks for dev/staging/prod:

**GitHub Actions:**
```yaml
- name: SAM Deploy
  run: |
    if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
      STACK_NAME="granite-packer-prod"
      ENVIRONMENT="prod"
    else
      STACK_NAME="granite-packer-dev"
      ENVIRONMENT="dev"
    fi

    sam deploy \
      --stack-name $STACK_NAME \
      --parameter-overrides "Environment=$ENVIRONMENT"
```

### 3. Manual Approval for Production

Add manual approval step for production deployments:

**GitHub Actions:**
```yaml
deploy-prod:
  needs: deploy-backend
  if: github.ref == 'refs/heads/main'
  environment:
    name: production
    url: https://your-app.com
  # Requires manual approval in GitHub Settings → Environments
```

**GitLab CI:**
```yaml
deploy-production:
  stage: deploy
  when: manual
  only:
    - main
```

## 📊 Monitoring & Notifications

### GitHub Actions Notifications

**Slack Integration:**
```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

**Email Notifications:**
- Go to **Settings** → **Notifications**
- Enable workflow notifications

### GitLab CI Notifications

**Slack Integration:**
1. Go to **Settings** → **Integrations**
2. Click **Slack notifications**
3. Configure webhook URL
4. Select events: Pipeline success/failure

**Email Notifications:**
- Automatic for pipeline failures
- Configure in user preferences

## 🐛 Troubleshooting

### Issue: "AccessDenied" errors

**Cause:** IAM user doesn't have required permissions

**Solution:**
```bash
# Check IAM policies
aws iam list-attached-user-policies --user-name github-actions-deployer

# Verify credentials work
aws sts get-caller-identity
```

### Issue: SAM build fails

**Cause:** Docker not available in CI environment

**Solution:** Use `--use-container` flag (already in workflows)

### Issue: CloudFront invalidation slow

**Cause:** CloudFront cache invalidation takes 5-15 minutes

**Solution:** This is normal. Users may see old version until invalidation completes.

**Workaround:** Use versioned file names in build:
```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name].[hash].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash].[ext]'
      }
    }
  }
}
```

### Issue: Frontend shows old API URL

**Cause:** Environment variable not passed correctly

**Solution:** Check `.env.production` is created before build:
```bash
cat .env.production
# Should show: VITE_API_URL=https://...
```

### Issue: Pipeline runs on every branch

**GitHub Actions - Solution:** Add branch filter:
```yaml
on:
  push:
    branches:
      - main
      - develop
```

**GitLab CI - Solution:** Use `only:` directive:
```yaml
deploy:
  only:
    - main
    - develop
```

## 🔄 Rollback Strategy

### Automatic Rollback

CloudFormation automatically rolls back on failure.

### Manual Rollback

**Roll back to previous version:**
```bash
# List stack events
aws cloudformation describe-stack-events \
    --stack-name granite-packer-stack \
    --max-items 20

# Roll back
aws cloudformation cancel-update-stack \
    --stack-name granite-packer-stack
```

**Deploy specific version:**
```bash
# Checkout previous commit
git checkout <previous-commit-hash>

# Manually deploy
./deploy-backend.sh
./deploy-frontend.sh
```

### Frontend Rollback (Fast)

```bash
# Get previous S3 version
aws s3api list-object-versions \
    --bucket granite-packer-frontend-dev-123456789 \
    --prefix index.html

# Restore previous version
aws s3api copy-object \
    --bucket granite-packer-frontend-dev-123456789 \
    --copy-source granite-packer-frontend-dev-123456789/index.html?versionId=<VERSION_ID> \
    --key index.html

# Invalidate CloudFront
aws cloudfront create-invalidation \
    --distribution-id <DIST_ID> \
    --paths "/index.html"
```

## 📈 Performance Tips

### 1. Speed Up Builds

**Cache more aggressively:**
```yaml
cache:
  paths:
    - .aws-sam/build/
    - frontend/node_modules/
    - ~/.npm
    - ~/.cache/pip
```

### 2. Parallel Jobs

Run independent jobs in parallel:
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    # Runs in parallel with deploy

  deploy:
    runs-on: ubuntu-latest
```

### 3. Skip CI for Docs

```bash
git commit -m "Update docs [skip ci]"
```

## 🎓 Best Practices

1. **Always test locally first:** Run `./deploy-backend.sh` before pushing
2. **Use semantic versioning:** Tag releases (v1.0.0, v1.1.0)
3. **Review logs:** Check CloudWatch logs after deployment
4. **Monitor costs:** Set up AWS billing alerts
5. **Separate environments:** Dev, staging, prod stacks
6. **Secret rotation:** Rotate IAM keys every 90 days
7. **Manual approval for prod:** Require review before production deploy

## 📋 Checklist

Before enabling CI/CD:

- [ ] AWS credentials added to GitHub/GitLab secrets
- [ ] IAM user has required permissions
- [ ] Workflow/pipeline file committed to repository
- [ ] Test deployment works locally
- [ ] CloudFormation stack exists
- [ ] S3 buckets created
- [ ] Branch protection rules configured (optional)
- [ ] Notifications configured (optional)

## 🚀 Next Steps

After CI/CD is working:

1. **Add tests:** Unit tests, integration tests
2. **Add linting:** ESLint, Pylint
3. **Add security scanning:** Dependabot, Snyk
4. **Add performance monitoring:** CloudWatch dashboards
5. **Add cost monitoring:** AWS Cost Explorer alerts

---

**Questions?** Check AWS CloudFormation events for detailed error messages.
