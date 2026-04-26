"""
FastAPI application for container packing optimization.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packing.models import Container, CrateType
from packing.packer import ContainerPacker
from packing.utils import export_to_dict


app = FastAPI(
    title="Granite Crate Packing Optimizer",
    description="Optimizes placement of granite crates in shipping containers",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ContainerInput(BaseModel):
    length: float = Field(..., gt=0, description="Container length in mm")
    width: float = Field(..., gt=0, description="Container width in mm")
    height: float = Field(..., gt=0, description="Container height in mm")
    max_weight: float = Field(..., gt=0, description="Max weight capacity in kg")


class CrateInput(BaseModel):
    id: str = Field(..., description="Crate type identifier")
    length: float = Field(..., gt=0, description="Crate length in mm")
    width: float = Field(..., gt=0, description="Crate width in mm")
    height: float = Field(..., gt=0, description="Crate height in mm")
    weight: float = Field(..., gt=0, description="Crate weight in kg")
    quantity: int = Field(..., gt=0, description="Number of this crate type")
    max_stack: int = Field(..., gt=0, le=10, description="Max stack height")
    can_rotate: bool = Field(True, description="Allow 90-degree rotation")


class OptimizeRequest(BaseModel):
    container: ContainerInput
    crates: List[CrateInput]
    gap_tolerance: Optional[float] = Field(
        50.0,
        ge=0,
        le=200,
        description="Gap tolerance in mm (default: 50mm)"
    )


class OptimizeResponse(BaseModel):
    utilization_percent: float
    weight_utilization: float
    total_crates_packed: int
    total_weight: float
    placements: List[dict]
    unpacked_crates: List[dict]
    weight_distribution: dict
    warnings: List[str]
    steps: List[dict]


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Granite Crate Packing Optimizer",
        "status": "operational",
        "version": "1.0.0"
    }


@app.post("/optimize", response_model=OptimizeResponse)
async def optimize_packing(request: OptimizeRequest):
    """
    Optimize crate packing in container.

    Returns:
        Optimized packing plan with placements and utilization metrics
    """
    try:
        # Convert input models to domain models
        container = Container(
            length=request.container.length,
            width=request.container.width,
            height=request.container.height,
            max_weight=request.container.max_weight
        )

        crate_types = [
            CrateType(
                id=crate.id,
                length=crate.length,
                width=crate.width,
                height=crate.height,
                weight=crate.weight,
                quantity=crate.quantity,
                max_stack=crate.max_stack,
                can_rotate=crate.can_rotate
            )
            for crate in request.crates
        ]

        # Run optimization
        packer = ContainerPacker(
            container=container,
            gap_tolerance=request.gap_tolerance
        )
        result = packer.optimize(crate_types)

        # Export to response format
        response_data = export_to_dict(result, container)

        return OptimizeResponse(**response_data)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )


@app.get("/examples/standard-container")
async def get_standard_container_example():
    """
    Get example input for a standard 20ft container.
    """
    return {
        "container": {
            "length": 5898,
            "width": 2352,
            "height": 2393,
            "max_weight": 28000
        },
        "crates": [
            {
                "id": "Large-Granite",
                "length": 1200,
                "width": 1000,
                "height": 800,
                "weight": 1200,
                "quantity": 10,
                "max_stack": 2,
                "can_rotate": True
            },
            {
                "id": "Medium-Granite",
                "length": 1000,
                "width": 800,
                "height": 700,
                "weight": 900,
                "quantity": 20,
                "max_stack": 3,
                "can_rotate": True
            },
            {
                "id": "Small-Granite",
                "length": 800,
                "width": 600,
                "height": 500,
                "weight": 500,
                "quantity": 15,
                "max_stack": 4,
                "can_rotate": True
            }
        ],
        "gap_tolerance": 50.0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
