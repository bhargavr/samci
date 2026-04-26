# Container Packing Algorithm - Visual Guide

## Table of Contents
1. [Quick Overview](#quick-overview)
2. [Main Algorithm Flow](#main-algorithm-flow)
3. [Data Structures](#data-structures)
4. [Placement Strategy](#placement-strategy)
5. [Free Space Management](#free-space-management)
6. [Stacking Rules](#stacking-rules)
7. [Safety Checks](#safety-checks)
8. [Examples](#examples)

---

## Quick Overview

### **Algorithm Type**
**Greedy Heuristic + Skyline Method + Free Space Tracking**

### **One-Sentence Summary**
Place largest crates first on the floor, stack when possible, track remaining free spaces, and validate safety constraints.

### **Key Metrics**
- **Speed:** O(n²) - Milliseconds for 50 crates
- **Quality:** 70-80% space utilization
- **Deterministic:** Same input → Same output

---

## Main Algorithm Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    START: OPTIMIZATION                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  1. EXPAND CRATE TYPES       │
        │  • Convert quantities to     │
        │    individual instances      │
        │  • Large×10 → Large_1..10    │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │  2. SORT CRATES              │
        │  • By footprint (desc)       │
        │  • Then by weight (desc)     │
        │  • Largest + heaviest first  │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │  3. INITIALIZE FREE SPACES   │
        │  • Start with full container │
        │  • [(0,0,0) → full dims]     │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │  4. MAIN PACKING LOOP        │◄─────┐
        │  For each crate:             │      │
        │                              │      │
        │  ┌────────────────────────┐  │      │
        │  │ Try Floor Placement    │  │      │
        │  │ (z=0 spaces only)      │  │      │
        │  └────────┬───────────────┘  │      │
        │           │ ✗ Failed          │      │
        │           ▼                   │      │
        │  ┌────────────────────────┐  │      │
        │  │ Try Stacking           │  │      │
        │  │ (on existing crates)   │  │      │
        │  └────────┬───────────────┘  │      │
        │           │ ✗ Failed          │      │
        │           ▼                   │      │
        │  ┌────────────────────────┐  │      │
        │  │ Try Elevated Placement │  │      │
        │  │ (any free space)       │  │      │
        │  └────────┬───────────────┘  │      │
        │           │                   │      │
        │           ├─ ✓ Success        │      │
        │           │                   │      │
        │           ▼                   │      │
        │  ┌────────────────────────┐  │      │
        │  │ Update Free Spaces     │  │      │
        │  │ (Guillotine splits)    │  │      │
        │  └────────────────────────┘  │      │
        │           │                   │      │
        │           ├─ More crates? ────┘      │
        │           │                          │
        └───────────┼──────────────────────────┘
                    │ All done
                    ▼
        ┌──────────────────────────────┐
        │  5. VALIDATE CONSTRAINTS     │
        │  • No overlaps               │
        │  • Within bounds             │
        │  • Weight limit              │
        │  • No overhang               │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │  6. TRANSPORT SAFETY         │
        │  • Check horizontal gaps     │
        │  • Check dimensional mismatch│
        │  • Check loose crates        │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │     RETURN: PACKING RESULT   │
        │  • Placements list           │
        │  • Unpacked crates           │
        │  • Warnings                  │
        │  • Utilization metrics       │
        └──────────────────────────────┘
```

---

## Data Structures

### **1. Container**
```
┌─────────────────────────────────────┐
│          CONTAINER                  │
│  ┌───────────────────────────────┐  │
│  │                               │  │
│  │    Length (X): 5898mm        │  │ Height (Z)
│  │    Width (Y): 2352mm         │  │ 2393mm
│  │    Height (Z): 2393mm        │  │
│  │    Max Weight: 28000kg       │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
│  Coordinate System:                 │
│  • Origin (0,0,0) = front-left-bottom
│  • X-axis = front to back          │
│  • Y-axis = left to right          │
│  • Z-axis = bottom to top          │
└─────────────────────────────────────┘
```

### **2. Crate**
```
┌─────────────────────────┐
│    CRATE PROPERTIES     │
├─────────────────────────┤
│ ID: "Large-Granite_1"   │
│ Length: 1200mm (X)      │
│ Width:  1000mm (Y)      │
│ Height:  800mm (Z)      │
│ Weight: 1200kg          │
│ Max Stack: 2            │ ← How many can stack on this
│ Can Rotate: Yes         │ ← Allow 90° rotation
└─────────────────────────┘

Dimensions:
    ┌──────────── 1200mm ────────────┐
    │                                │
  ──┤   ┌───────────────────┐        │ 1000mm
    │   │                   │  ▲     │
    │   │                   │  │ 800mm
    │   │     CRATE         │  ▼     │
    │   └───────────────────┘        │
    └────────────────────────────────┘
```

### **3. Free Space**
```
Free Space = Available volume for packing

┌─────────────────────────────────┐
│  Position: (x, y, z)            │ ← Bottom-front-left corner
│  Dimensions: (L, W, H)          │
│  Area: L × W                    │ ← For sorting
└─────────────────────────────────┘

Example:
    Z
    ▲
    │     ┌────────────────┐
    │    ╱                ╱│
    │   ╱  FREE SPACE    ╱ │  Height (H)
    │  ╱                ╱  │
    │ ┌────────────────┐   │
    │ │  (x,y,z)       │   │
    │ │                │   ╱
    │ │     Width (W)  │  ╱
    └─┴────────────────┴─╱────────▶ Y
     ╱    Length (L)   ╱
    ╱                 ╱
   ╱─────────────────╱
  X
```

### **4. Placement**
```
Placement = Crate + Position + Orientation

┌──────────────────────────────────┐
│  Crate: <Crate object>           │
│  Position: (x, y, z)             │
│  Rotation: "LxW" or "WxL"        │
│  Stack Level: 0, 1, 2, ...       │
│  Stack ID: "uuid-123..."         │
└──────────────────────────────────┘

Rotation:
  LxW (original):        WxL (90° rotated):
  ┌──────────┐          ┌────────┐
  │          │          │        │
  │  L × W   │          │  W × L │
  │          │          │        │
  └──────────┘          │        │
                        └────────┘
```

---

## Placement Strategy

### **Decision Tree for Each Crate**

```
                    ┌─────────────┐
                    │  New Crate  │
                    └──────┬──────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │  Is floor space available?│
            └──────┬───────────────┬───┘
                   │ YES           │ NO
                   ▼               │
          ┌────────────────┐       │
          │ Place on Floor │       │
          │  (Priority #1) │       │
          └────────────────┘       │
                                   ▼
                    ┌──────────────────────────┐
                    │ Can stack on existing?   │
                    │  • Check max_stack       │
                    │  • Check no overhang     │
                    │  • Check height limit    │
                    └──────┬───────────────┬───┘
                           │ YES           │ NO
                           ▼               │
                  ┌────────────────┐       │
                  │ Stack on Base  │       │
                  │  (Priority #2) │       │
                  └────────────────┘       │
                                           ▼
                            ┌──────────────────────────┐
                            │ Elevated space available?│
                            └──────┬───────────────┬───┘
                                   │ YES           │ NO
                                   ▼               ▼
                          ┌────────────────┐  ┌──────────┐
                          │ Place Elevated │  │ UNPACKED │
                          │  (Priority #3) │  │  (Failed)│
                          └────────────────┘  └──────────┘
```

### **Floor Placement Algorithm**

```python
Input: Crate, Free_Spaces (filtered to z=0)
Output: Placement or None

Step 1: Sort spaces by area (smallest first)
   Why? Use smallest sufficient space to preserve larger spaces

Step 2: For each space:
   ┌─────────────────────────────────┐
   │ Try Original Orientation        │
   │ Does crate fit?                 │
   │  • crate.L + gap ≤ space.L      │
   │  • crate.W + gap ≤ space.W      │
   │  • crate.H + gap ≤ space.H      │
   └────────┬────────────────────────┘
            │ YES → Return placement
            │ NO ↓
   ┌─────────────────────────────────┐
   │ Try Rotated (if allowed)        │
   │ Swap length ↔ width             │
   │ Check fit again                 │
   └────────┬────────────────────────┘
            │ YES → Return placement
            │ NO → Try next space
            ▼
   Return None (no fit found)
```

**Visual Example:**

```
Free Spaces (sorted by area):
1. [1200×1000] = 1,200,000 mm²  ✓ Use this (smallest that fits)
2. [2000×2000] = 4,000,000 mm²
3. [3000×2000] = 6,000,000 mm²

Crate: 1200×1000×800

Fit Check:
  1200 + 10 ≤ 1200? YES (barely fits!)
  1000 + 10 ≤ 1000? YES
  → Place here to preserve larger spaces
```

### **Stacking Algorithm**

```python
Input: Crate, Existing_Placements
Output: Placement or None

Step 1: Group existing placements by stack_id
   stack_1: [base, level1, level2, ...]
   stack_2: [base, level1, ...]
   ...

Step 2: For each existing placement (potential base):
   ┌─────────────────────────────────┐
   │ Check 1: Max Stack Height       │
   │ • Get stack from stack_id       │
   │ • Count levels in stack         │
   │ • Compare to base.max_stack     │
   └────────┬────────────────────────┘
            │ PASS
            ▼
   ┌─────────────────────────────────┐
   │ Check 2: No Overhang            │
   │ • crate.L ≤ base.crate.L        │
   │ • crate.W ≤ base.crate.W        │
   │ (Top must fit fully on base)    │
   └────────┬────────────────────────┘
            │ PASS
            ▼
   ┌─────────────────────────────────┐
   │ Check 3: Height Limit           │
   │ • new_z = base.z_max            │
   │ • new_z + crate.H ≤ container.H │
   └────────┬────────────────────────┘
            │ PASS
            ▼
   Return Placement(
      position=(base.x, base.y, new_z),
      stack_level=base.level + 1,
      stack_id=base.stack_id
   )
```

**No-Overhang Rule Visualization:**

```
✓ VALID STACK (no overhang):
    ┌──────┐
    │ Top  │  1000×800
    │      │
    ├──────┤
    │ Base │  1200×1000
    │      │
    └──────┘

✗ INVALID STACK (overhang):
    ┌────────┐
    │  Top   │  1400×1000 (too wide!)
    ├──┬──┬──┤
    │  │Base │  overhang →
    │  │    │
    └──┴────┴──┘
         ↑
      overhang
```

**Max Stack Example:**

```
Base crate has max_stack = 3

Level 2  ┌──────┐  ← 3rd crate (level=2) ✓ ALLOWED
         │      │
Level 1  ├──────┤  ← 2nd crate (level=1)
         │      │
Level 0  ├──────┤  ← Base crate (level=0)
         │      │
Floor    └──────┘

Level 3  [ ? ]      ← 4th crate? ✗ DENIED (exceeds max_stack=3)
```

---

## Free Space Management

### **Guillotine Cut Method**

When a crate is placed, split intersecting free spaces.

**Before Placement:**
```
┌────────────────────────────────┐
│                                │
│                                │
│     Free Space                 │
│     2000 × 2000 × 2000         │
│                                │
│                                │
└────────────────────────────────┘
```

**After Placing Crate (1200×1000×800) at (0,0,0):**
```
        ┌────── Right Split ──────┐
        │                         │
    ┌───┼────┬─── Top Split ──────┤
    │   │    │                    │
    │ C │ B  │         R          │  B = Back Split
    │ R │ A  │         I          │  (y > crate.y_max)
    │ A │ C  │         G          │
    │ T │ K  │         H          │  R = Right Split
    │ E │    │         T          │  (x > crate.x_max)
    │   │    │                    │
    └───┴────┴────────────────────┘  T = Top Split
                                     (z > crate.z_max)
```

**Code Logic:**
```python
def split_space(space, placed_crate):
    splits = []
    
    # Right split (along X-axis)
    if placed_crate.x_max < space.x_max:
        splits.append(
            FreeSpace(
                x = placed_crate.x_max,
                y = space.y,
                z = space.z,
                L = space.x_max - placed_crate.x_max,
                W = space.width,
                H = space.height
            )
        )
    
    # Back split (along Y-axis)
    if placed_crate.y_max < space.y_max:
        splits.append(
            FreeSpace(
                x = space.x,
                y = placed_crate.y_max,
                z = space.z,
                L = placed_crate.x_max - space.x,  # Only up to crate
                W = space.y_max - placed_crate.y_max,
                H = space.height
            )
        )
    
    # Top split (along Z-axis)
    if placed_crate.z_max < space.z_max:
        splits.append(
            FreeSpace(
                x = space.x,
                y = space.y,
                z = placed_crate.z_max,
                L = space.length,  # Keep full length
                W = space.width,   # Keep full width
                H = space.z_max - placed_crate.z_max
            )
        )
    
    return splits
```

### **Free Space Updates**

```
Step 1: Check each existing free space
   ┌─────────────────────────────┐
   │ Does it intersect placement?│
   └────────┬──────────┬─────────┘
            │ YES      │ NO
            ▼          ▼
   ┌─────────────┐  ┌─────────┐
   │ Split Space │  │ Keep It │
   │ (Guillotine)│  │         │
   └─────────────┘  └─────────┘

Step 2: Remove tiny spaces
   ┌─────────────────────────────┐
   │ Filter out spaces where:    │
   │  • length < 100mm OR        │
   │  • width < 100mm OR         │
   │  • height < 100mm           │
   └─────────────────────────────┘
   (Too small to be useful)

Step 3: Return updated list
```

**Example Sequence:**

```
Initial:
  Free_Spaces = [A: (0,0,0)→(5898,2352,2393)]

Place Crate_1 at (0,0,0) [1200×1000×800]:
  A intersects → Split into:
    A_right: (1200,0,0)→(4698,2352,2393)
    A_back:  (0,1000,0)→(1200,1352,2393)
    A_top:   (0,0,800)→(5898,2352,1593)
  
  Free_Spaces = [A_right, A_back, A_top]

Place Crate_2 at (0,1000,0) [1200×1000×800]:
  A_back intersects → Split
  A_right unchanged
  A_top unchanged
  
  Free_Spaces = [A_right, A_back_right, A_back_top, A_top]

...continues...
```

---

## Stacking Rules

### **Rule 1: Max Stack Height**

```
max_stack = N means at most N crates total in stack
(including the base)

Example: max_stack = 3

┌──────┐  Level 2 (3rd crate) ✓
├──────┤  Level 1 (2nd crate) ✓
├──────┤  Level 0 (base)      ✓
└──────┘  FLOOR

Cannot add level 3 (would be 4th crate)
```

### **Rule 2: No Overhang**

```
Top crate must be fully supported by base

✓ VALID:
  Top View:
  ┌──────────────┐
  │  ┌────────┐  │  Base = 1200×1000
  │  │  Top   │  │  Top  = 1000×800
  │  │ 1000×  │  │  ✓ Top ⊆ Base
  │  │  800   │  │
  │  └────────┘  │
  └──────────────┘

✗ INVALID:
  Top View:
  ┌──────────────┐
  │            ┌─┼──┐  Base = 1000×800
  │    Base    │ │  │  Top  = 1200×1000
  │            └─┼──┘  ✗ Top overhangs
  └──────────────┘
                 ↑
              overhang
```

**Code Check:**
```python
def can_stack_on_top(top_crate, base_placement):
    return (
        top_crate.length <= base_placement.crate.length AND
        top_crate.width <= base_placement.crate.width
    )
```

### **Rule 3: Weight Limit**

```
Track running total weight

total_weight = Σ(crate.weight for all placed crates)

If total_weight > container.max_weight:
   - Remove last placement
   - Add crate to unpacked list
   - Stop packing
```

### **Rule 4: Container Bounds**

```
For every placement:
  x_max = x + crate.length ≤ container.length
  y_max = y + crate.width  ≤ container.width
  z_max = z + crate.height ≤ container.height
```

---

## Safety Checks

### **1. Horizontal Gap Detection**

Detect gaps between adjacent crates that could allow movement.

```
Algorithm:
1. Group placements by height level (round to 100mm)
2. For each level:
   a. Sort by X, check gaps along X-axis
   b. Sort by Y, check gaps along Y-axis
3. Warn if gap > 50mm
```

**Visual Example - Level 800mm:**

```
Top View:
                Gap!
          ┌────┐   ┌────┐
    Y=0   │ A  │   │ B  │  200mm gap between A and B
          └────┘   └────┘
          x=1200   x=2400

    X-axis: ──────────────────▶

Crate A: x=[1200-2200] (1000mm long)
Crate B: x=[2400-3400] (1000mm long)
Gap = 2400 - 2200 = 200mm ⚠ UNSAFE (>50mm)
```

**Y-Overlap Check:**
```
For gap to matter, crates must be in same row

Crate A: y=[0-800]
Crate B: y=[0-800]

Y-overlap = NOT(A.y_max ≤ B.y OR B.y_max ≤ A.y)
          = NOT(800 ≤ 0 OR 800 ≤ 0)
          = NOT(False OR False)
          = True ✓ They're in same row, gap matters!
```

### **2. Dimensional Mismatch Detection**

Detect when smaller crates on larger bases create edge gaps.

```
Stack Analysis:
1. Group placements by stack_id
2. For each stack, sort by Z (bottom to top)
3. For each adjacent pair (base, top):
   - Calculate length_diff = base.L - top.L
   - Calculate width_diff = base.W - top.W
   - If diff > 50mm → Warning
```

**Visual Example:**

```
Side View:                   Top View (looking down):

┌─────────┐  800mm          ┌──────────────┐
│   Top   │                 │  ┌────────┐  │
│ 1000×800│                 │  │  Top   │  │ ← 200mm gap
├─────────┤  800mm          │  │1000×800│  │    on right edge
│  Base   │                 │  └────────┘  │
│1200×1000│                 │   Base       │
└─────────┘  Floor          │   1200×1000  │
                            └──────────────┘
                                   ↑
                              200mm gap on back

Differences:
- Length: 1200 - 1000 = 200mm ⚠ WARNING
- Width:  1000 - 800  = 200mm ⚠ WARNING

Edge gaps allow crates to shift during transport!
```

### **3. Loose Crate Detection**

Check if floor crates have enough adjacent support.

```
Algorithm:
1. For each floor crate:
   a. Count adjacent crates (within 50mm on each side)
   b. Check all 4 sides: left, right, front, back
2. If adjacent_count < 2:
   → Warning: minimal contact, may shift

Visual:
┌───┐     ┌───┐
│ A │     │ B │  Crate B is isolated (0 contacts)
└───┘     └───┘  ⚠ HIGH RISK

┌───┬───┐
│ A │ B │        Crate B has 1 contact (with A)
└───┴───┘        ⚠ MEDIUM RISK

┌───┬───┐
│ A │ B │        Crate B has 2 contacts (A and C)
├───┼───┤        ✓ ACCEPTABLE
│ C │ D │
└───┴───┘
```

---

## Examples

### **Example 1: Simple 2-Crate Placement**

**Input:**
```
Container: 3000×2000×2000 mm
Crates:
  - Large_1: 1200×1000×800 mm
  - Large_2: 1200×1000×800 mm
```

**Step-by-Step:**

```
STEP 1: Initialize
  Free_Spaces = [(0,0,0) → (3000,2000,2000)]

STEP 2: Place Large_1
  Floor placement at (0,0,0)
  
  Before:                   After:
  ┌──────────────┐         ┌────┬─────────┐
  │              │         │ L1 │         │
  │     Free     │         ├────┤  Free   │
  │              │         │    │         │
  └──────────────┘         └────┴─────────┘
  
  New Free_Spaces:
    - (1200,0,0) → (1800,2000,2000)  [Right]
    - (0,1000,0) → (1200,1000,2000)  [Back]
    - (0,0,800) → (3000,2000,1200)   [Top]

STEP 3: Place Large_2
  Floor placement at (0,1000,0)
  
  Top View:
  ┌────┬─────────┐
  │ L1 │         │
  ├────┤  Free   │
  │ L2 │         │
  └────┴─────────┘
  
  Final placements:
    - Large_1: (0, 0, 0)
    - Large_2: (0, 1000, 0)
  
  Utilization:
    Used = 2 × (1200×1000×800) = 1,920,000 mm³
    Total = 3000×2000×2000 = 12,000,000 mm³
    Efficiency = 16%
```

### **Example 2: Stacking**

**Input:**
```
Container: 3000×2000×2000 mm
Crates:
  - Large_1: 1200×1000×800, max_stack=3
  - Large_2: 1200×1000×800
  - Medium_1: 1000×800×700
```

**Execution:**

```
STEP 1: Place Large_1 on floor
  Position: (0,0,0)
  Stack: level=0, stack_id="abc-123"

STEP 2: Place Large_2 - Floor or Stack?
  Check floor: ✓ Space available at (1200,0,0)
  Choose floor (Priority #1)
  Position: (1200,0,0)
  Stack: level=0, stack_id="def-456"

STEP 3: Place Medium_1
  Check floor: Space at (2400,0,0) but too small
  Check stack on Large_1:
    ✓ max_stack check: 1 < 3
    ✓ no-overhang: 1000≤1200, 800≤1000
    ✓ height: 800+700=1500 ≤ 2000
  Choose stack!
  Position: (0,0,800)
  Stack: level=1, stack_id="abc-123"

Side View:
      ┌──────┐
  700 │ Med1 │  Level 1
      ├──────┤
  800 │Large1│  Level 0 (base)
      └──────┴─────┐
                800│Large2│
                   └──────┘

Final:
  - Large_1: (0,0,0) level=0
  - Large_2: (1200,0,0) level=0
  - Medium_1: (0,0,800) level=1 [stacked on Large_1]
```

### **Example 3: Gap Detection**

**Scenario:**
```
Level 800mm has these placements:

Top View:
      0    1200  2400  3600
  0   ┌────┐┌───┐┌───┐┌───┐
      │ L1 ││M1 ││M2 ││M3 │
 1000 ├────┤└───┘└───┘└───┘
      │ L2 │
 2000 └────┘

Crates:
- L1: Large (1200×1000) at x=[0-1200], y=[0-1000]
- L2: Large (1200×1000) at x=[0-1200], y=[1000-2000]
- M1: Medium (1000×800) at x=[1200-2200], y=[0-800]
- M2: Medium (1000×800) at x=[2400-3400], y=[0-800]
- M3: Medium (1000×800) at x=[3600-4600], y=[0-800]
```

**Gap Analysis:**

```
Sort by X: [L1, L2, M1, M2, M3]

Check M1 → M2:
  M1.x_max = 2200
  M2.x = 2400
  Gap = 2400 - 2200 = 200mm
  Y-overlap? M1.y=[0-800], M2.y=[0-800] → YES
  ⚠ WARNING: 200mm gap at height 800mm

Check M2 → M3:
  M2.x_max = 3400
  M3.x = 3600
  Gap = 3600 - 3400 = 200mm
  Y-overlap? YES
  ⚠ WARNING: 200mm gap at height 800mm
```

**Dimensional Mismatch:**

```
Stack 1 (L1 base):
  Base: 1200×1000
  Top: 1000×800 (if M1 were stacked on L1)
  Diff: 200mm × 200mm
  ⚠ WARNING: Edge gaps from size mismatch
```

---

## Algorithm Properties

### **Strengths** ✓

1. **Fast:** O(n²) complexity, milliseconds for typical loads
2. **Deterministic:** Same input always produces same output
3. **Practical:** Handles real-world constraints (weight, overhang, stacking)
4. **Safe:** Transport safety checks prevent dangerous configurations
5. **Transparent:** Easy to understand and debug

### **Weaknesses** ✗

1. **Not Optimal:** Greedy approach doesn't guarantee best solution
2. **No Backtracking:** Once placed, crates never move
3. **Fragmentation:** Many different sizes can create unusable gaps
4. **Local Decisions:** Each placement doesn't consider future crates

### **When It Works Best**

- ✓ Moderate crate count (10-100)
- ✓ Similar-sized crates
- ✓ Real-time requirements (fast response needed)
- ✓ Practical constraints matter (safety, physics)

### **When It Struggles**

- ✗ Extreme heterogeneity (many wildly different sizes)
- ✗ Need for global optimum (academic benchmarks)
- ✗ Very large problems (1000+ crates)
- ✗ Irregular shapes (non-rectangular)

---

## Complexity Analysis

### **Time Complexity**

```
n = number of crates
m = average free spaces (typically O(n))

Operations:
1. Expand: O(n)
2. Sort: O(n log n)
3. Main loop: O(n) iterations
   - Floor placement: O(m) = O(n)
   - Stacking: O(n)
   - Space update: O(m) = O(n)
   Per iteration: O(n)
4. Validation: O(n²) for overlap checks
5. Safety: O(n²) for gap checks

Total: O(n² log n) dominated by O(n²)
```

**Practical Performance:**
- 10 crates: ~100 ops → <1ms
- 50 crates: ~2500 ops → ~5ms
- 100 crates: ~10,000 ops → ~20ms

### **Space Complexity**

```
Storage:
- Crates: O(n)
- Placements: O(n)
- Free spaces: O(n) worst case
- Stacks: O(n)

Total: O(n)
```

---

## Comparison with Other Algorithms

| Algorithm | Time | Quality | Pros | Cons |
|-----------|------|---------|------|------|
| **This (Greedy+Skyline)** | O(n²) | 70-80% | Fast, practical | Not optimal |
| **Brute Force** | O(n!) | 100% | Optimal | Impossible for n>15 |
| **Genetic Algorithm** | O(k·p·n) | 85-95% | Good quality | Complex, slow |
| **Branch & Bound** | O(2ⁿ) | 100% | Optimal | Slow for n>50 |
| **Random/Monte Carlo** | O(n) | 40-60% | Very fast | Poor quality |

**Legend:**
- k = generations, p = population size, n = crates
- Quality = average space utilization %

---

## Key Takeaways

### **Core Idea**
Place largest crates first, track free spaces, stack when safe, validate constraints.

### **Why Greedy?**
Balances speed and quality for practical applications.

### **Why Skyline/Free Space?**
Efficiently tracks available volumes without explicit 3D grid.

### **Why Safety Checks?**
Real-world logistics requires stable, secure loads - not just maximum density.

### **Trade-offs**
Sacrifices global optimality for speed and practicality.

---

## Summary Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  PACKING ALGORITHM SUMMARY                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INPUT: Container + Crates                                  │
│     ↓                                                       │
│  SORT: Largest → Smallest (by footprint + weight)          │
│     ↓                                                       │
│  INITIALIZE: Free_Spaces = [Full Container]                │
│     ↓                                                       │
│  LOOP: For each crate                                      │
│     ├─ Try Floor (z=0 only)                                │
│     ├─ Try Stack (on existing)                             │
│     └─ Try Elevated (any space)                            │
│     ↓                                                       │
│  UPDATE: Split free spaces (Guillotine)                    │
│     ↓                                                       │
│  VALIDATE: Overlaps, Bounds, Weight, Overhang              │
│     ↓                                                       │
│  SAFETY: Gaps, Mismatches, Loose Crates                    │
│     ↓                                                       │
│  OUTPUT: Placements + Warnings + Metrics                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  COMPLEXITY: O(n²) time, O(n) space                        │
│  QUALITY: 70-80% utilization                               │
│  SPEED: Milliseconds for 50 crates                         │
└─────────────────────────────────────────────────────────────┘
```

---

**End of Visual Guide**

For detailed code implementation and mathematical proofs, see `ALGORITHM_EXPLAINED.md`.
