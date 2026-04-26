"""
Data models for container packing optimization.
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum


class Rotation(Enum):
    """Rotation options for crate placement."""
    LxW = "LxW"  # Original orientation (length x width)
    WxL = "WxL"  # Rotated 90 degrees (width x length)


@dataclass
class Container:
    """Shipping container specifications."""
    length: float
    width: float
    height: float
    max_weight: float

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height

    @property
    def floor_area(self) -> float:
        return self.length * self.width


@dataclass
class CrateType:
    """Definition of a crate type with constraints."""
    id: str
    length: float
    width: float
    height: float
    weight: float
    quantity: int
    max_stack: int
    can_rotate: bool = True


@dataclass
class Crate:
    """Individual crate instance."""
    id: str
    original_id: str  # Reference to CrateType
    length: float
    width: float
    height: float
    weight: float
    max_stack: int
    can_rotate: bool
    instance_num: int = 0

    @property
    def footprint(self) -> float:
        """Floor area occupied by this crate."""
        return self.length * self.width

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height

    def get_rotated(self) -> 'Crate':
        """Return a copy of this crate rotated 90 degrees."""
        return Crate(
            id=self.id,
            original_id=self.original_id,
            length=self.width,
            width=self.length,
            height=self.height,
            weight=self.weight,
            max_stack=self.max_stack,
            can_rotate=self.can_rotate,
            instance_num=self.instance_num
        )


@dataclass
class Position:
    """3D position in container."""
    x: float
    y: float
    z: float

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z]


@dataclass
class Placement:
    """A placed crate with position and orientation."""
    crate: Crate
    position: Position
    rotation: Rotation
    stack_level: int
    stack_id: Optional[str] = None  # Identifier for stack tower

    @property
    def x_max(self) -> float:
        return self.position.x + self.crate.length

    @property
    def y_max(self) -> float:
        return self.position.y + self.crate.width

    @property
    def z_max(self) -> float:
        return self.position.z + self.crate.height

    def overlaps_xy(self, other: 'Placement') -> bool:
        """Check if two placements overlap on the XY plane."""
        return not (
            self.x_max <= other.position.x or
            other.x_max <= self.position.x or
            self.y_max <= other.position.y or
            other.y_max <= self.position.y
        )

    def can_support(self, other_crate: Crate) -> bool:
        """Check if this placement can support another crate on top."""
        # Top crate must fully fit on bottom crate (no overhang)
        return (
            other_crate.length <= self.crate.length and
            other_crate.width <= self.crate.width
        )


@dataclass
class FreeSpace:
    """Represents a free rectangular space in the container."""
    x: float
    y: float
    z: float
    length: float
    width: float
    height: float

    @property
    def area(self) -> float:
        return self.length * self.width

    def can_fit(self, crate: Crate, tolerance: float = 0.0) -> bool:
        """Check if a crate can fit in this space."""
        return (
            crate.length <= self.length + tolerance and
            crate.width <= self.width + tolerance and
            crate.height <= self.height + tolerance
        )


@dataclass
class PackingResult:
    """Result of packing optimization."""
    placements: List[Placement] = field(default_factory=list)
    unpacked_crates: List[Crate] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def total_volume_used(self) -> float:
        return sum(p.crate.volume for p in self.placements)

    @property
    def total_weight_used(self) -> float:
        return sum(p.crate.weight for p in self.placements)

    @property
    def crates_packed(self) -> int:
        return len(self.placements)

    def calculate_utilization(self, container: Container) -> float:
        """Volume utilization percentage."""
        return (self.total_volume_used / container.volume) * 100

    def calculate_weight_utilization(self, container: Container) -> float:
        """Weight utilization percentage."""
        return (self.total_weight_used / container.max_weight) * 100
