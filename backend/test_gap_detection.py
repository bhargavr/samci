from packing.packer import ContainerPacker
from packing.models import Container, CrateType

container = Container(length=5898, width=2352, height=2393, max_weight=28000)
crate_types = [
    CrateType(id="Large", length=1200, width=1000, height=800, weight=1200, quantity=10, max_stack=2, can_rotate=True),
    CrateType(id="Medium", length=1000, width=800, height=700, weight=900, quantity=20, max_stack=3, can_rotate=True),
]

packer = ContainerPacker(container, gap_tolerance=10.0)
result = packer.optimize(crate_types)

# Manual gap check for level 800
level_800 = [p for p in result.placements if 750 < p.position.z < 850]
crates_x = sorted(level_800, key=lambda p: p.position.x)

print(f"=== Level 800: {len(crates_x)} crates ===\n")

max_safe_gap = 50.0
gaps_found = []

for i in range(len(crates_x) - 1):
    current = crates_x[i]
    next_crate = crates_x[i + 1]

    # Check Y overlap
    y_overlap = not (current.y_max <= next_crate.position.y or next_crate.y_max <= current.position.y)

    gap = next_crate.position.x - current.x_max

    print(f"{i+1}. {current.crate.id:12s} x=[{current.position.x:4d}-{current.x_max:4d}] y=[{current.position.y:4d}-{current.y_max:4d}]")
    print(f"   -> {next_crate.crate.id:12s} x=[{next_crate.position.x:4d}-{next_crate.x_max:4d}] y=[{next_crate.position.y:4d}-{next_crate.y_max:4d}]")
    print(f"   Y-overlap: {y_overlap}, Gap: {gap}mm", end="")

    if y_overlap and gap > max_safe_gap:
        print(f" ⚠ UNSAFE GAP!")
        gaps_found.append(gap)
    else:
        print()
    print()

print(f"\n=== Summary ===")
print(f"Unsafe gaps found: {len(gaps_found)}")
if gaps_found:
    print(f"Max gap: {max(gaps_found)}mm")

print(f"\n=== Warnings from packer: {len(result.warnings)} ===")
for w in result.warnings:
    if "TRANSPORT" in w:
        print(f"  {w}")
