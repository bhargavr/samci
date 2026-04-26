import React from 'react'
import './ResultsPanel.css'

const ResultsPanel = ({ result }) => {
  if (!result) return null

  const {
    utilization_percent,
    weight_utilization,
    total_crates_packed,
    total_weight,
    unpacked_crates,
    weight_distribution,
    warnings
  } = result

  const hasWarnings = warnings && warnings.length > 0
  const hasUnpacked = unpacked_crates && unpacked_crates.length > 0

  return (
    <div className="results-panel">
      <h2>Results</h2>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Space Utilization</div>
          <div className="metric-value" style={{ color: getUtilizationColor(utilization_percent) }}>
            {utilization_percent.toFixed(1)}%
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Weight Utilization</div>
          <div className="metric-value" style={{ color: getUtilizationColor(weight_utilization) }}>
            {weight_utilization.toFixed(1)}%
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Crates Packed</div>
          <div className="metric-value">{total_crates_packed}</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Total Weight</div>
          <div className="metric-value">{total_weight.toFixed(0)} kg</div>
        </div>
      </div>

      {/* Weight Distribution */}
      {weight_distribution && (
        <div className="distribution-section">
          <h3>Weight Distribution</h3>
          <div className="distribution-grid">
            <div className="distribution-item">
              <span className="distribution-label">Front Left</span>
              <span className="distribution-value">
                {weight_distribution.front_left?.toFixed(0) || 0} kg
              </span>
            </div>
            <div className="distribution-item">
              <span className="distribution-label">Front Right</span>
              <span className="distribution-value">
                {weight_distribution.front_right?.toFixed(0) || 0} kg
              </span>
            </div>
            <div className="distribution-item">
              <span className="distribution-label">Back Left</span>
              <span className="distribution-value">
                {weight_distribution.back_left?.toFixed(0) || 0} kg
              </span>
            </div>
            <div className="distribution-item">
              <span className="distribution-label">Back Right</span>
              <span className="distribution-value">
                {weight_distribution.back_right?.toFixed(0) || 0} kg
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Unpacked Crates */}
      {hasUnpacked && (
        <div className="unpacked-section">
          <h3>Unpacked Crates ({unpacked_crates.length})</h3>
          <div className="unpacked-list">
            {unpacked_crates.map((crate, index) => (
              <div key={index} className="unpacked-item">
                {crate.crate_id} #{crate.instance_num}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Warnings */}
      {hasWarnings && (
        <div className="warnings-section">
          <h3>Warnings</h3>
          <ul className="warnings-list">
            {warnings.map((warning, index) => (
              <li key={index} className={warning.startsWith('[CRITICAL]') ? 'warning-critical' : ''}>
                {warning}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

const getUtilizationColor = (percent) => {
  if (percent >= 80) return '#10b981' // green
  if (percent >= 60) return '#f59e0b' // amber
  return '#ef4444' // red
}

export default ResultsPanel
