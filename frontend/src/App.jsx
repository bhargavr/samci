import React, { useState } from 'react'
import InputForm from './components/InputForm'
import Viewer3D from './components/Viewer3D'
import ResultsPanel from './components/ResultsPanel'
import StepsPanel from './components/StepsPanel'
import UserGuide from './components/UserGuide'
import { API_URL } from './config'
import './App.css'

/* ── SAMCI Logo Mark (Direction C — Structural Wordmark) ─────────── */
function SamciLogoMark({ size = 1 }) {
  const dots = [
    [0,0],[1,0],[2,0],
    [0,1],[1,1],[2,1],
    [0,2],[1,2],[2,2],
  ]
  return (
    <svg width={32 * size} height={32 * size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      {dots.map(([col, row]) => {
        const isAccent = row === 0 && col === 2
        return (
          <rect
            key={`${row}-${col}`}
            x={3 + col * 9} y={3 + row * 9}
            width={6} height={6} rx={1}
            fill={isAccent ? '#E07828' : '#fff'}
            opacity={isAccent ? 1 : row === 0 ? 0.9 : row === 1 ? 0.5 : 0.2}
          />
        )
      })}
    </svg>
  )
}

const NAV_ITEMS = [
  { id: 'jobs',      label: 'Packing Jobs' },
  { id: 'guide',     label: 'User Guide'   },
  { id: 'dashboard', label: 'Dashboard'    },
  { id: 'containers',label: 'Containers'   },
  { id: 'reports',   label: 'Reports'      },
]

function App() {
  const [page, setPage] = useState('jobs')
  const [packingResult, setPackingResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [viewMode, setViewMode] = useState('final')

  const handleOptimize = async (inputData) => {
    setLoading(true)
    setError(null)
    setPackingResult(null)
    setCurrentStep(0)
    try {
      const response = await fetch(`${API_URL}/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputData),
      })
      if (!response.ok) throw new Error(`Optimization failed: ${response.statusText}`)
      const result = await response.json()
      setPackingResult(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getVisiblePlacements = () => {
    if (!packingResult) return []
    if (viewMode === 'final') return packingResult.placements
    return packingResult.placements.slice(0, currentStep + 1)
  }

  return (
    <div className="app">

      {/* ── Dark Sidebar ─────────────────────────────────────────── */}
      <aside className="app-sidebar">
        {/* Logo */}
        <div className="sidebar-logo">
          <div className="sidebar-logo-mark">
            <SamciLogoMark size={0.9} />
          </div>
          <span className="sidebar-logo-text">SAMCI</span>
        </div>

        {/* Nav */}
        <nav className="sidebar-nav">
          {NAV_ITEMS.map(item => (
            <div
              key={item.id}
              className={`sidebar-nav-item${page === item.id ? ' active' : ''}`}
              onClick={() => setPage(item.id)}
            >
              {item.label}
            </div>
          ))}
        </nav>

        {/* Status indicator */}
        <div className="sidebar-footer">
          <div className="sidebar-status-dot" />
          <span className="sidebar-status-label">System Online</span>
        </div>
      </aside>

      {/* ── Main Area ────────────────────────────────────────────── */}
      <div className="app-main">

        {/* Top bar */}
        <header className="app-topbar">
          <div className="topbar-title">
            <span className="topbar-label">
              {page === 'guide' ? 'DOCUMENTATION' : 'PACKING JOBS'}
            </span>
            <h1 className="topbar-heading">
              {page === 'guide' ? 'User Guide' : 'Container Loading Optimizer'}
            </h1>
          </div>
          {page !== 'guide' && (
            <div className="topbar-badge">
              <div className="status-dot status-dot--ready" />
              READY
            </div>
          )}
        </header>

        {/* Content */}
        {page === 'guide' ? (
          <UserGuide />
        ) : (
          <div className="app-content">
            <div className="left-panel">
              <InputForm onOptimize={handleOptimize} loading={loading} />

              {packingResult && (
                <>
                  <ResultsPanel result={packingResult} />
                  <StepsPanel
                    steps={packingResult.steps}
                    currentStep={currentStep}
                    onStepChange={setCurrentStep}
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
        )}
      </div>
    </div>
  )
}

export default App
