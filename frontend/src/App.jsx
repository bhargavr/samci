import React, { useState } from 'react'
import InputForm from './components/InputForm'
import Viewer3D from './components/Viewer3D'
import ResultsPanel from './components/ResultsPanel'
import StepsPanel from './components/StepsPanel'
import { API_URL } from './config'
import './App.css'

function App() {
  const [packingResult, setPackingResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [viewMode, setViewMode] = useState('final') // 'final' or 'step-by-step'

  const handleOptimize = async (inputData) => {
    setLoading(true)
    setError(null)
    setPackingResult(null)
    setCurrentStep(0)

    try {
      const response = await fetch(`${API_URL}/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(inputData),
      })

      if (!response.ok) {
        throw new Error(`Optimization failed: ${response.statusText}`)
      }

      const result = await response.json()
      setPackingResult(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleStepChange = (step) => {
    setCurrentStep(step)
  }

  const getVisiblePlacements = () => {
    if (!packingResult) return []
    if (viewMode === 'final') return packingResult.placements
    // In step-by-step mode, show placements up to current step
    return packingResult.placements.slice(0, currentStep + 1)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>SAMCI</h1>
        <p>Precision at Scale - Container Optimization Platform</p>
      </header>

      <div className="app-content">
        <div className="left-panel">
          <InputForm onOptimize={handleOptimize} loading={loading} />

          {packingResult && (
            <>
              <ResultsPanel result={packingResult} />
              <StepsPanel
                steps={packingResult.steps}
                currentStep={currentStep}
                onStepChange={handleStepChange}
                viewMode={viewMode}
                onViewModeChange={setViewMode}
              />
            </>
          )}

          {error && (
            <div className="error-panel">
              <h3>Error</h3>
              <p>{error}</p>
            </div>
          )}
        </div>

        <div className="right-panel">
          <Viewer3D
            container={packingResult?.container}
            placements={getVisiblePlacements()}
            loading={loading}
          />
        </div>
      </div>
    </div>
  )
}

export default App
