"""
AWS Lambda handler for FastAPI application using Mangum.
"""
import os
from mangum import Mangum
from api.main import app

# Strip the API Gateway stage prefix from rawPath so FastAPI routes match.
# HTTP API named stages (e.g. "dev") include the stage in rawPath ("/dev/path").
_stage = os.environ.get("ENVIRONMENT", "dev")
handler = Mangum(app, lifespan="off", api_gateway_base_path=f"/{_stage}")
