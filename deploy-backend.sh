#!/bin/bash

# Granite Crate Packing Optimizer - Backend Deployment Script
# Deploys FastAPI backend to AWS Lambda using SAM

set -e  # Exit on error

echo "=========================================="
echo "Backend Deployment to AWS Lambda"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}ERROR: AWS CLI not found. Please install it first.${NC}"
    echo "Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check SAM CLI
if ! command -v sam &> /dev/null; then
    echo -e "${RED}ERROR: AWS SAM CLI not found. Please install it first.${NC}"
    echo "Install: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}ERROR: AWS credentials not configured.${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"

# Get environment parameter
ENVIRONMENT="${1:-dev}"
echo -e "${YELLOW}Deploying to environment: ${ENVIRONMENT}${NC}"

# Prepare Lambda requirements
echo ""
echo "=========================================="
echo "Preparing Lambda dependencies..."
echo "=========================================="

cd backend

# Copy Lambda-specific requirements
if [ -f "requirements-lambda.txt" ]; then
    cp requirements-lambda.txt requirements.txt
    echo -e "${GREEN}✓ Using Lambda-optimized requirements${NC}"
else
    echo -e "${YELLOW}Warning: requirements-lambda.txt not found, using requirements.txt${NC}"
fi

cd ..

# Build SAM application
echo ""
echo "=========================================="
echo "Building SAM application..."
echo "=========================================="

sam build \
    --use-container \
    --cached \
    --parallel

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

# Deploy SAM application
echo ""
echo "=========================================="
echo "Deploying to AWS..."
echo "=========================================="

# First time deployment (guided)
if [ ! -f "samconfig.toml" ]; then
    echo -e "${YELLOW}First time deployment detected. Running guided mode...${NC}"
    sam deploy \
        --guided \
        --parameter-overrides "Environment=${ENVIRONMENT}"
else
    # Subsequent deployments
    sam deploy \
        --parameter-overrides "Environment=${ENVIRONMENT}" \
        --no-confirm-changeset
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Deployment successful${NC}"
else
    echo -e "${RED}✗ Deployment failed${NC}"
    exit 1
fi

# Get outputs
echo ""
echo "=========================================="
echo "Deployment Outputs"
echo "=========================================="

API_URL=$(aws cloudformation describe-stacks \
    --stack-name granite-packer-stack \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
    --output text)

FUNCTION_NAME=$(aws cloudformation describe-stacks \
    --stack-name granite-packer-stack \
    --query "Stacks[0].Outputs[?OutputKey=='FunctionName'].OutputValue" \
    --output text)

CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
    --stack-name granite-packer-stack \
    --query "Stacks[0].Outputs[?OutputKey=='CloudFrontUrl'].OutputValue" \
    --output text)

echo ""
echo -e "${GREEN}API Endpoint:${NC} ${API_URL}"
echo -e "${GREEN}Lambda Function:${NC} ${FUNCTION_NAME}"
echo -e "${GREEN}CloudFront URL:${NC} ${CLOUDFRONT_URL}"

# Test API endpoint
echo ""
echo "=========================================="
echo "Testing API..."
echo "=========================================="

echo -e "${YELLOW}Testing health endpoint...${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/")

if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ API is responding (HTTP ${HTTP_CODE})${NC}"
else
    echo -e "${RED}✗ API returned HTTP ${HTTP_CODE}${NC}"
fi

# Save outputs to file
echo ""
echo "Saving outputs to deployment-outputs.json..."
aws cloudformation describe-stacks \
    --stack-name granite-packer-stack \
    --query "Stacks[0].Outputs" \
    --output json > deployment-outputs.json

echo -e "${GREEN}✓ Outputs saved to deployment-outputs.json${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update frontend/.env with API_URL: ${API_URL}"
echo "2. Deploy frontend: ./deploy-frontend.sh"
echo ""
echo "To view logs:"
echo "  aws logs tail /aws/lambda/${FUNCTION_NAME} --follow"
echo ""
echo "To test API:"
echo "  curl ${API_URL}/"
echo ""
