"""
Example script to test the packing algorithm without running the API server.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from packing.models import Container, CrateType
from packing.packer import ContainerPacker
from packing.utils import export_to_dict
import json


def test_basic_packing():
    """Test basic packing scenario."""
    print("=" * 60)
    print("Testing Basic Packing Scenario")
    print("=" * 60)

    # Define container (standard 20ft container)
    container = Container(
        length=5898,
        width=2352,
        height=2393,
        max_weight=28000
    )

    print(f"\nContainer: {container.length}mm x {container.width}mm x {container.height}mm")
    print(f"Max Weight: {container.max_weight} kg")

    # Define crate types
    crate_types = [
        CrateType(
            id="Large-Granite",
            length=1200,
            width=1000,
            height=800,
            weight=1200,
            quantity=10,
            max_stack=2,
            can_rotate=True
        ),
        CrateType(
            id="Medium-Granite",
            length=1000,
            width=800,
            height=700,
            weight=900,
            quantity=20,
            max_stack=3,
            can_rotate=True
        ),
        CrateType(
            id="Small-Granite",
            length=800,
            width=600,
            height=500,
            weight=500,
            quantity=15,
            max_stack=4,
            can_rotate=True
        )
    ]

    print("\nCrate Types:")
    for ct in crate_types:
        print(f"  - {ct.id}: {ct.length}x{ct.width}x{ct.height}mm, "
              f"{ct.weight}kg, qty={ct.quantity}, max_stack={ct.max_stack}")

    # Run optimization
    print("\n" + "-" * 60)
    print("Running optimization...")
    print("-" * 60)

    packer = ContainerPacker(container=container, gap_tolerance=50.0)
    result = packer.optimize(crate_types)

    # Export results
    output = export_to_dict(result, container)

    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nSpace Utilization: {output['utilization_percent']:.1f}%")
    print(f"Weight Utilization: {output['weight_utilization']:.1f}%")
    print(f"Total Crates Packed: {output['total_crates_packed']}")
    print(f"Total Weight: {output['total_weight']:.0f} kg")

    if output['unpacked_crates']:
        print(f"\nUnpacked Crates: {len(output['unpacked_crates'])}")
        for crate in output['unpacked_crates'][:5]:  # Show first 5
            print(f"  - {crate['crate_id']} #{crate['instance_num']}")

    # Weight distribution
    print("\nWeight Distribution:")
    wd = output['weight_distribution']
    print(f"  Front Left:  {wd['front_left']:.0f} kg")
    print(f"  Front Right: {wd['front_right']:.0f} kg")
    print(f"  Back Left:   {wd['back_left']:.0f} kg")
    print(f"  Back Right:  {wd['back_right']:.0f} kg")

    # Warnings
    if output['warnings']:
        print("\nWarnings:")
        for warning in output['warnings']:
            print(f"  ⚠ {warning}")

    # Sample placements
    print("\nSample Placements (first 5):")
    for placement in output['placements'][:5]:
        pos = placement['position']
        dims = placement['dimensions']
        print(f"  - {placement['crate_id']} #{placement['instance_num']}: "
              f"pos=[{pos[0]:.0f}, {pos[1]:.0f}, {pos[2]:.0f}], "
              f"dims=[{dims[0]:.0f}x{dims[1]:.0f}x{dims[2]:.0f}], "
              f"stack_level={placement['stack_level']}")

    # Sample steps
    print("\nSample Steps (first 5):")
    for step in output['steps'][:5]:
        print(f"  Step {step['step']}: {step['description']}")

    # Save to file
    output_file = "test_output.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nFull output saved to: {output_file}")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


def test_tight_fit():
    """Test scenario with tight container."""
    print("\n\n" + "=" * 60)
    print("Testing Tight Fit Scenario")
    print("=" * 60)

    # Smaller container
    container = Container(
        length=3000,
        width=2000,
        height=2000,
        max_weight=15000
    )

    crate_types = [
        CrateType(
            id="Heavy-Slab",
            length=1500,
            width=1000,
            height=800,
            weight=1500,
            quantity=8,
            max_stack=2,
            can_rotate=False  # Cannot rotate
        )
    ]

    packer = ContainerPacker(container=container, gap_tolerance=20.0)
    result = packer.optimize(crate_types)
    output = export_to_dict(result, container)

    print(f"\nSpace Utilization: {output['utilization_percent']:.1f}%")
    print(f"Weight Utilization: {output['weight_utilization']:.1f}%")
    print(f"Crates Packed: {output['total_crates_packed']} / {sum(ct.quantity for ct in crate_types)}")

    if output['warnings']:
        print("\nWarnings:")
        for warning in output['warnings']:
            print(f"  ⚠ {warning}")


if __name__ == "__main__":
    test_basic_packing()
    test_tight_fit()
