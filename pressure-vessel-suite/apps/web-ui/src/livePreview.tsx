// Anlık 3D önizleme — geometri tarayıcıda üretilir, backend'e gidilmez.
// Yazdıkça (her tuşta) güncellenir; ağ isteği yoktur.
//
// K2: Ölçüler project data'dan gelir, mesh'ten ölçülmez.
// K6: Flanş/kapak biçimleri görsel temsildir (B16.5 ölçüsü değildir).
// Kesin imalat modeli için CadQuery/STEP çıktısı kullanılır.

import React, { useMemo } from "react";
import { Canvas } from "@react-three/fiber";
import { Bounds, GizmoHelper, GizmoViewport, OrbitControls } from "@react-three/drei";
import * as THREE from "three";

import type { Head, Nozzle, ShellSection } from "./types";
import type { DimKey } from "./schematic";
import { nozzlePlacement, nozzleVisual, vesselProfile } from "./vesselModel";

const COLOR_BODY = "#aeb8c4";
const COLOR_ACTIVE = "#f0883e"; // 2D şemadaki turuncu vurgunun 3D karşılığı
const COLOR_NOZZLE = "#9fb0c4";
const COLOR_FLANGE = "#8c9bad";

// Tek koordinat çerçevesi: **model çerçevesi** — kap ekseni = Z, radyal düzlem = XY,
// θ = +X'ten itibaren. Backend `nozzles/position.py` ile aynı sözleşme.
// LatheGeometry Y ekseni etrafında döndürdüğü için gövde geometrisi bir kez
// rotateX(+90) ile bu çerçeveye alınır; başka hiçbir yerde eksen düzeltmesi yoktur.

function VesselBody({
  shell, leftHead, rightHead, active,
}: {
  shell: ShellSection; leftHead: Head; rightHead: Head; active: DimKey;
}) {
  const geometry = useMemo(() => {
    const pts = vesselProfile(shell, leftHead, rightHead).map(
      (p) => new THREE.Vector2(Math.max(p.r, 0), p.z),
    );
    const g = new THREE.LatheGeometry(pts, 72);
    g.rotateX(Math.PI / 2); // lathe Y-eksenel → model Z-eksenel
    return g;
  }, [
    shell.inside_diameter, shell.tangent_length, shell.nominal_thickness,
    leftHead.type, leftHead.straight_flange_length, leftHead.inside_diameter,
    rightHead.type, rightHead.straight_flange_length, rightHead.inside_diameter,
  ]);

  const highlighted =
    active === "Di" || active === "L" || active === "t" ||
    active === "headType" || active === "headDi" || active === "headT" || active === "sf";

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial
        color={highlighted ? COLOR_ACTIVE : COLOR_BODY}
        metalness={0.55}
        roughness={0.42}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

function NozzleMesh({
  nozzle, shell, heads, highlighted,
}: {
  nozzle: Nozzle; shell: ShellSection; heads: Head[]; highlighted: boolean;
}) {
  const parts = useMemo(() => {
    const place = nozzlePlacement(nozzle, shell, heads);
    if (!place) return null;

    const axis = new THREE.Vector3(...place.axis).normalize();
    const anchor = new THREE.Vector3(...place.position);

    // Silindir varsayılanı +Y; ekseni nozul yönüne çevir.
    const quat = new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(0, 1, 0), axis,
    );

    const wall = Math.max(shell.nominal_thickness, 1);
    const outside = Math.max(nozzle.outside_projection, 0);
    const inside = Math.max(nozzle.inside_projection, 0);
    const length = inside + wall + outside;
    const odR = nozzle.outside_diameter / 2;
    const idR = nozzle.inside_diameter / 2;

    // Boru merkezi: çıpadan içeriye `inside`, dışarıya `wall+outside`
    const pipeCenter = anchor.clone().add(
      axis.clone().multiplyScalar(-inside + length / 2),
    );

    const vis = nozzleVisual(nozzle.nozzle_type);
    const flR = odR * vis.flangeRatio;
    const flT = Math.max(odR * vis.flangeThicknessRatio, vis.minThickness);
    const tipDist = wall + outside;

    let fitCenter: THREE.Vector3;
    if (vis.boss) {
      // Kısa boss gövdeye yakın oturur
      fitCenter = anchor.clone().add(axis.clone().multiplyScalar(wall + flT / 2));
    } else {
      const setback = vis.setback ? flT * 0.6 : 0;
      fitCenter = anchor.clone().add(
        axis.clone().multiplyScalar(tipDist - setback - flT / 2),
      );
    }

    return {
      pipe: { center: pipeCenter, quat, odR, idR, length },
      fitting: { center: fitCenter, quat, r: flR, t: flT, blind: vis.blindCover },
    };
  }, [
    nozzle.host_component_id, nozzle.axial_position, nozzle.circumferential_angle,
    nozzle.inclination_angle, nozzle.outside_diameter, nozzle.inside_diameter,
    nozzle.outside_projection, nozzle.inside_projection, nozzle.nozzle_type,
    shell.inside_diameter, shell.tangent_length, shell.nominal_thickness, heads,
  ]);

  if (!parts) return null;
  const { pipe, fitting } = parts;
  const color = highlighted ? COLOR_ACTIVE : COLOR_NOZZLE;

  return (
    <group>
      {/* Boru — içi boş görünsün diye açık uçlu silindir */}
      <mesh position={pipe.center} quaternion={pipe.quat}>
        <cylinderGeometry args={[pipe.odR, pipe.odR, pipe.length, 32, 1, true]} />
        <meshStandardMaterial color={color} metalness={0.55} roughness={0.42}
          side={THREE.DoubleSide} />
      </mesh>
      <mesh position={pipe.center} quaternion={pipe.quat}>
        <cylinderGeometry args={[pipe.idR, pipe.idR, pipe.length * 1.001, 32, 1, true]} />
        <meshStandardMaterial color="#5c6672" metalness={0.3} roughness={0.7}
          side={THREE.BackSide} />
      </mesh>

      {/* Flanş / kapak / boss */}
      <mesh position={fitting.center} quaternion={fitting.quat}>
        <cylinderGeometry args={[fitting.r, fitting.r, fitting.t, 40]} />
        <meshStandardMaterial color={highlighted ? COLOR_ACTIVE : COLOR_FLANGE}
          metalness={0.6} roughness={0.38} />
      </mesh>
      {/* Kör kapak değilse akış deliği görünür kalsın */}
      {!fitting.blind && (
        <mesh position={fitting.center} quaternion={fitting.quat}>
          <cylinderGeometry args={[pipe.idR, pipe.idR, fitting.t * 1.05, 32, 1, true]} />
          <meshStandardMaterial color="#5c6672" metalness={0.3} roughness={0.7}
            side={THREE.BackSide} />
        </mesh>
      )}
    </group>
  );
}

export interface LivePreviewProps {
  shell: ShellSection;
  heads: Head[];
  nozzles: Nozzle[];
  orientation?: string;
  active: DimKey;
  activeNozzle?: number;
}

export function LivePreview({
  shell, heads, nozzles, orientation, active, activeNozzle,
}: LivePreviewProps) {
  const leftHead = heads[0];
  const rightHead = heads[1] ?? heads[0];

  if (!shell || !leftHead) {
    return (
      <div className="viewer-msg">
        <p>Geometri tanımlanmadı.</p>
      </div>
    );
  }

  const isVertical = orientation === "vertical";
  const nozzleActive = active === "nz" || active === "theta" || active === "nd";

  return (
    <div className="live-preview">
      <div className="live-preview__stage">
      <Canvas
        camera={{ position: [2600, 1700, 2900], near: 1, far: 60000, fov: 42 }}
        gl={{ alpha: true, antialias: true }}
        dpr={[1, 2]}
      >
        <ambientLight intensity={0.55} />
        <directionalLight position={[1500, 3000, 2000]} intensity={1.3} />
        <directionalLight position={[-2000, -1000, -1500]} intensity={0.35} />
        <hemisphereLight args={["#dfe7f0", "#1a2230", 0.4]} />

        <Bounds fit clip observe margin={1.3}>
          {/* Tek görüntüleme rotasyonu (model çerçevesi → sahne):
              yatay → θ=0° ekranda üst (2D şemadaki sözleşme),
              dikey → kap ekseni yukarı. */}
          <group rotation={isVertical ? [-Math.PI / 2, 0, 0] : [0, 0, Math.PI / 2]}>
            <VesselBody shell={shell} leftHead={leftHead} rightHead={rightHead}
              active={active} />
            {nozzles.map((nz, i) => (
              <NozzleMesh
                key={`${nz.tag}-${i}`}
                nozzle={nz}
                shell={shell}
                heads={heads}
                highlighted={nozzleActive && activeNozzle === i}
              />
            ))}
          </group>
        </Bounds>

        <OrbitControls makeDefault enableDamping dampingFactor={0.08} />
        <GizmoHelper alignment="bottom-right" margin={[64, 64]}>
          <GizmoViewport axisColors={["#ef5a63", "#37c98b", "#4aa8e0"]}
            labelColor="#e6edf5" />
        </GizmoHelper>
      </Canvas>
      </div>

      <p className="preview-note">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2" aria-hidden="true">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        Önizleme — kesin imalat modeli değildir. Flanş/kapak biçimleri temsilidir;
        ölçülendirilmiş model için <strong>Kesin Modeli Yükle</strong>.
      </p>
    </div>
  );
}
