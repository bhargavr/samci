"""
Utility functions for packing operations.
"""
from typing import List, Dict, Any
from .models import PackingResult, Container, Placement


def generate_step_by_step(
    result: PackingResult,
    container: Container
) -> List[Dict[str, Any]]:
    """
    Generate human-friendly step-by-step placement instructions.

    Returns:
        List of instruction steps with descriptions
    """
    if not result.placements:
        return [{"step": 1, "description": "No crates to place"}]

    steps = []

    # Sort placements by: z-level, then x, then y (bottom-up, front-to-back, left-to-right)
    sorted_placements = sorted(
        result.placements,
        key=lambda p: (p.position.z, p.position.x, p.position.y)
    )

    current_level = 0
    level_count = 0

    for i, placement in enumerate(sorted_placements):
        step_num = i + 1

        # Check if we've moved to a new height level
        if placement.position.z > current_level:
            current_level = placement.position.z
            level_count += 1

        # Generate position description
        position_desc = _describe_position(placement, container)

        # Generate action description
        if placement.stack_level == 0:
            action = f"Place crate {placement.crate.original_id} (#{placement.crate.instance_num})"
        else:
            action = f"Stack crate {placement.crate.original_id} (#{placement.crate.instance_num})"

        # Rotation info
        rotation_desc = ""
        if placement.rotation.value == "WxL":
            rotation_desc = " (rotated 90°)"

        # Combine description
        description = f"{action} {position_desc}{rotation_desc}"

        steps.append({
            "step": step_num,
            "description": description,
            "crate_id": placement.crate.id,
            "position": placement.position.to_list(),
            "stack_level": placement.stack_level,
            "dimensions": [
                placement.crate.length,
                placement.crate.width,
                placement.crate.height
            ]
        })

    return steps


def _describe_position(placement: Placement, container: Container) -> str:
    """Generate human-readable position description."""
    x, y, z = placement.position.x, placement.position.y, placement.position.z

    # Horizontal position (X-axis: front-to-back)
    x_percent = x / container.length
    if x_percent < 0.1:
        x_desc = "at front"
    elif x_percent < 0.4:
        x_desc = "near front"
    elif x_percent < 0.6:
        x_desc = "at center"
    elif x_percent < 0.9:
        x_desc = "near back"
    else:
        x_desc = "at back"

    # Lateral position (Y-axis: left-to-right)
    y_percent = y / container.width
    if y_percent < 0.1:
        y_desc = "left side"
    elif y_percent < 0.4:
        y_desc = "left-center"
    elif y_percent < 0.6:
        y_desc = "center"
    elif y_percent < 0.9:
        y_desc = "right-center"
    else:
        y_desc = "right side"

    # Vertical position
    if z == 0:
        z_desc = ""
    else:
        z_desc = f" at height {z:.0f}mm"

    return f"{x_desc}, {y_desc}{z_desc}"


def calculate_weight_distribution(
    result: PackingResult,
    container: Container
) -> Dict[str, float]:
    """
    Calculate weight distribution across container sections.

    Returns:
        Dictionary with weight per section
    """
    if not result.placements:
        return {
            "front_left": 0.0,
            "front_right": 0.0,
            "back_left": 0.0,
            "back_right": 0.0
        }

    mid_x = container.length / 2
    mid_y = container.width / 2

    distribution = {
        "front_left": 0.0,
        "front_right": 0.0,
        "back_left": 0.0,
        "back_right": 0.0
    }

    for placement in result.placements:
        # Calculate center of crate
        center_x = placement.position.x + placement.crate.length / 2
        center_y = placement.position.y + placement.crate.width / 2

        # Determine quadrant
        is_back = center_x >= mid_x
        is_right = center_y >= mid_y

        if is_back and is_right:
            distribution["back_right"] += placement.crate.weight
        elif is_back:
            distribution["back_left"] += placement.crate.weight
        elif is_right:
            distribution["front_right"] += placement.crate.weight
        else:
            distribution["front_left"] += placement.crate.weight

    return distribution


def export_to_dict(
    result: PackingResult,
    container: Container
) -> Dict[str, Any]:
    """
    Export packing result to JSON-serializable dictionary.
    """
    placements_data = []
    for placement in result.placements:
        placements_data.append({
            "crate_id": placement.crate.original_id,
            "instance_id": placement.crate.id,
            "instance_num": placement.crate.instance_num,
            "position": placement.position.to_list(),
            "dimensions": [
                placement.crate.length,
                placement.crate.width,
                placement.crate.height
            ],
            "weight": placement.crate.weight,
            "rotation": placement.rotation.value,
            "stack_level": placement.stack_level,
            "stack_id": placement.stack_id
        })

    unpacked_data = [
        {
            "crate_id": crate.original_id,
            "instance_id": crate.id,
            "instance_num": crate.instance_num
        }
        for crate in result.unpacked_crates
    ]

    weight_dist = calculate_weight_distribution(result, container)

    return {
        "utilization_percent": round(result.calculate_utilization(container), 2),
        "weight_utilization": round(result.calculate_weight_utilization(container), 2),
        "total_crates_packed": result.crates_packed,
        "total_weight": round(result.total_weight_used, 2),
        "placements": placements_data,
        "unpacked_crates": unpacked_data,
        "weight_distribution": weight_dist,
        "warnings": result.warnings,
        "steps": generate_step_by_step(result, container)
    }
