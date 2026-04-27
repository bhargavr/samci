import React, { useState } from 'react'
import './UserGuide.css'

const Section = ({ number, title, children }) => (
  <section className="guide-section">
    <h2 className="guide-section-title">
      <span className="guide-step-num">{number}</span>
      {title}
    </h2>
    {children}
  </section>
)

const Table = ({ headers, rows }) => (
  <div className="guide-table-wrap">
    <table className="guide-table">
      <thead>
        <tr>{headers.map(h => <th key={h}>{h}</th>)}</tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>
        ))}
      </tbody>
    </table>
  </div>
)

const Tip = ({ children }) => (
  <div className="guide-tip">
    <span className="guide-tip-label">TIP</span>
    {children}
  </div>
)

export default function UserGuide() {
  const [activeSection, setActiveSection] = useState(null)

  const toc = [
    { id: 'overview',      label: 'What It Does' },
    { id: 'container',     label: 'Step 1 — Container' },
    { id: 'crates',        label: 'Step 2 — Crates' },
    { id: 'gap',           label: 'Step 3 — Gap Tolerance' },
    { id: 'run',           label: 'Step 4 — Run' },
    { id: 'results',       label: 'Reading Results' },
    { id: 'tips',          label: 'Tips' },
  ]

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    setActiveSection(id)
  }

  return (
    <div className="guide-root">

      {/* Sidebar TOC */}
      <nav className="guide-toc">
        <div className="guide-toc-label">On this page</div>
        {toc.map(item => (
          <button
            key={item.id}
            className={`guide-toc-item${activeSection === item.id ? ' active' : ''}`}
            onClick={() => scrollTo(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      {/* Content */}
      <article className="guide-content">
        <header className="guide-header">
          <div className="guide-header-tag">USER GUIDE</div>
          <h1 className="guide-title">Container Loading Optimizer</h1>
          <p className="guide-subtitle">
            Calculate the optimal arrangement of granite crates inside a shipping container,
            maximising space utilisation while respecting weight limits and stacking rules.
          </p>
        </header>

        {/* ── What It Does ─────────────────────────────────────────── */}
        <section className="guide-section" id="overview">
          <h2 className="guide-section-title">What It Does</h2>
          <p className="guide-body">
            Enter your container dimensions and crate types, click <strong>Optimize Packing</strong>,
            and the engine returns a fully worked loading plan — 3D visualisation, space and weight
            utilisation metrics, and a step-by-step loading sequence for the crew on the floor.
          </p>
        </section>

        {/* ── Step 1 ───────────────────────────────────────────────── */}
        <Section number="01" title="Set Container Dimensions" id="container">
          <p className="guide-body">Enter the internal dimensions and maximum payload of your container.</p>
          <Table
            headers={['Field', 'Description', 'Example']}
            rows={[
              ['Length (mm)', 'Internal length', '5898 — standard 20 ft'],
              ['Width (mm)',  'Internal width',  '2352'],
              ['Height (mm)', 'Internal height', '2393'],
              ['Max Weight (kg)', 'Total load capacity', '28000'],
            ]}
          />
        </Section>

        {/* ── Step 2 ───────────────────────────────────────────────── */}
        <Section number="02" title="Add Your Crates" id="crates">
          <p className="guide-body">
            Add one row per crate <em>type</em>. Click <strong>+ Add Crate</strong> for more types,
            or <strong>✕</strong> to remove one.
          </p>
          <Table
            headers={['Field', 'Description']}
            rows={[
              ['Crate ID',        'Name for this crate type, e.g. Large-Granite'],
              ['L / W / H (mm)',  'Crate dimensions'],
              ['Weight (kg)',     'Weight of a single crate'],
              ['Quantity',        'How many of this type to pack'],
              ['Max Stack',       'Maximum crates of this type stacked vertically'],
              ['Allow 90° rotation', 'Whether the crate can be turned sideways to fit better'],
            ]}
          />

          <div className="guide-callout" id="max-stack-detail">
            <div className="guide-callout-title">About Max Stack</div>
            <p className="guide-body">
              <strong>Max Stack</strong> limits how many crates of this type can be placed on top of
              each other in a single vertical column. It reflects real-world constraints:
            </p>
            <ul className="guide-list">
              <li><strong>Fragility / crush risk</strong> — heavier slabs cannot bear the load of additional crates above them</li>
              <li><strong>Container height</strong> — a tall stack may exceed the available headroom</li>
              <li><strong>Handling safety</strong> — warehouse and loading regulations often cap stack height</li>
            </ul>
            <Table
              headers={['Crate type', 'Typical Max Stack']}
              rows={[
                ['Heavy / fragile (large granite slabs)', '1 – 2'],
                ['Medium crates',                         '3'],
                ['Small / light crates',                  '4 or more'],
              ]}
            />
          </div>
        </Section>

        {/* ── Step 3 ───────────────────────────────────────────────── */}
        <Section number="03" title="Adjust Gap Tolerance" id="gap">
          <p className="guide-body">
            <strong>Gap Tolerance</strong> (default <code>50 mm</code>) is the allowable slack when
            fitting crates side by side. It accounts for packaging material, strapping, and loading
            imprecision.
          </p>
          <Table
            headers={['Setting', 'When to use']}
            rows={[
              ['20 – 30 mm', 'Precision-cut crates, tight packing needed'],
              ['50 mm',      'Standard — recommended starting point'],
              ['80 – 100 mm', 'Irregular shapes, extra strapping, or easier manual loading'],
            ]}
          />
          <Tip>Start with the default 50 mm. If crates come back unpacked, increase the tolerance before adding more containers.</Tip>
        </Section>

        {/* ── Step 4 ───────────────────────────────────────────────── */}
        <Section number="04" title="Run the Optimizer" id="run">
          <p className="guide-body">
            Click <strong>Optimize Packing</strong>. The engine typically returns results in under
            two seconds. Results stay on screen until you run a new optimisation.
          </p>
          <Tip>Use <strong>Load Example</strong> to pre-fill a standard 20 ft container with typical granite crate sizes — good for a quick test run.</Tip>
        </Section>

        {/* ── Results ──────────────────────────────────────────────── */}
        <section className="guide-section" id="results">
          <h2 className="guide-section-title">Reading the Results</h2>

          <div className="guide-results-grid">
            <div className="guide-result-card">
              <div className="guide-result-card-title">Metrics</div>
              <ul className="guide-list">
                <li><strong>Space utilisation %</strong> — volume of container actually used</li>
                <li><strong>Weight utilisation %</strong> — load as a percentage of max capacity</li>
                <li><strong>Crates packed</strong> — total count placed successfully</li>
                <li><strong>Total weight</strong> — gross load in kg</li>
              </ul>
            </div>

            <div className="guide-result-card">
              <div className="guide-result-card-title">3D Viewer</div>
              <ul className="guide-list">
                <li>Rotate — click and drag</li>
                <li>Pan — middle-click or two-finger drag</li>
                <li>Zoom — scroll wheel or pinch</li>
                <li>Each crate type has a distinct colour</li>
              </ul>
            </div>

            <div className="guide-result-card">
              <div className="guide-result-card-title">Step-by-Step Mode</div>
              <ul className="guide-list">
                <li>Switch to <strong>Step-by-Step</strong> to walk through the loading sequence one crate at a time</li>
                <li>Use ← → to move between steps</li>
                <li>Print or share the sequence with the loading crew</li>
              </ul>
            </div>

            <div className="guide-result-card guide-result-card--warn">
              <div className="guide-result-card-title">Unpacked Crates</div>
              <ul className="guide-list">
                <li>Crates that didn't fit are listed separately</li>
                <li>Try increasing gap tolerance, reducing quantities, or splitting across multiple containers</li>
              </ul>
            </div>
          </div>
        </section>

        {/* ── Tips ─────────────────────────────────────────────────── */}
        <section className="guide-section" id="tips">
          <h2 className="guide-section-title">Tips</h2>
          <ul className="guide-list guide-list--spaced">
            <li>Run the optimiser <strong>after every change</strong> — it recalculates from scratch each time.</li>
            <li>If utilisation seems low, try enabling <strong>90° rotation</strong> for crate types where orientation doesn't matter.</li>
            <li>For mixed loads, order crate types from <strong>heaviest to lightest</strong> — the algorithm places heavy items first, which typically improves stability scores.</li>
            <li>Max Stack of <strong>1</strong> forces floor-level placement only — useful for crates with fragile top surfaces.</li>
          </ul>
        </section>

      </article>
    </div>
  )
}
