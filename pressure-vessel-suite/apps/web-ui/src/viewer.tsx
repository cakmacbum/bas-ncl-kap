import React, { useEffect, useMemo, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { Bounds, Html, GizmoHelper, GizmoViewport } from "@react-three/drei";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
import * as THREE from "three";
import { CameraHelpNote, CameraRigLayer, CameraToolbar, type CameraApi } from "./cameraToolbar";

// 3D model için ölçü/konum bilgisi (project data'dan; K2 — mesh'ten ölçülmez).
export interface NozzleDims {
  tag: string;
  z: number;
  thetaDeg: number;
  tipR: number;
  od: number;
  host: string;
}

export interface ModelDims {
  L: number;        // teğet boyu (mm)
  outerR: number;   // gövde dış yarıçapı (mm)
  overallLen: number;
  outerD: number;
  thickness: number;
  orientation?: "horizontal" | "vertical";
  nozzle: NozzleDims;       // geriye uyumluluk (ilk nozul)
  nozzles?: NozzleDims[];   // tüm nozullar
}

function Label({ position, children }: { position: [number, number, number]; children: React.ReactNode }) {
  return (
    <Html position={position} center distanceFactor={2600} className="dim3d" zIndexRange={[10, 0]}>
      {children}
    </Html>
  );
}

function VesselMesh({ geometry, dims, clippingPlanes }: { geometry: THREE.BufferGeometry; dims: ModelDims; clippingPlanes: THREE.Plane[] }) {
  const { L, outerR, nozzles, nozzle } = dims;
  const nzList = nozzles ?? [nozzle];

  return (
    <group>
      <mesh geometry={geometry} castShadow receiveShadow>
        <meshStandardMaterial color="#b8b8b8" metalness={0.6} roughness={0.38} side={THREE.DoubleSide} clippingPlanes={clippingPlanes} />
      </mesh>

      {/* Ölçü etiketleri (project data) */}
      <Label position={[0, outerR + 240, L / 2]}>Boy ≈ {dims.overallLen.toFixed(0)} mm</Label>
      <Label position={[outerR + 260, 0, L / 2]}>Ø dış {dims.outerD.toFixed(0)} mm</Label>
      <Label position={[0, -(outerR + 200), 0]}>◀ sol teğet (z=0)</Label>

      {/* Nozul etiketleri */}
      {nzList.map((nz, i) => {
        const th = (nz.thetaDeg * Math.PI) / 180;
        const nx = nz.tipR * Math.sin(th);
        const ny = nz.tipR * Math.cos(th);
        return (
          <Label key={i} position={[nx, ny + 120, nz.z]}>
            {nz.tag} · z={nz.z} · θ={nz.thetaDeg}° · Ø{nz.od}
          </Label>
        );
      })}
    </group>
  );
}

interface ViewerProps {
  url: string;
  autoRotate: boolean;
  dims: ModelDims;
  section: boolean;
  orientation?: "horizontal" | "vertical";
  onManual?: () => void;
}

import { authFetch } from "./api";

export function VesselViewer({ url, autoRotate, dims, section, onManual }: ViewerProps) {
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const cameraApi = useRef<CameraApi | null>(null);

  // Kesit düzlemi — Y ekseninde üst yarıyı keser (normal aşağı, sabit=0)
  const clipPlane = useMemo(() => new THREE.Plane(new THREE.Vector3(0, -1, 0), 0), []);
  const clippingPlanes = useMemo(() => (section ? [clipPlane] : []), [section, clipPlane]);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    setErr(null);
    authFetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`STL alınamadı (${r.status})`);
        return r.arrayBuffer();
      })
      .then((buf) => {
        if (!alive) return;
        const geo = new STLLoader().parse(buf);
        geo.computeVertexNormals();
        setGeometry(geo);
        setLoading(false);
      })
      .catch((e) => {
        if (!alive) return;
        setErr(e.message ?? "3D model yüklenemedi");
        setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, [url]);

  if (err) {
    return (
      <div className="viewer-msg">
        <div className="empty__mark">⚠</div>
        <p>{err}</p>
      </div>
    );
  }

  if (loading || !geometry) {
    return (
      <div className="viewer-msg">
        <div className="spin" style={{ margin: "0 auto 12px" }} />
        <p>3D model hazırlanıyor…</p>
      </div>
    );
  }

  // Dikey yönelim: modeli 90° döndür (CAD ekseni Z→dikey)
  const isVertical = dims.orientation === "vertical";

  return (
    <div className="viewer-frame">
    <Canvas
      camera={{ position: [2600, 1700, 2900], near: 1, far: 60000, fov: 42 }}
      gl={{ alpha: true, antialias: true, localClippingEnabled: true }}
      dpr={[1, 2]}
    >
      <ambientLight intensity={0.55} />
      <directionalLight position={[1500, 3000, 2000]} intensity={1.3} />
      <directionalLight position={[-2000, -1000, -1500]} intensity={0.35} />
      <hemisphereLight args={["#eeeeee", "#1a1a1a", 0.4]} />

      <Bounds fit clip observe margin={1.35}>
        <group rotation={isVertical ? [-Math.PI / 2, 0, 0] : [0, 0, 0]}>
          <VesselMesh geometry={geometry} dims={dims} clippingPlanes={clippingPlanes} />
        </group>
      </Bounds>

      <CameraRigLayer apiRef={cameraApi} orientation={dims.orientation} onManual={onManual}
        autoRotate={autoRotate && !section} />
      <GizmoHelper alignment="bottom-right" margin={[70, 70]}>
        <GizmoViewport axisColors={["#ef5a63", "#37c98b", "#4aa8e0"]} labelColor="#fafafa" />
      </GizmoHelper>
    </Canvas>
    <CameraToolbar apiRef={cameraApi} onManual={onManual} autoRotate={autoRotate} />
    <CameraHelpNote />
    </div>
  );
}
