import React, { Suspense, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Grid, Box, Text } from '@react-three/drei'
import './Viewer3D.css'

// SAMCI Brand Color Palette for Crate Types
const CRATE_COLORS = [
  '#E07828', // Orange — primary accent
  '#0D1F35', // Navy — brand primary
  '#5A6A7E', // Steel — secondary
  '#2E9E6B', // Success green
  '#A8B4C2', // Slate — muted
  '#1A3252', // Navy dark
  '#C86A20', // Orange dark
  '#3D7A5E', // Green dark
]

const getCrateColor = (crateId) => {
  // Generate consistent color based on crate type ID
  const hash = crateId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return CRATE_COLORS[hash % CRATE_COLORS.length]
}

const Crate = ({ placement, opacity = 1 }) => {
  const [x, y, z] = placement.position
  const [length, width, height] = placement.dimensions
  const color = getCrateColor(placement.crate_id)

  // Convert mm to scene units (divide by 1000 for better scaling)
  const scaleX = length / 1000
  const scaleY = width / 1000
  const scaleZ = height / 1000

  // Position: add half dimensions to center the box
  const posX = (x + length / 2) / 1000
  const posY = (y + width / 2) / 1000
  const posZ = (z + height / 2) / 1000

  return (
    <group position={[posX, posZ, posY]}>
      <Box args={[scaleX, scaleZ, scaleY]}>
        <meshStandardMaterial
          color={color}
          transparent={opacity < 1}
          opacity={opacity}
          metalness={0.3}
          roughness={0.7}
        />
      </Box>
      {/* Wireframe */}
      <Box args={[scaleX, scaleZ, scaleY]}>
        <meshBasicMaterial color="#000000" wireframe />
      </Box>
    </group>
  )
}

const Container = ({ length, width, height }) => {
  if (!length || !width || !height) return null

  // Convert mm to scene units
  const scaleX = length / 1000
  const scaleY = width / 1000
  const scaleZ = height / 1000

  return (
    <group position={[scaleX / 2, scaleZ / 2, scaleY / 2]}>
      <Box args={[scaleX, scaleZ, scaleY]}>
        <meshBasicMaterial
          color="#1e293b"
          transparent
          opacity={0.1}
          wireframe
        />
      </Box>
      <Box args={[scaleX, scaleZ, scaleY]}>
        <meshBasicMaterial
          color="#475569"
          transparent
          opacity={0.05}
        />
      </Box>
    </group>
  )
}

const Scene = ({ container, placements }) => {
  const containerLength = container?.length || 6000
  const containerWidth = container?.width || 2400
  const containerHeight = container?.height || 2400

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={0.8} />
      <directionalLight position={[-10, 10, -5]} intensity={0.4} />

      {/* Camera */}
      <PerspectiveCamera
        makeDefault
        position={[8, 6, 8]}
        fov={50}
      />

      {/* Controls */}
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={2}
        maxDistance={30}
      />

      {/* Grid */}
      <Grid
        args={[containerLength / 1000 + 2, containerWidth / 1000 + 2]}
        cellSize={0.5}
        cellThickness={0.5}
        cellColor="#334155"
        sectionSize={1}
        sectionThickness={1}
        sectionColor="#475569"
        fadeDistance={30}
        fadeStrength={1}
        infiniteGrid={false}
        position={[containerLength / 2000, 0, containerWidth / 2000]}
      />

      {/* Container */}
      {container && (
        <Container
          length={containerLength}
          width={containerWidth}
          height={containerHeight}
        />
      )}

      {/* Crates */}
      {placements && placements.map((placement, index) => (
        <Crate key={index} placement={placement} />
      ))}

      {/* Axes helper - X (red), Y (green), Z (blue) */}
      <axesHelper args={[2]} />
    </>
  )
}

const Viewer3D = ({ container, placements, loading }) => {
  return (
    <div className="viewer-3d">
      {loading && (
        <div className="viewer-overlay">
          <div className="loading-spinner"></div>
          <p>Optimizing packing...</p>
        </div>
      )}

      {!placements && !loading && (
        <div className="viewer-overlay">
          <div className="viewer-placeholder">
            <p>Configure your container and crates, then click "Optimize Packing"</p>
            <p className="viewer-hint">The 3D view will show the optimized layout</p>
          </div>
        </div>
      )}

      <Canvas>
        <Suspense fallback={null}>
          <Scene container={container} placements={placements} />
        </Suspense>
      </Canvas>

      {placements && (
        <div className="viewer-controls">
          <div className="control-hint">
            <strong>Controls:</strong> Left-click + drag to rotate | Right-click + drag to pan | Scroll to zoom
          </div>
        </div>
      )}
    </div>
  )
}

export default Viewer3D
