"""
Constraint validation for packing operations.
"""
from typing import List, Dict, Tuple
from .models import Container, Placement, PackingResult


class ConstraintChecker:
    """Validates hard and soft constraints for packing."""

    def __init__(self, container: Container):
        self.container = container

    def check_all_constraints(self, result: PackingResult) -> List[str]:
        """
        Check all constraints and return list of violations/warnings.
        """
        warnings = []

        # Hard constraints
        hard_violations = self._check_hard_constraints(result)
        if hard_violations:
            warnings.extend([f"[CRITICAL] {v}" for v in hard_violations])

        # Soft constraints
        soft_warnings = self._check_soft_constraints(result)
        warnings.extend(soft_warnings)

        return warnings

    def _check_hard_constraints(self, result: PackingResult) -> List[str]:
        """Check critical constraints that must not be violated."""
        violations = []

        # Check container boundaries
        for placement in result.placements:
            if placement.x_max > self.container.length:
                violations.append(
                    f"Crate {placement.crate.id} exceeds container length"
                )
            if placement.y_max > self.container.width:
                violations.append(
                    f"Crate {placement.crate.id} exceeds container width"
                )
            if placement.z_max > self.container.height:
                violations.append(
                    f"Crate {placement.crate.id} exceeds container height"
                )

        # Check weight limit
        if result.total_weight_used > self.container.max_weight:
            violations.append(
                f"Total weight {result.total_weight_used:.0f} kg exceeds "
                f"container limit {self.container.max_weight:.0f} kg"
            )

        # Check for overlaps on same level
        for i, p1 in enumerate(result.placements):
            for p2 in result.placements[i + 1:]:
                if p1.position.z == p2.position.z and p1.overlaps_xy(p2):
                    violations.append(
                        f"Crates {p1.crate.id} and {p2.crate.id} overlap"
                    )

        # Check stacking constraints
        stack_violations = self._check_stack_constraints(result)
        violations.extend(stack_violations)

        return violations

    def _check_stack_constraints(self, result: PackingResult) -> List[str]:
        """Validate stacking rules."""
        violations = []

        # Group placements by stack
        stacks: Dict[str, List[Placement]] = {}
        for placement in result.placements:
            if placement.stack_id:
                if placement.stack_id not in stacks:
                    stacks[placement.stack_id] = []
                stacks[placement.stack_id].append(placement)

        for stack_id, stack_placements in stacks.items():
            # Sort by height
            stack_placements.sort(key=lambda p: p.position.z)

            # Check each level
            for i in range(len(stack_placements) - 1):
                bottom = stack_placements[i]
                top = stack_placements[i + 1]

                # Check overhang (top must fully sit on bottom)
                if not bottom.can_support(top.crate):
                    violations.append(
                        f"Stack {stack_id}: Top crate {top.crate.id} "
                        f"overhangs bottom crate {bottom.crate.id}"
                    )

                # Check vertical alignment
                if top.position.z != bottom.z_max:
                    violations.append(
                        f"Stack {stack_id}: Gap between crates "
                        f"{bottom.crate.id} and {top.crate.id}"
                    )

            # Check max stack height
            bottom_crate = stack_placements[0].crate
            if len(stack_placements) > bottom_crate.max_stack:
                violations.append(
                    f"Stack {stack_id}: Exceeds max stack height of "
                    f"{bottom_crate.max_stack} (has {len(stack_placements)})"
                )

        return violations

    def _check_soft_constraints(self, result: PackingResult) -> List[str]:
        """Check optimization goals and best practices."""
        warnings = []

        # Weight distribution
        weight_warning = self._check_weight_distribution(result)
        if weight_warning:
            warnings.append(weight_warning)

        # Stability warnings
        stability_warnings = self._check_stability(result)
        warnings.extend(stability_warnings)

        return warnings

    def _check_weight_distribution(self, result: PackingResult) -> str:
        """Check if weight is evenly distributed."""
        if not result.placements:
            return ""

        # Split container into left/right halves
        mid_x = self.container.length / 2
        left_weight = sum(
            p.crate.weight for p in result.placements
            if p.position.x + p.crate.length / 2 < mid_x
        )
        right_weight = sum(
            p.crate.weight for p in result.placements
            if p.position.x + p.crate.length / 2 >= mid_x
        )

        total_weight = left_weight + right_weight
        if total_weight == 0:
            return ""

        # Calculate imbalance
        imbalance = abs(left_weight - right_weight) / total_weight * 100

        if imbalance > 20:
            heavier_side = "left" if left_weight > right_weight else "right"
            return (
                f"Weight imbalance: {imbalance:.1f}% heavier on {heavier_side} side "
                f"(left: {left_weight:.0f} kg, right: {right_weight:.0f} kg)"
            )

        return ""

    def _check_stability(self, result: PackingResult) -> List[str]:
        """Check for potential stability issues."""
        warnings = []

        # Check for tall stacks with small base
        stacks: Dict[str, List[Placement]] = {}
        for placement in result.placements:
            if placement.stack_id:
                if placement.stack_id not in stacks:
                    stacks[placement.stack_id] = []
                stacks[placement.stack_id].append(placement)

        for stack_id, stack_placements in stacks.items():
            if len(stack_placements) < 2:
                continue

            # Sort by height
            stack_placements.sort(key=lambda p: p.position.z)
            base = stack_placements[0]
            top = stack_placements[-1]

            # Check if top is significantly smaller than base
            base_area = base.crate.footprint
            top_area = top.crate.footprint

            if top_area < base_area * 0.5:
                warnings.append(
                    f"Stack {stack_id}: Top crate is less than 50% of base area "
                    f"(may be unstable)"
                )

        return warnings
