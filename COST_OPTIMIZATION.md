# AWS Cost Optimization Guide

Comprehensive guide to minimize AWS costs for the Granite Crate Packing Optimizer.

## 💰 Current Cost Breakdown

### MVP/Low Usage (~10K requests/month)

| Service | Monthly Cost | Annual Cost | % of Total |
|---------|--------------|-------------|------------|
| Lambda (after free tier) | $0.00 | $0.00 | 0% |
| API Gateway (HTTP API) | $0.01 | $0.12 | 0.5% |
| S3 Storage (Frontend) | $0.03 | $0.36 | 1.5% |
| S3 Requests | $0.02 | $0.24 | 1% |
| CloudFront | $4.25 | $51.00 | 85% |
| CloudWatch Logs | $0.50 | $6.00 | 10% |
| S3 (Results - Optional) | $0.03 | $0.36 | 1.5% |
| **Total (with free tier)** | **$2-3** | **$24-36** | **100%** |
| **Total (without free tier)** | **$5** | **$60** | **100%** |

### Medium Usage (~100K requests/month)

| Service | Monthly Cost | Notes |
|---------|--------------|-------|
| Lambda | $0.20 | 100K requests × 2s avg × 1024MB |
| API Gateway | $0.10 | $1 per 1M requests |
| CloudFront | $8.50 | 100 GB transfer |
| S3 + CloudWatch | $1.20 | Storage + logs |
| **Total** | **$10** | |

### High Usage (~1M requests/month)

| Service | Monthly Cost | Notes |
|---------|--------------|-------|
| Lambda | $2.00 | 1M requests |
| API Gateway | $1.00 | HTTP API pricing |
| CloudFront | $50.00 | 500 GB transfer |
| S3 + CloudWatch | $2.00 | Increased storage |
| **Total** | **$55** | |

## 🎯 Cost Optimization Strategies

### 1. Lambda Optimization

#### Current Configuration
```yaml
MemorySize: 1024
Timeout: 15
```

#### Optimization Options

**Option A: Reduce Memory (if performance allows)**
```yaml
MemorySize: 512  # 50% cost reduction
Timeout: 20      # Allow more time
```

**Savings:** 50% on Lambda costs ($0.10 → $0.05 per 100K requests)

**Trade-off:** Slower execution (may timeout on large loads)

**Test first:**
```bash
# Update template.yaml, then:
sam build --use-container
sam deploy

# Test performance
time curl -X POST $API_URL/optimize -d @test-input.json
```

**Option B: Optimize Code Size**

**Current package size:** ~50 MB

**Reduce to <10 MB:**
```bash
# Use Lambda-optimized dependencies
cd backend

# Remove unnecessary packages
pip install --target=./package \
    fastapi==0.115.0 \
    pydantic==2.9.0 \
    mangum==0.17.0 \
    --no-deps  # Skip unnecessary dependencies

# Only include required files
zip -r function.zip package/ \
    packing/ \
    api/ \
    lambda_handler.py
```

**Benefits:**
- Faster cold starts (50% reduction)
- Lower deployment time
- Better performance

**Option C: Increase Memory for Faster Execution**

If optimization <50ms is critical:
```yaml
MemorySize: 1536  # More CPU power
Timeout: 10
```

**Result:** Faster execution = lower cost (if runtime < 1s)

### 2. CloudFront Optimization (Biggest Cost)

CloudFront is 85% of costs. Key optimization target.

#### Strategy A: Enable Aggressive Caching

**Current:** 1-day cache for assets, no cache for index.html

**Optimize:**
```yaml
# In template.yaml
DefaultCacheBehavior:
  DefaultTTL: 604800      # 7 days (from 1 day)
  MaxTTL: 2592000         # 30 days (from 1 year)
  MinTTL: 86400           # 1 day minimum
```

**Savings:** Reduces origin requests by 70%

**Trade-off:** Users may see cached content longer

**Invalidation strategy:**
```bash
# Invalidate on deployment only
aws cloudfront create-invalidation \
    --distribution-id $DIST_ID \
    --paths "/index.html" "/assets/*"
```

#### Strategy B: Use Price Class 100 (Default)

**Current:** PriceClass_100 (North America + Europe)

**Already optimized!** This is the cheapest option.

**Don't change to PriceClass_All** (adds +50% cost for global edge locations)

#### Strategy C: Compress Assets

**Current:** Compression enabled

**Verify:**
```yaml
Compress: true  # ✅ Already enabled
```

**Additional optimization:**
```bash
# Pre-compress with Brotli (better than gzip)
cd frontend
npm install --save-dev vite-plugin-compression

# vite.config.js
import compression from 'vite-plugin-compression'

export default {
  plugins: [
    compression({
      algorithm: 'brotliCompress',
      ext: '.br'
    })
  ]
}
```

**Savings:** 20-30% smaller assets = 20-30% less CloudFront transfer cost

#### Strategy D: Reduce Bundle Size

**Current bundle size:** ~800 KB (gzipped)

**Optimize to <300 KB:**
```bash
cd frontend

# 1. Analyze bundle
npm run build -- --report

# 2. Remove unused dependencies
npm uninstall lodash moment  # Use native alternatives

# 3. Tree-shake Three.js
# Import only what you need
import { BoxGeometry, Mesh } from 'three'  # Not: import * as THREE

# 4. Code splitting
# Lazy load components
const Viewer3D = React.lazy(() => import('./components/Viewer3D'))

# 5. Optimize images (if any)
npm install --save-dev vite-plugin-imagemin
```

**Savings:** 60% smaller = 60% less CloudFront cost ($4.25 → $1.70)

### 3. API Gateway Optimization

**Current:** HTTP API (cheapest option already)

**Don't switch to REST API** (3x more expensive)

**Optimization:** Enable caching (for GET endpoints only)

```yaml
# In template.yaml - add cache for /examples endpoint
Events:
  ExampleEndpoint:
    Type: HttpApi
    Properties:
      Path: /examples/standard-container
      Method: GET
      # Add caching (not available in HTTP API v1)
      # Use CloudFront caching instead
```

**Better approach:** Cache example data in CloudFront:
```javascript
// Serve example.json as static file
// Move examples to S3 instead of Lambda
```

**Savings:** Eliminates Lambda + API Gateway cost for example requests

### 4. S3 Optimization

#### Strategy A: Lifecycle Policies (Already Enabled)

**Current:**
```yaml
LifecycleConfiguration:
  Rules:
    - ExpirationInDays: 7  # Auto-delete after 7 days
```

**Optimize further:**
```yaml
LifecycleConfiguration:
  Rules:
    - Id: DeleteOldResults
      Status: Enabled
      ExpirationInDays: 1  # Delete after 1 day (if acceptable)

    - Id: TransitionToIA
      Status: Enabled
      Transitions:
        - Days: 30
          StorageClass: STANDARD_IA  # Cheaper storage after 30 days
```

**Savings:** 50% on long-term storage costs

#### Strategy B: Intelligent Tiering

For results bucket:
```yaml
StorageClass: INTELLIGENT_TIERING
```

**Auto-moves** infrequently accessed objects to cheaper storage.

**Savings:** 40-70% on storage costs (automatic)

### 5. CloudWatch Logs Optimization

**Current:** 7-day retention

**Already optimized!** Don't increase unless debugging.

**Further optimization:**
```yaml
RetentionInDays: 3  # Reduce to 3 days (if acceptable)
```

**Savings:** 40% reduction ($0.50 → $0.30)

**Trade-off:** Less log history for debugging

**Alternative:** Export logs to S3 for long-term storage (cheaper)
```bash
aws logs create-export-task \
    --log-group-name /aws/lambda/granite-packer-api-dev \
    --from 1640000000000 \
    --to 1640086400000 \
    --destination s3://my-logs-bucket
```

### 6. Remove Optional Resources

**Results bucket:** If you don't use it, delete it.

```yaml
# Comment out in template.yaml
# ResultsBucket:
#   Type: AWS::S3::Bucket
#   ...
```

**Savings:** $0.03-0.10/month (small but eliminates unused resource)

## 📊 Free Tier Benefits

### Always Free (No Expiration)

| Service | Free Tier | Value |
|---------|-----------|-------|
| Lambda Requests | 1M requests/month | $0.20 |
| Lambda Compute | 400K GB-seconds/month | $7.20 |
| API Gateway | 1M HTTP API calls/month | $1.00 |
| CloudFront | 1 TB transfer out/month | $85.00 |
| CloudWatch Logs | 5 GB ingestion/month | $2.50 |

**Total free tier value:** ~$100/month for first year

### 12-Month Free Tier

| Service | Free Tier | Duration |
|---------|-----------|----------|
| S3 Storage | 5 GB | 12 months |
| S3 Requests | 20K GET, 2K PUT | 12 months |

**Strategy:** Maximize free tier usage in year 1, then optimize

## 🎯 Cost Reduction Roadmap

### Immediate Actions (Save 50%)

1. ✅ **Use HTTP API** (not REST API) - already done
2. ✅ **Enable CloudFront caching** - already done
3. ✅ **Use PriceClass_100** - already done
4. ✅ **7-day log retention** - already done
5. ⚠️ **Reduce frontend bundle size** - do this!

**Estimated savings:** $2.50 → $1.25/month

### Short-term Actions (Next Sprint)

1. **Bundle size optimization** (biggest impact)
   - Target: <300 KB gzipped
   - Savings: 60% CloudFront cost

2. **Serve static example data**
   - Move `/examples` to S3
   - Savings: Eliminate Lambda calls for examples

3. **Implement Brotli compression**
   - Better compression than gzip
   - Savings: 20-30% transfer reduction

**Estimated savings:** $1.25 → $0.75/month

### Long-term Optimization

1. **Custom domain with Route 53**
   - Cost: +$0.50/month for hosted zone
   - Benefit: Professional URL
   - ROI: Only if business value justifies cost

2. **Reserved capacity** (only if high traffic)
   - Lambda provisioned concurrency
   - Cost: +$10/month
   - Benefit: Zero cold starts
   - ROI: Only for >100K requests/month

3. **CloudFront Functions** (edge computing)
   - Process at edge instead of Lambda
   - Cost: $0.10 per 1M invocations
   - Benefit: Lower latency + cost
   - ROI: Only for simple operations

## 🚨 Cost Alerts

Set up billing alerts to avoid surprises:

```bash
# Create SNS topic for alerts
aws sns create-topic --name billing-alerts

# Subscribe to email
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:123456789:billing-alerts \
    --protocol email \
    --notification-endpoint your-email@example.com

# Create billing alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "Monthly Bill > $10" \
    --alarm-description "Alert if monthly bill exceeds $10" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 21600 \
    --evaluation-periods 1 \
    --threshold 10.0 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions arn:aws:sns:us-east-1:123456789:billing-alerts
```

**Recommended thresholds:**
- Warning: $5/month
- Critical: $10/month
- Emergency: $20/month

## 📈 Cost Monitoring

### View Current Costs

```bash
# Get month-to-date costs
aws ce get-cost-and-usage \
    --time-period Start=$(date -u -d '1 month ago' +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
    --granularity MONTHLY \
    --metrics "UnblendedCost" \
    --group-by Type=SERVICE

# Get daily costs
aws ce get-cost-and-usage \
    --time-period Start=$(date -u -d '7 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
    --granularity DAILY \
    --metrics "UnblendedCost"
```

### Cost Explorer Dashboard

1. Go to **AWS Console** → **Cost Explorer**
2. Filter by tag: `Application=granite-packer`
3. Group by: Service
4. View: Last 6 months

### Budget Setup

**AWS Console:**
1. Go to **Billing** → **Budgets**
2. Create budget
3. Budget type: Cost budget
4. Budget amount: $10/month
5. Alert threshold: 80% ($8)

**CLI:**
```bash
aws budgets create-budget \
    --account-id 123456789 \
    --budget file://budget.json \
    --notifications-with-subscribers file://notifications.json
```

## 💡 Cost Optimization Checklist

### Before Deployment

- [ ] Remove unused dependencies
- [ ] Minimize Lambda package size
- [ ] Enable compression
- [ ] Set appropriate Lambda memory
- [ ] Use HTTP API (not REST API)
- [ ] Enable CloudFront caching
- [ ] Set log retention to 7 days
- [ ] Add S3 lifecycle policies

### After Deployment

- [ ] Set up billing alerts
- [ ] Monitor costs weekly
- [ ] Review CloudWatch logs (check for errors causing retries)
- [ ] Analyze CloudFront cache hit rate
- [ ] Check Lambda execution duration (optimize if >2s)
- [ ] Review unused resources

### Monthly Review

- [ ] Check Cost Explorer
- [ ] Identify cost spikes
- [ ] Analyze request patterns
- [ ] Optimize based on usage
- [ ] Update budgets if needed

## 🎓 Cost Optimization Best Practices

1. **Right-size resources:** Don't over-provision Lambda memory
2. **Cache aggressively:** CloudFront caching reduces origin costs
3. **Use serverless:** Avoid always-on resources (EC2, RDS)
4. **Monitor continuously:** Set up alerts and dashboards
5. **Delete unused resources:** Results buckets, old logs, test stacks
6. **Leverage free tier:** Maximize usage in first 12 months
7. **Batch operations:** Combine multiple Lambda invocations if possible
8. **Optimize cold starts:** Smaller packages = faster cold starts = lower costs

## 📉 Cost Comparison

### Serverless vs. Traditional

**Traditional Architecture (EC2 + RDS):**
- t3.small EC2 instance: $15/month (24/7)
- db.t3.micro RDS: $15/month (24/7)
- ALB: $20/month
- EBS storage: $5/month
- **Total: $55/month minimum** (even with zero traffic)

**Serverless Architecture (Current):**
- Lambda: $0 (with free tier)
- API Gateway: $0.01
- S3 + CloudFront: $4.30
- **Total: $2-5/month** (scales with usage)

**Savings: 90-95% at MVP scale**

## 🚀 Summary

**Current Cost:** $2-5/month (MVP usage)

**After Optimization:** $0.75-2/month (with bundle optimization)

**At Scale (1M requests):** $55/month

**Conclusion:** Serverless architecture is highly cost-effective for MVP and scales economically.

**Next Steps:**
1. Implement bundle size reduction
2. Set up billing alerts
3. Monitor costs weekly
4. Optimize based on actual usage patterns

---

**Questions?** Review AWS Cost Explorer for detailed breakdowns.
