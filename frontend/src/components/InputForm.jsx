import React, { useState } from 'react'
import { API_URL } from '../config'
import './InputForm.css'

const InputForm = ({ onOptimize, loading }) => {
  const [container, setContainer] = useState({
    length: 5898,
    width: 2352,
    height: 2393,
    max_weight: 28000,
  })

  const [crates, setCrates] = useState([
    {
      id: 'Large-Granite',
      length: 1200,
      width: 1000,
      height: 800,
      weight: 1200,
      quantity: 10,
      max_stack: 2,
      can_rotate: true,
    },
    {
      id: 'Medium-Granite',
      length: 1000,
      width: 800,
      height: 700,
      weight: 900,
      quantity: 20,
      max_stack: 3,
      can_rotate: true,
    },
  ])

  const [gapTolerance, setGapTolerance] = useState(50)

  const handleContainerChange = (field, value) => {
    setContainer({ ...container, [field]: parseFloat(value) || 0 })
  }

  const handleCrateChange = (index, field, value) => {
    const newCrates = [...crates]
    if (field === 'can_rotate') {
      newCrates[index][field] = value
    } else if (field === 'id') {
      newCrates[index][field] = value
    } else {
      newCrates[index][field] = parseFloat(value) || 0
    }
    setCrates(newCrates)
  }

  const addCrate = () => {
    setCrates([
      ...crates,
      {
        id: `Crate-${crates.length + 1}`,
        length: 1000,
        width: 800,
        height: 600,
        weight: 800,
        quantity: 5,
        max_stack: 2,
        can_rotate: true,
      },
    ])
  }

  const removeCrate = (index) => {
    setCrates(crates.filter((_, i) => i !== index))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onOptimize({
      container,
      crates,
      gap_tolerance: gapTolerance,
    })
  }

  const loadExample = async () => {
    try {
      const response = await fetch(`${API_URL}/examples/standard-container`)
      const data = await response.json()
      setContainer(data.container)
      setCrates(data.crates)
      setGapTolerance(data.gap_tolerance)
    } catch (err) {
      console.error('Failed to load example:', err)
    }
  }

  return (
    <div className="input-form">
      <div className="form-header">
        <h2>Configuration</h2>
        <button type="button" onClick={loadExample} className="btn-secondary">
          Load Example
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Container Section */}
        <section className="form-section">
          <h3>Container Dimensions</h3>
          <div className="form-grid">
            <div className="form-field">
              <label>Length (mm)</label>
              <input
                type="number"
                value={container.length}
                onChange={(e) => handleContainerChange('length', e.target.value)}
                required
              />
            </div>
            <div className="form-field">
              <label>Width (mm)</label>
              <input
                type="number"
                value={container.width}
                onChange={(e) => handleContainerChange('width', e.target.value)}
                required
              />
            </div>
            <div className="form-field">
              <label>Height (mm)</label>
              <input
                type="number"
                value={container.height}
                onChange={(e) => handleContainerChange('height', e.target.value)}
                required
              />
            </div>
            <div className="form-field">
              <label>Max Weight (kg)</label>
              <input
                type="number"
                value={container.max_weight}
                onChange={(e) => handleContainerChange('max_weight', e.target.value)}
                required
              />
            </div>
          </div>
        </section>

        {/* Crates Section */}
        <section className="form-section">
          <div className="section-header">
            <h3>Crate Types</h3>
            <button type="button" onClick={addCrate} className="btn-add">
              + Add Crate
            </button>
          </div>

          {crates.map((crate, index) => (
            <div key={index} className="crate-card">
              <div className="crate-header">
                <input
                  type="text"
                  value={crate.id}
                  onChange={(e) => handleCrateChange(index, 'id', e.target.value)}
                  className="crate-id-input"
                  placeholder="Crate ID"
                />
                <button
                  type="button"
                  onClick={() => removeCrate(index)}
                  className="btn-remove"
                >
                  ✕
                </button>
              </div>

              <div className="form-grid-small">
                <div className="form-field">
                  <label>L (mm)</label>
                  <input
                    type="number"
                    value={crate.length}
                    onChange={(e) => handleCrateChange(index, 'length', e.target.value)}
                    required
                  />
                </div>
                <div className="form-field">
                  <label>W (mm)</label>
                  <input
                    type="number"
                    value={crate.width}
                    onChange={(e) => handleCrateChange(index, 'width', e.target.value)}
                    required
                  />
                </div>
                <div className="form-field">
                  <label>H (mm)</label>
                  <input
                    type="number"
                    value={crate.height}
                    onChange={(e) => handleCrateChange(index, 'height', e.target.value)}
                    required
                  />
                </div>
                <div className="form-field">
                  <label>Weight (kg)</label>
                  <input
                    type="number"
                    value={crate.weight}
                    onChange={(e) => handleCrateChange(index, 'weight', e.target.value)}
                    required
                  />
                </div>
                <div className="form-field">
                  <label>Quantity</label>
                  <input
                    type="number"
                    value={crate.quantity}
                    onChange={(e) => handleCrateChange(index, 'quantity', e.target.value)}
                    required
                    min="1"
                  />
                </div>
                <div className="form-field">
                  <label>Max Stack</label>
                  <input
                    type="number"
                    value={crate.max_stack}
                    onChange={(e) => handleCrateChange(index, 'max_stack', e.target.value)}
                    required
                    min="1"
                    max="10"
                  />
                </div>
              </div>

              <div className="form-field-checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={crate.can_rotate}
                    onChange={(e) => handleCrateChange(index, 'can_rotate', e.target.checked)}
                  />
                  Allow 90° rotation
                </label>
              </div>
            </div>
          ))}
        </section>

        {/* Settings Section */}
        <section className="form-section">
          <h3>Settings</h3>
          <div className="form-field">
            <label>Gap Tolerance (mm)</label>
            <input
              type="number"
              value={gapTolerance}
              onChange={(e) => setGapTolerance(parseFloat(e.target.value) || 0)}
              min="0"
              max="200"
            />
            <small>Allowed gap for fitting crates (typically 20-50mm)</small>
          </div>
        </section>

        {/* Submit Button */}
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Optimizing...' : 'Optimize Packing'}
        </button>
      </form>
    </div>
  )
}

export default InputForm
