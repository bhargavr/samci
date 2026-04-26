"""
Core packing algorithm using heuristic approach.
"""
from typing import List, Dict, Tuple, Optional
import uuid
from .models import (
    Container, CrateType, Crate, Position, Placement,
    FreeSpace, PackingResult, Rotation
)
from .constraints import ConstraintChecker


class ContainerPacker:
    """
    Implements custom heuristic packing algorithm for granite crates.

    Strategy:
    1. Expand crate types into individual instances
    2. Sort by size (largest first) and weight
    3. Floor packing using skyline/free-space approach
    4. Stack crates where possible
    5. Fill gaps with smaller crates
    """

    def __init__(self, container: Container, gap_tolerance: float = 10.0):
        """
        Args:
            container: Container specifications
            gap_tolerance: Allowed gap in mm for fitting crates (default 1cm for tight packing)

        Note: Reduced gap tolerance minimizes movement during transport.
        Tight packing prevents crates from shifting on the road.
        """
        self.container = container
        self.gap_tolerance = gap_tolerance
        self.constraint_checker = ConstraintChecker(container)

    def optimize(self, crate_types: List[CrateType]) -> PackingResult:
        """
        Main optimization routine.

        Returns:
            PackingResult with placements and warnings
        """
        result = PackingResult()

        # Step 1: Expand crates
        crates = self._expand_crates(crate_types)
        if not crates:
            result.warnings.append("No crates to pack")
            return result

        # Step 2: Sort crates (largest first, then by weight)
        sorted_crates = self._sort_crates(crates)

        # Step 3: Initialize free spaces (start with entire container floor)
        free_spaces = [
            FreeSpace(
                x=0, y=0, z=0,
                length=self.container.length,
                width=self.container.width,
                height=self.container.height
            )
        ]

        # Step 4: Pack crates iteratively
        for crate in sorted_crates:
            placement = self._find_best_placement(
                crate, free_spaces, result.placements
            )

            if placement:
                result.placements.append(placement)
                # Update free spaces
                free_spaces = self._update_free_spaces(
                    free_spaces, placement
                )
            else:
                # Could not fit this crate
                result.unpacked_crates.append(crate)

            # Check weight limit
            if result.total_weight_used > self.container.max_weight:
                # Remove last placement
                result.placements.pop()
                result.unpacked_crates.append(crate)
                result.warnings.append("Weight limit reached")
                break

        # Step 5: Validate constraints
        constraint_warnings = self.constraint_checker.check_all_constraints(result)
        result.warnings.extend(constraint_warnings)

        # Step 6: Check for transport safety (gaps between crates)
        transport_warnings = self._check_transport_safety(result.placements)
        result.warnings.extend(transport_warnings)

        # Add unpacked crates warning
        if result.unpacked_crates:
            result.warnings.append(
                f"{len(result.unpacked_crates)} crates could not be packed"
            )

        return result

    def _expand_crates(self, crate_types: List[CrateType]) -> List[Crate]:
        """Convert crate types with quantities into individual crate instances."""
        crates = []
        for crate_type in crate_types:
            for i in range(crate_type.quantity):
                crate = Crate(
                    id=f"{crate_type.id}_{i+1}",
                    original_id=crate_type.id,
                    length=crate_type.length,
                    width=crate_type.width,
                    height=crate_type.height,
                    weight=crate_type.weight,
                    max_stack=crate_type.max_stack,
                    can_rotate=crate_type.can_rotate,
                    instance_num=i + 1
                )
                crates.append(crate)
        return crates

    def _sort_crates(self, crates: List[Crate]) -> List[Crate]:
        """
        Sort crates for optimal packing.
        Priority: largest footprint first, then heaviest.
        """
        return sorted(
            crates,
            key=lambda c: (c.footprint, c.weight),
            reverse=True
        )

    def _find_best_placement(
        self,
        crate: Crate,
        free_spaces: List[FreeSpace],
        existing_placements: List[Placement]
    ) -> Optional[Placement]:
        """
        Find the best position to place a crate.

        Strategy:
        1. Try floor placement first (maximize floor coverage)
        2. If floor is full, try stacking
        3. Try both orientations if rotation allowed
        """
        # Option 1: Try floor placement first
        floor_placement = self._try_floor_placement(crate, free_spaces, floor_only=True)
        if floor_placement and self._is_valid_placement(floor_placement, existing_placements):
            return floor_placement

        # Option 2: Try stacking on existing placements
        stack_placement = self._try_stacking(crate, existing_placements)
        if stack_placement and self._is_valid_placement(stack_placement, existing_placements):
            return stack_placement

        # Option 3: Try any elevated placement
        elevated_placement = self._try_floor_placement(crate, free_spaces, floor_only=False)
        if elevated_placement and self._is_valid_placement(elevated_placement, existing_placements):
            return elevated_placement

        return None

    def _is_valid_placement(
        self,
        placement: Placement,
        existing_placements: List[Placement]
    ) -> bool:
        """Check if placement is valid (within container bounds and no overlaps)."""
        # Check container boundaries
        if placement.x_max > self.container.length:
            return False
        if placement.y_max > self.container.width:
            return False
        if placement.z_max > self.container.height:
            return False

        # Check for overlaps with existing placements
        for existing in existing_placements:
            if self._placements_overlap(placement, existing):
                return False

        return True

    def _placements_overlap(self, p1: Placement, p2: Placement) -> bool:
        """Check if two placements overlap in 3D space."""
        return not (
            p1.x_max <= p2.position.x or
            p2.x_max <= p1.position.x or
            p1.y_max <= p2.position.y or
            p2.y_max <= p1.position.y or
            p1.z_max <= p2.position.z or
            p2.z_max <= p1.position.z
        )

    def _try_stacking(
        self,
        crate: Crate,
        existing_placements: List[Placement]
    ) -> Optional[Placement]:
        """
        Attempt to stack crate on top of existing placements.
        """
        # Group placements by stack to track stack heights
        stacks: Dict[str, List[Placement]] = {}
        for p in existing_placements:
            if p.stack_id:
                if p.stack_id not in stacks:
                    stacks[p.stack_id] = []
                stacks[p.stack_id].append(p)

        # Try stacking on each existing placement
        for base_placement in existing_placements:
            # Check if we can stack on this placement
            if not self._can_stack_on(crate, base_placement, stacks):
                continue

            # Try original orientation
            if self._can_place_on_top(crate, base_placement):
                new_z = base_placement.z_max
                if new_z + crate.height <= self.container.height:
                    stack_id = base_placement.stack_id or str(uuid.uuid4())
                    stack_level = base_placement.stack_level + 1

                    return Placement(
                        crate=crate,
                        position=Position(
                            base_placement.position.x,
                            base_placement.position.y,
                            new_z
                        ),
                        rotation=Rotation.LxW,
                        stack_level=stack_level,
                        stack_id=stack_id
                    )

            # Try rotated orientation if allowed
            if crate.can_rotate:
                rotated = crate.get_rotated()
                if self._can_place_on_top(rotated, base_placement):
                    new_z = base_placement.z_max
                    if new_z + rotated.height <= self.container.height:
                        stack_id = base_placement.stack_id or str(uuid.uuid4())
                        stack_level = base_placement.stack_level + 1

                        return Placement(
                            crate=rotated,
                            position=Position(
                                base_placement.position.x,
                                base_placement.position.y,
                                new_z
                            ),
                            rotation=Rotation.WxL,
                            stack_level=stack_level,
                            stack_id=stack_id
                        )

        return None

    def _can_stack_on(
        self,
        crate: Crate,
        base_placement: Placement,
        stacks: Dict[str, List[Placement]]
    ) -> bool:
        """Check if stacking is allowed based on max_stack constraint."""
        if not base_placement.stack_id:
            # This is a floor placement, can start a stack
            return True

        stack = stacks.get(base_placement.stack_id, [])
        # Count how many crates are already in this stack
        current_height = len(stack)

        # The base crate determines max stack height
        base_crate = min(stack, key=lambda p: p.position.z).crate
        return current_height < base_crate.max_stack

    def _can_place_on_top(self, crate: Crate, base: Placement) -> bool:
        """Check if crate can physically sit on top of base (no overhang)."""
        return base.can_support(crate)

    def _try_floor_placement(
        self,
        crate: Crate,
        free_spaces: List[FreeSpace],
        floor_only: bool = False
    ) -> Optional[Placement]:
        """
        Try to place crate in available free space.
        Uses first-fit strategy with smallest sufficient space.

        Args:
            crate: Crate to place
            free_spaces: Available spaces
            floor_only: If True, only consider floor-level spaces (z=0)
        """
        # Filter spaces
        if floor_only:
            spaces = [s for s in free_spaces if s.z == 0]
        else:
            spaces = free_spaces

        # Sort by area (smallest first), then by z (lower first)
        sorted_spaces = sorted(spaces, key=lambda s: (s.area, s.z))

        for space in sorted_spaces:
            # Try original orientation
            if space.can_fit(crate, self.gap_tolerance):
                stack_id = str(uuid.uuid4()) if space.z == 0 else None
                stack_level = 0 if space.z == 0 else 0
                return Placement(
                    crate=crate,
                    position=Position(space.x, space.y, space.z),
                    rotation=Rotation.LxW,
                    stack_level=stack_level,
                    stack_id=stack_id
                )

            # Try rotated orientation
            if crate.can_rotate:
                rotated = crate.get_rotated()
                if space.can_fit(rotated, self.gap_tolerance):
                    stack_id = str(uuid.uuid4()) if space.z == 0 else None
                    stack_level = 0 if space.z == 0 else 0
                    return Placement(
                        crate=rotated,
                        position=Position(space.x, space.y, space.z),
                        rotation=Rotation.WxL,
                        stack_level=stack_level,
                        stack_id=stack_id
                    )

        return None

    def _update_free_spaces(
        self,
        free_spaces: List[FreeSpace],
        placement: Placement
    ) -> List[FreeSpace]:
        """
        Update free space list after placing a crate.
        Uses simple guillotine cut approach.
        """
        new_spaces = []

        for space in free_spaces:
            # Check if placement intersects with this space
            if not self._spaces_intersect(space, placement):
                # No intersection, keep the space
                new_spaces.append(space)
            else:
                # Split the space around the placement
                splits = self._split_space(space, placement)
                new_spaces.extend(splits)

        # Remove spaces that are too small to be useful (< 100mm in any dimension)
        new_spaces = [
            s for s in new_spaces
            if s.length >= 100 and s.width >= 100 and s.height >= 100
        ]

        # Merge overlapping spaces (simple approach: keep all for now)
        return new_spaces

    def _spaces_intersect(self, space: FreeSpace, placement: Placement) -> bool:
        """Check if a free space intersects with a placement."""
        return not (
            space.x + space.length <= placement.position.x or
            placement.x_max <= space.x or
            space.y + space.width <= placement.position.y or
            placement.y_max <= space.y or
            space.z + space.height <= placement.position.z or
            placement.z_max <= space.z
        )

    def _split_space(
        self,
        space: FreeSpace,
        placement: Placement
    ) -> List[FreeSpace]:
        """
        Split a free space around a placement using guillotine cuts.
        Creates up to 6 new spaces (left, right, front, back, top, bottom).
        """
        splits = []

        # Right split (along X axis)
        if placement.x_max < space.x + space.length:
            splits.append(FreeSpace(
                x=placement.x_max,
                y=space.y,
                z=space.z,
                length=space.x + space.length - placement.x_max,
                width=space.width,
                height=space.height
            ))

        # Back split (along Y axis)
        if placement.y_max < space.y + space.width:
            splits.append(FreeSpace(
                x=space.x,
                y=placement.y_max,
                z=space.z,
                length=placement.x_max - space.x,
                width=space.y + space.width - placement.y_max,
                height=space.height
            ))

        # Top split (along Z axis) - only if not on floor
        if placement.z_max < space.z + space.height:
            splits.append(FreeSpace(
                x=space.x,
                y=space.y,
                z=placement.z_max,
                length=space.length,
                width=space.width,
                height=space.z + space.height - placement.z_max
            ))

        return splits

    def _check_transport_safety(self, placements: List[Placement]) -> List[str]:
        """
        Check for gaps between crates that could cause movement during transport.
        Gaps larger than 50mm are safety concerns.
        Checks all levels, not just floor.
        """
        warnings = []
        max_safe_gap = 50.0  # mm - maximum safe gap between crates

        # Group crates by height level (rounded to nearest 100mm to group stacks)
        levels = {}
        for p in placements:
            level_key = round(p.position.z / 100) * 100
            if level_key not in levels:
                levels[level_key] = []
            levels[level_key].append(p)

        # Check each level separately
        for level_z, crates_at_level in levels.items():
            if not crates_at_level:
                continue

            # Sort by position for gap detection
            crates_x = sorted(crates_at_level, key=lambda p: p.position.x)

            # Check gaps along X-axis (front-to-back)
            gaps_x = []
            for i in range(len(crates_x) - 1):
                current = crates_x[i]
                next_crate = crates_x[i + 1]

                # Check if they're in the same row (Y-axis overlap)
                y_overlap = not (current.y_max <= next_crate.position.y or
                               next_crate.y_max <= current.position.y)

                if y_overlap:
                    gap = next_crate.position.x - current.x_max
                    if gap > max_safe_gap:
                        gaps_x.append((gap, level_z))

            # Check gaps along Y-axis (left-to-right)
            crates_y = sorted(crates_at_level, key=lambda p: p.position.y)
            gaps_y = []

            for i in range(len(crates_y) - 1):
                current = crates_y[i]
                next_crate = crates_y[i + 1]

                # Check if they're in the same column (X-axis overlap)
                x_overlap = not (current.x_max <= next_crate.position.x or
                               next_crate.x_max <= current.position.x)

                if x_overlap:
                    gap = next_crate.position.y - current.y_max
                    if gap > max_safe_gap:
                        gaps_y.append((gap, level_z))

            # Add warnings for significant gaps at this level
            if gaps_x:
                max_gap_x = max(gap for gap, _ in gaps_x)
                level_desc = "floor level" if level_z == 0 else f"height {level_z:.0f}mm"
                warnings.append(
                    f"⚠ TRANSPORT SAFETY: Gap of {max_gap_x:.0f}mm detected at {level_desc} "
                    f"(front-to-back). Recommend securing with straps or dunnage to prevent movement."
                )

            if gaps_y:
                max_gap_y = max(gap for gap, _ in gaps_y)
                level_desc = "floor level" if level_z == 0 else f"height {level_z:.0f}mm"
                warnings.append(
                    f"⚠ TRANSPORT SAFETY: Gap of {max_gap_y:.0f}mm detected at {level_desc} "
                    f"(left-to-right). Recommend securing with straps or dunnage to prevent movement."
                )

        # Check for dimensional mismatches in stacks (smaller on top of larger)
        stacks = {}
        for p in placements:
            if p.stack_id:
                if p.stack_id not in stacks:
                    stacks[p.stack_id] = []
                stacks[p.stack_id].append(p)

        for stack_id, stack_placements in stacks.items():
            sorted_stack = sorted(stack_placements, key=lambda p: p.position.z)
            for i in range(len(sorted_stack) - 1):
                base = sorted_stack[i]
                top = sorted_stack[i + 1]

                # Check if top crate is smaller than base
                length_diff = base.crate.length - top.crate.length
                width_diff = base.crate.width - top.crate.width

                if length_diff > max_safe_gap or width_diff > max_safe_gap:
                    warnings.append(
                        f"⚠ TRANSPORT SAFETY: Crate {top.crate.id} (level {top.stack_level}) is "
                        f"{max(length_diff, width_diff):.0f}mm smaller than base crate, creating edge gaps. "
                        f"Recommend securing or using filler material."
                    )

        # Check for loose crates at floor level (not touching any other crate on at least 2 sides)
        floor_crates = [p for p in placements if p.position.z == 0]
        for placement in floor_crates:
            adjacent_count = 0

            for other in floor_crates:
                if other == placement:
                    continue

                # Check if adjacent (within 50mm)
                # Right side
                if abs(other.position.x - placement.x_max) < max_safe_gap:
                    if not (other.y_max <= placement.position.y or
                           placement.y_max <= other.position.y):
                        adjacent_count += 1

                # Left side
                if abs(placement.position.x - other.x_max) < max_safe_gap:
                    if not (other.y_max <= placement.position.y or
                           placement.y_max <= other.position.y):
                        adjacent_count += 1

                # Front side
                if abs(other.position.y - placement.y_max) < max_safe_gap:
                    if not (other.x_max <= placement.position.x or
                           placement.x_max <= other.position.x):
                        adjacent_count += 1

                # Back side
                if abs(placement.position.y - other.y_max) < max_safe_gap:
                    if not (other.x_max <= placement.position.x or
                           placement.x_max <= other.position.x):
                        adjacent_count += 1

            if adjacent_count < 2 and len(floor_crates) > 1:
                warnings.append(
                    f"⚠ TRANSPORT SAFETY: Crate {placement.crate.id} has minimal contact with "
                    f"adjacent crates. Recommend additional securing or repositioning."
                )

        return warnings
