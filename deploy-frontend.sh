#!/bin/bash

# Granite Crate Packing Optimizer - Frontend Deployment Script
# Builds React app and deploys to S3 + CloudFront

set -e  # Exit on error

echo "=========================================="
echo "Frontend Deployment to S3 + CloudFront"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}ERROR: AWS CLI not found${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"

# Get Stack outputs
echo ""
echo "Fetching CloudFormation stack outputs..."

STACK_OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name granite-packer-stack \
    --region ap-south-1 \
    --query "Stacks[0].Outputs" \
    --output json)

BUCKET_NAME=$(echo "$STACK_OUTPUTS" | python3 -c "import sys,json; o={x['OutputKey']:x['OutputValue'] for x in json.load(sys.stdin)}; print(o.get('FrontendBucketName',''))")
CLOUDFRONT_URL=$(echo "$STACK_OUTPUTS" | python3 -c "import sys,json; o={x['OutputKey']:x['OutputValue'] for x in json.load(sys.stdin)}; print(o.get('CloudFrontUrl',''))")
API_URL=$(echo "$STACK_OUTPUTS" | python3 -c "import sys,json; o={x['OutputKey']:x['OutputValue'] for x in json.load(sys.stdin)}; print(o.get('ApiUrl',''))")

CLOUDFRONT_ID=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?DomainName==\`$(echo $CLOUDFRONT_URL | sed 's|https://||')\`].Id" \
    --output text 2>/dev/null || echo "")

if [ -z "$BUCKET_NAME" ]; then
    echo -e "${RED}ERROR: Could not find S3 bucket. Deploy backend first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found S3 bucket: ${BUCKET_NAME}${NC}"
echo -e "${GREEN}✓ Found API URL: ${API_URL}${NC}"

# Create or update .env file
echo ""
echo "Configuring environment variables..."

cd frontend

cat > .env.production << EOF
VITE_API_URL=${API_URL}
VITE_ENVIRONMENT=production
EOF

echo -e "${GREEN}✓ Created .env.production${NC}"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo ""
    echo "Installing dependencies..."
    npm install
fi

# Build React app
echo ""
echo "=========================================="
echo "Building React application..."
echo "=========================================="

npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

# Upload to S3
echo ""
echo "=========================================="
echo "Uploading to S3..."
echo "=========================================="

aws s3 sync dist/ s3://${BUCKET_NAME}/ \
    --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "index.html" \
    --exclude "*.map"

# Upload index.html separately with shorter cache
aws s3 cp dist/index.html s3://${BUCKET_NAME}/index.html \
    --cache-control "public, max-age=0, must-revalidate" \
    --content-type "text/html"

echo -e "${GREEN}✓ Upload complete${NC}"

# Invalidate CloudFront cache
echo ""
echo "=========================================="
echo "Invalidating CloudFront cache..."
echo "=========================================="

INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id ${CLOUDFRONT_ID} \
    --paths "/*" \
    --query "Invalidation.Id" \
    --output text)

echo -e "${GREEN}✓ Invalidation created: ${INVALIDATION_ID}${NC}"
echo -e "${YELLOW}Note: Cache invalidation may take 5-15 minutes${NC}"

cd ..

# Test deployment
echo ""
echo "=========================================="
echo "Testing deployment..."
echo "=========================================="

echo -e "${YELLOW}Testing CloudFront endpoint...${NC}"
sleep 5  # Wait a bit for S3/CloudFront sync

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${CLOUDFRONT_URL}")

if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ Frontend is responding (HTTP ${HTTP_CODE})${NC}"
else
    echo -e "${YELLOW}⚠ Frontend returned HTTP ${HTTP_CODE} (may need to wait for cache invalidation)${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Frontend Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo -e "${GREEN}Frontend URL:${NC} ${CLOUDFRONT_URL}"
echo -e "${GREEN}API URL:${NC} ${API_URL}"
echo ""
echo "Open your browser to:"
echo "  ${CLOUDFRONT_URL}"
echo ""
echo "To check invalidation status:"
echo "  aws cloudfront get-invalidation --distribution-id ${CLOUDFRONT_ID} --id ${INVALIDATION_ID}"
echo ""
