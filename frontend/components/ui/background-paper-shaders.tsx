"use client";

import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

interface BackgroundPaperShadersProps {
  className?: string;
}

function AnimatedShader() {
  const meshRef = useRef<THREE.Mesh>(null);

  const vertexShader = `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `;

  const fragmentShader = `
    uniform float uTime;
    uniform vec2 uResolution;
    varying vec2 vUv;

    // Noise function for paper texture
    float random(vec2 st) {
      return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
    }

    float noise(vec2 st) {
      vec2 i = floor(st);
      vec2 f = fract(st);
      float a = random(i);
      float b = random(i + vec2(1.0, 0.0));
      float c = random(i + vec2(0.0, 1.0));
      float d = random(i + vec2(1.0, 1.0));
      vec2 u = f * f * (3.0 - 2.0 * f);
      return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
    }

    void main() {
      vec2 st = vUv * 3.0;
      
      // Animated paper texture
      float n = noise(st + uTime * 0.05);
      n += noise(st * 2.0 + uTime * 0.03) * 0.5;
      n += noise(st * 4.0 - uTime * 0.02) * 0.25;
      n /= 1.75;
      
      // Subtle color variations for depth
      vec3 color1 = vec3(0.95, 0.95, 0.97); // Light blue-grey
      vec3 color2 = vec3(0.92, 0.93, 0.95); // Slightly darker
      vec3 color = mix(color1, color2, n);
      
      // Add subtle vignette
      float vignette = smoothstep(0.8, 0.2, length(vUv - 0.5));
      color *= 0.85 + 0.15 * vignette;
      
      gl_FragColor = vec4(color, 1.0);
    }
  `;

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uResolution: { 
        value: new THREE.Vector2(
          typeof window !== 'undefined' ? window.innerWidth : 1920,
          typeof window !== 'undefined' ? window.innerHeight : 1080
        ) 
      },
    }),
    []
  );

  useFrame((state) => {
    if (meshRef.current) {
      const material = meshRef.current.material as THREE.ShaderMaterial;
      material.uniforms.uTime.value = state.clock.getElapsedTime();
    }
  });

  return (
    <mesh ref={meshRef}>
      <planeGeometry args={[2, 2]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
      />
    </mesh>
  );
}

export function BackgroundPaperShaders({ className }: BackgroundPaperShadersProps) {
  return (
    <div
      className={className}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        zIndex: -1,
        pointerEvents: "none",
      }}
    >
      <Canvas
        camera={{ position: [0, 0, 1], fov: 75 }}
        style={{ width: "100%", height: "100%" }}
      >
        <AnimatedShader />
      </Canvas>
    </div>
  );
}
