# SAMCI Brand Identity Guide

Official brand guidelines for SAMCI - Container Optimization Platform

---

## 🎯 Brand Essence

**SAMCI** is an industrial SaaS platform for container packing optimization.

**Brand Personality:**
- Strong & Industrial
- Precise & Engineering-Grade
- Intelligent & Data-Driven
- Practical & Operational
- Modern & Professional

**Not:** Playful, consumer-facing, overly futuristic, or startup-trendy

---

## 🔤 Brand Name

### Primary Name
**SAMCI** (pronounced: SAM-see)

### Tagline
**"Precision at Scale"**

**Alternative Taglines:**
- "Where Every Millimeter Counts"
- "Optimize Every Container. Every Time."
- "Master the Load"
- "Industrial Packing Intelligence"

### Name Meaning

**As Acronym:**
- **S**mart **A**utomated **M**odular **C**ontainer **I**ntelligence

**As Brand Word:**
Strong, industrial name that evokes precision engineering and reliability.

---

## 🎨 Color Palette

### Primary Colors

**Industrial Steel Blue**
- **Hex:** `#1E3A5F`
- **RGB:** 30, 58, 95
- **Usage:** Primary brand color, headers, logo
- **Meaning:** Shipping containers, industrial machinery, trust

**Charcoal Iron**
- **Hex:** `#2C3E50`
- **RGB:** 44, 62, 80
- **Usage:** Text, secondary UI elements
- **Meaning:** Industrial metal, engineering precision

### Accent Colors

**Safety Orange**
- **Hex:** `#E67E22`
- **RGB:** 230, 126, 34
- **Usage:** CTAs, alerts, highlights, primary actions
- **Meaning:** Industrial safety equipment, high visibility, urgency

**Mint Efficiency**
- **Hex:** `#2ECC71`
- **RGB:** 46, 204, 113
- **Usage:** Success states, optimization indicators
- **Meaning:** Green light, operational success, efficiency

### Supporting Colors

**Concrete Gray**
- **Hex:** `#7F8C8D`
- **RGB:** 127, 140, 141
- **Usage:** Borders, dividers, disabled states

**Steel Blue Light**
- **Hex:** `#3498DB`
- **RGB:** 52, 152, 219
- **Usage:** Links, secondary accents

**Sunset Red**
- **Hex:** `#E74C3C`
- **RGB:** 231, 76, 60
- **Usage:** Errors, warnings, critical states

**Industrial Gray**
- **Hex:** `#95A5A6`
- **RGB:** 149, 165, 166
- **Usage:** Neutral elements, backgrounds

### Dark Mode Palette (Primary UI)

**Background Primary:** `#0A1628`
**Background Secondary:** `#15202B`
**Background Card:** `#1E293B`
**Background Input:** `#0F1720`

**Text Primary:** `#E2E8F0`
**Text Secondary:** `#94A3B8`
**Text Muted:** `#64748B`

**Border:** `#334155`
**Border Light:** `#475569`

---

## 🔠 Typography

### Font Family

**Primary Font:** IBM Plex Sans
- Weights: Regular (400), Medium (500), SemiBold (600), Bold (700)
- Usage: All UI text, headings, body copy
- Why: Industrial heritage, excellent screen readability, engineered feel

**Monospace Font:** JetBrains Mono
- Usage: Technical specs, dimensions, IDs, code
- Why: Technical precision, clear numerals

### Type Scale

```
h1: 32px / Bold / -0.02em
h2: 24px / SemiBold / -0.01em
h3: 18px / SemiBold / normal
h4: 16px / SemiBold / normal
Body: 14px / Regular / normal
Small: 13px / Regular / normal
Label: 12px / Medium / 0.05em (uppercase)
Caption: 11px / Medium / 0.08em (uppercase)
```

### Typography Rules

- **Headlines:** Bold, tight letter-spacing
- **UI Labels:** Uppercase, tracked (letter-spacing: 0.05em)
- **Body Text:** 14px minimum for readability
- **Line Height:** 1.6 for body, 1.3 for headings
- **No decorative fonts:** Keep it functional

---

## 🧊 Logo Concepts

### Recommended Direction: Interlocking Crate System

**Visual:** Three stacked rectangular blocks in isometric view, fitting together perfectly.

**Style:** Geometric, minimal, modern industrial

**Colors:** 
- Primary: Industrial Steel Blue (#1E3A5F)
- Accent: Safety Orange (#E67E22)

**Variations Needed:**
- Full logo (with SAMCI text)
- Icon only (blocks symbol)
- Horizontal layout
- Stacked layout
- Dark and light versions

### Logo Usage Rules

**Minimum Size:**
- Digital: 24px height
- Print: 0.5 inch height

**Clear Space:**
- Minimum 1x logo height on all sides

**Don'ts:**
- Don't stretch or skew
- Don't rotate
- Don't add effects/shadows
- Don't change colors
- Don't outline

---

## 🎨 UI Design System

### Layout Principles

**Grid System:**
- Base unit: 8px
- All spacing in multiples of 8px
- Consistent alignment across components

**Border Radius:**
- Base: 6px (inputs, buttons, small cards)
- Large: 8px (panels, modals, major sections)
- Never use extreme rounding (no pill shapes except buttons)

**Shadows:**
- Small: `0 1px 2px rgba(0, 0, 0, 0.3)`
- Medium: `0 2px 4px rgba(0, 0, 0, 0.4)`
- Large: `0 4px 8px rgba(0, 0, 0, 0.5)`
- Use sparingly, prefer borders over shadows

### Component Styling

**Buttons:**

Primary:
```css
background: #E67E22 (Safety Orange)
color: white
padding: 12px 24px
border-radius: 6px
font-size: 13px
font-weight: 600
text-transform: uppercase
letter-spacing: 0.05em
```

Secondary:
```css
background: #2C3E50 (Charcoal Iron)
color: #E2E8F0
border: 1px solid #334155
```

**Cards:**
```css
background: #1E293B (Card background)
border: 1px solid #334155
border-radius: 8px
padding: 24px
box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4)
```

**Input Fields:**
```css
background: #0F1720 (Input background)
border: 1px solid #334155
border-radius: 6px
padding: 12px
color: #E2E8F0
font-size: 14px
```

Focus state:
```css
border-color: #1E3A5F (Steel Blue)
box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.2)
```

**Tables:**
- Header: Light gray background (#F8F9FA in light mode)
- Borders: 1px solid #334155
- Row hover: Subtle steel blue tint
- Zebra striping: Optional, subtle

### Icon Style

**Stroke-based icons** (not filled)
- Stroke weight: 2px
- Size: 24x24px standard
- Style: Phosphor Icons or Lucide Icons
- Industrial feel: boxes, grids, layers, gears

### 3D Visualization Colors

**Container:**
- Wireframe: Steel Blue (#1E3A5F) at 30% opacity
- Grid: Concrete Gray (#7F8C8D), 1px lines

**Crate Color Coding:**
- Type A: Safety Orange (#E67E22)
- Type B: Steel Blue Light (#3498DB)
- Type C: Mint Efficiency (#2ECC71)
- Type D: Sunset Red (#E74C3C)
- Type E: Industrial Gray (#95A5A6)

Each crate has dark edge/wireframe for definition.

---

## 📐 Spacing System

Based on 8px grid:

```
xs:  8px   (1 unit)
sm:  12px  (1.5 units)
md:  16px  (2 units)
lg:  24px  (3 units)
xl:  32px  (4 units)
2xl: 48px  (6 units)
```

---

## 🎯 Brand Voice & Tone

### Writing Style

**Direct & Functional:**
✅ "Optimize your container capacity"
❌ "Unlock your shipping potential"

**Confident & Precise:**
✅ "SAMCI calculates optimal placement"
❌ "SAMCI tries to help you pack better"

**Technical but Accessible:**
✅ "Achieve 91% space utilization"
✅ "Pack 23% more crates"
❌ "Significantly improve your packing"

### Messaging Principles

1. **Lead with benefits, not features**
   - "Save 15% on shipping costs" before "AI-powered algorithm"

2. **Use numbers and data**
   - Quantify improvements
   - Show exact metrics

3. **Be honest about limitations**
   - No overpromising
   - Clear about what it does and doesn't do

4. **Respect the user's expertise**
   - Logistics managers are professionals
   - Don't talk down or oversimplify

---

## 🚫 Brand Don'ts

**Visual:**
- No gradients (except subtle UI accents)
- No playful illustrations
- No emoji in professional contexts
- No trendy startup aesthetics
- No rounded "friendly" shapes everywhere

**Language:**
- No "disrupting" or "revolutionizing"
- No "unlock" or "unleash"
- No excessive exclamation marks
- No jargon without explanation
- No consumer-style marketing speak

**Positioning:**
- We're not a lifestyle brand
- We're not a generic AI platform
- We're not trying to be cool
- We ARE reliable engineering software

---

## 🎨 Marketing Assets

### Landing Page Style
- Clean, data-focused
- Screenshots with real data
- Engineering console aesthetic
- Clear pricing table
- ROI calculator

### Screenshots
- Dark mode UI
- Real container/crate data
- Clear annotations
- Professional lighting
- No fake data

### Sales Materials
- PDF with brand colors
- Data tables in monospace font
- Charts with brand palette
- Professional, not flashy

---

## 📊 Competitive Positioning

**Most logistics software:**
- Looks outdated (Windows 95)
- OR tries too hard to be "innovative"

**SAMCI:**
- Modern but industrial
- Smart but practical
- Confident through restraint
- Looks like equipment you trust

---

## ✅ Brand Checklist

Before any design release:

**Visual Identity:**
- [ ] Uses IBM Plex Sans font
- [ ] Colors match brand palette
- [ ] 8px grid alignment
- [ ] Proper border radius (6-8px)
- [ ] Industrial feel maintained

**Voice & Tone:**
- [ ] Direct and clear language
- [ ] No excessive jargon
- [ ] Numbers and data used
- [ ] Confident but not arrogant
- [ ] Respects user expertise

**User Experience:**
- [ ] Readable at dashboard scale
- [ ] High contrast for warehouse environments
- [ ] Clear hierarchy
- [ ] Functional over decorative

---

## 🔗 Design Resources

**Fonts:**
- IBM Plex Sans: https://fonts.google.com/specimen/IBM+Plex+Sans
- JetBrains Mono: https://www.jetbrains.com/lp/mono/

**Icon Libraries:**
- Phosphor Icons: https://phosphoricons.com/
- Lucide Icons: https://lucide.dev/

**Design Tools:**
- Figma components (to be created)
- CSS variables (implemented in code)
- Brand color palette (exported formats)

---

## 📞 Brand Governance

**Who Can Use:**
- Marketing team
- Product designers
- Engineering (for UI implementation)
- Sales (for decks and materials)

**Approval Required:**
- Logo variations
- New color additions
- Major UI pattern changes
- External brand partnerships

**Questions?**
Contact: [Brand/Design Lead]

---

**Version:** 1.0  
**Last Updated:** 2026-04-26  
**Status:** Active

---

**This is a living document. Update as the brand evolves, but maintain core principles: Strong. Precise. Industrial. Trustworthy.**
