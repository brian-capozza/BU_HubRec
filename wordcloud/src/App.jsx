import * as THREE from 'three'
import { useRef, useState, useMemo, useEffect, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Billboard, Text, TrackballControls } from '@react-three/drei'

/* ------------------ WORD COMPONENT ------------------ */

function Word({ children, hoverColor, defaultColor, ...props }) {
  const color = new THREE.Color()
  const fontProps = { 
    fontSize: 2.5, 
    letterSpacing: -0.05, 
    lineHeight: 1, 
    'material-toneMapped': false 
  }

  const ref = useRef()
  const [hovered, setHovered] = useState(false)

  const over = (e) => {
    e.stopPropagation()
    setHovered(true)
  }

  const out = () => setHovered(false)

  // Change mouse cursor on hover
  useEffect(() => {
    if (hovered) document.body.style.cursor = 'pointer'
    return () => (document.body.style.cursor = 'auto')
  }, [hovered])

  // Lerp hover color
  useFrame(() => {
    if (ref.current) {
      ref.current.material.color.lerp(
        color.set(hovered ? hoverColor : defaultColor), 
        0.1
      )
    }
  })

  return (
    <Billboard {...props}>
      <Text 
        ref={ref} 
        onPointerOver={over} 
        onPointerOut={out} 
        onClick={() => console.log(`clicked: ${children}`)} 
        {...fontProps}
      >
        {children}
      </Text>
    </Billboard>
  )
}

/* ------------------ WORD CLOUD ------------------ */

function Cloud({ count, radius, wordColor, hoverColor, words }) {
  const wordList = useMemo(() => {
    const temp = []
    const spherical = new THREE.Spherical()

    const phiSpan = Math.PI / (count + 1)
    const thetaSpan = (Math.PI * 2) / count

    let wordIndex = 0

    for (let i = 1; i < count + 1; i++) {
      for (let j = 0; j < count; j++) {
        const position = new THREE.Vector3().setFromSpherical(
          spherical.set(radius, phiSpan * i, thetaSpan * j)
        )

        // Loop words if fewer than needed
        const word = words[wordIndex % words.length]

        temp.push([position, word])
        wordIndex++
      }
    }

    return temp
  }, [count, radius, words])

  return (
    <>
      {wordList.map(([pos, word], index) => (
        <Word
          key={index}
          position={pos}
          defaultColor={wordColor}
          hoverColor={hoverColor}
        >
          {word}
        </Word>
      ))}
    </>
  )
}

/* ------------------ ROTATING GROUP ------------------ */

function RotatingGroup({ children }) {
  const groupRef = useRef()

  // Subtle rotation animation
  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.001  // smooth spin
      groupRef.current.rotation.x += 0.0003 // tiny tilt
    }
  })

  return (
    <group ref={groupRef} rotation={[10, 10.5, 10]}>
      {children}
    </group>
  )
}


/* ------------------ MAIN APP ------------------ */

export default function App({
  backgroundColor = '#202025',
  fogColor = '#202025',
  wordCount = 8,
  sphereRadius = 20,
  wordColor = 'white',
  hoverColor = '#bd0e02',
  words = null
}) {
  const parsedWords = useMemo(() => {
    if (words) return words
    const el = document.getElementById('word-data')
    return JSON.parse(el.textContent)
  }, [words])

  return (
    <Canvas
      dpr={[1, 2]}
      camera={{ position: [0, 0, 60], fov: 75 }}
      style={{ background: backgroundColor, display: 'block' }}
    >
      <fog attach="fog" args={[fogColor, 0, 80]} />

      <Suspense fallback={null}>
        <RotatingGroup>
          <Cloud
            count={wordCount}
            radius={sphereRadius}
            wordColor={wordColor}
            hoverColor={hoverColor}
            words={parsedWords}
          />
        </RotatingGroup>
      </Suspense>

      <TrackballControls />
    </Canvas>
  )
}
