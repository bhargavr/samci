import React, { useState } from 'react'
import './StepsPanel.css'

const StepsPanel = ({ steps, currentStep, onStepChange, viewMode, onViewModeChange }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  if (!steps || steps.length === 0) return null

  const handlePrevious = () => {
    if (currentStep > 0) {
      onStepChange(currentStep - 1)
    }
  }

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      onStepChange(currentStep + 1)
    }
  }

  const handleStepClick = (stepIndex) => {
    onStepChange(stepIndex)
  }

  const currentStepData = steps[currentStep]

  return (
    <div className="steps-panel">
      <div className="steps-header">
        <h2>Step-by-Step Instructions</h2>
        <button
          className="btn-toggle-view"
          onClick={() => onViewModeChange(viewMode === 'final' ? 'step-by-step' : 'final')}
        >
          {viewMode === 'final' ? 'Enable Step Mode' : 'Show Final Layout'}
        </button>
      </div>

      {viewMode === 'step-by-step' && (
        <>
          {/* Current Step Display */}
          <div className="current-step">
            <div className="step-number">
              Step {currentStepData.step} of {steps.length}
            </div>
            <div className="step-description">
              {currentStepData.description}
            </div>
            <div className="step-details">
              <span className="step-detail-item">
                <strong>Crate:</strong> {currentStepData.crate_id}
              </span>
              <span className="step-detail-item">
                <strong>Position:</strong> [{currentStepData.position.map(p => p.toFixed(0)).join(', ')}]
              </span>
              <span className="step-detail-item">
                <strong>Level:</strong> {currentStepData.stack_level === 0 ? 'Floor' : `Stack ${currentStepData.stack_level}`}
              </span>
            </div>
          </div>

          {/* Navigation Controls */}
          <div className="step-controls">
            <button
              className="btn-step"
              onClick={handlePrevious}
              disabled={currentStep === 0}
            >
              ← Previous
            </button>
            <span className="step-indicator">
              {currentStep + 1} / {steps.length}
            </span>
            <button
              className="btn-step"
              onClick={handleNext}
              disabled={currentStep === steps.length - 1}
            >
              Next →
            </button>
          </div>

          {/* Progress Bar */}
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            />
          </div>

          {/* All Steps List (Collapsible) */}
          <div className="steps-list-section">
            <button
              className="btn-toggle-list"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? '▼' : '▶'} All Steps ({steps.length})
            </button>

            {isExpanded && (
              <div className="steps-list">
                {steps.map((step, index) => (
                  <div
                    key={index}
                    className={`step-item ${index === currentStep ? 'active' : ''} ${index <= currentStep ? 'completed' : ''}`}
                    onClick={() => handleStepClick(index)}
                  >
                    <div className="step-item-number">{step.step}</div>
                    <div className="step-item-description">{step.description}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {viewMode === 'final' && (
        <div className="final-mode-info">
          <p>Showing complete packing layout with all {steps.length} crates.</p>
          <p className="info-hint">Switch to Step Mode to see placement instructions one by one.</p>
        </div>
      )}
    </div>
  )
}

export default StepsPanel
