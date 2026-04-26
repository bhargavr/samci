# SAMCI Brand Quick Reference

Fast lookup for developers and designers.

---

## 🎨 Colors (CSS Variables)

```css
/* Primary Colors */
--color-steel-blue: #1E3A5F
--color-charcoal-iron: #2C3E50
--color-concrete-gray: #7F8C8D
--color-safety-orange: #E67E22
--color-mint-efficiency: #2ECC71

/* Extended Palette */
--color-steel-blue-light: #3498DB
--color-sunset-red: #E74C3C
--color-industrial-gray: #95A5A6

/* Dark Mode UI */
--color-bg-primary: #0A1628
--color-bg-secondary: #15202B
--color-bg-card: #1E293B
--color-bg-input: #0F1720

/* Text */
--color-text-primary: #E2E8F0
--color-text-secondary: #94A3B8
--color-text-muted: #64748B

/* Borders */
--color-border: #334155
--color-border-light: #475569
```

---

## 🔠 Typography

```css
/* Font Family */
font-family: 'IBM Plex Sans', system-ui, sans-serif;

/* Type Scale */
h1: 32px / 700 / -0.02em
h2: 24px / 600 / -0.01em
h3: 18px / 600 / normal
Body: 14px / 400 / normal
Label: 12px / 500 / 0.05em (uppercase)
Caption: 11px / 500 / 0.08em (uppercase)
```

---

## 📐 Spacing (8px Grid)

```css
--grid-base: 8px

/* Usage */
padding: calc(var(--grid-base) * 2)    /* 16px */
margin: calc(var(--grid-base) * 3)     /* 24px */
gap: calc(var(--grid-base) * 1.5)     /* 12px */
```

---

## 🎨 Component Styles

### Button (Primary)
```css
background: var(--color-safety-orange);
color: white;
padding: 12px 24px;
border-radius: 6px;
font-size: 13px;
font-weight: 600;
text-transform: uppercase;
letter-spacing: 0.05em;
```

### Card
```css
background: var(--color-bg-card);
border: 1px solid var(--color-border);
border-radius: 8px;
padding: 24px;
box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
```

### Input
```css
background: var(--color-bg-input);
border: 1px solid var(--color-border);
border-radius: 6px;
padding: 12px;
color: var(--color-text-primary);
font-size: 14px;
```

### Input Focus
```css
border-color: var(--color-steel-blue);
box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.2);
```

---

## 🎯 Brand Elements

### Name
**SAMCI**

### Tagline
**"Precision at Scale"**

### Full Title
**SAMCI - Container Optimization Platform**

### Header Format
```html
<h1>SAMCI</h1>
<p>Precision at Scale - Container Optimization Platform</p>
```

---

## 🧊 3D Viewer Colors

```javascript
// Crate type colors
const CRATE_COLORS = [
  '#E67E22', // Safety Orange
  '#3498DB', // Steel Blue Light
  '#2ECC71', // Mint Efficiency
  '#E74C3C', // Sunset Red
  '#95A5A6', // Industrial Gray
  '#1E3A5F', // Steel Blue Dark
  '#F39C12', // Industrial Yellow
  '#16A085', // Teal Accent
]

// Container wireframe
color: '#1E3A5F'
opacity: 0.3
```

---

## 📏 Border Radius

```css
--border-radius-base: 6px     /* Inputs, buttons, small cards */
--border-radius-large: 8px    /* Panels, major sections */
```

---

## 🌑 Shadows

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3)
--shadow-md: 0 2px 4px rgba(0, 0, 0, 0.4)
--shadow-lg: 0 4px 8px rgba(0, 0, 0, 0.5)
```

---

## ✅ Quick Checks

**Is this on-brand?**
- [ ] Uses IBM Plex Sans font
- [ ] Dark industrial colors
- [ ] 8px grid aligned
- [ ] Safety Orange for primary actions
- [ ] No playful/trendy elements
- [ ] Clear, direct language
- [ ] Professional engineering feel

---

## 🚫 Avoid

**Visual:**
- ❌ Bright gradients
- ❌ Rounded pill shapes (except buttons)
- ❌ Playful illustrations
- ❌ Consumer-style aesthetics

**Language:**
- ❌ "Revolutionizing"
- ❌ "Unlock your potential"
- ❌ Excessive exclamation marks!!!

**Use Instead:**
- ✅ Direct, factual statements
- ✅ Numbers and data
- ✅ Industrial terminology
- ✅ Engineering precision

---

## 📦 Usage Example

```jsx
// Button
<button className="btn-primary">
  Optimize Container
</button>

// Card
<div className="metric-card">
  <div className="metric-label">Space Utilization</div>
  <div className="metric-value">91.2%</div>
</div>

// Input
<div className="form-field">
  <label>Container Length (mm)</label>
  <input type="number" placeholder="5898" />
</div>
```

---

## 🎨 Color Usage Guide

| Element | Color | Variable |
|---------|-------|----------|
| Primary Action | Safety Orange | `--color-safety-orange` |
| Headers | Steel Blue | `--color-steel-blue` |
| Body Text | Text Primary | `--color-text-primary` |
| Labels | Text Secondary | `--color-text-secondary` |
| Success | Mint | `--color-mint-efficiency` |
| Error | Sunset Red | `--color-sunset-red` |
| Borders | Border | `--color-border` |

---

## 🔗 Resources

**Full Guide:** [BRAND_IDENTITY.md](BRAND_IDENTITY.md)

**Font:** IBM Plex Sans (Google Fonts)

**Icons:** Phosphor Icons or Lucide

**Design System:** See `frontend/src/index.css` for all CSS variables

---

**When in doubt:** Keep it industrial, keep it precise, keep it professional.
