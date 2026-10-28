// Anlık 3D önizleme — geometri tarayıcıda üretilir, backend'e gidilmez.
// Yazdıkça (her tuşta) güncellenir; ağ isteği yoktur.
//
// K2: Ölçüler project data'dan gelir, mesh'ten ölçülmez.
// K6: Flanş/kapak biçimleri görsel temsildir (B16.5 ölçüsü değildir).
// Kesin imalat modeli için CadQuery/STEP çıktısı kullanılır.

import { useEffect, useMemo, useRef, type CSSProperties } from "react";
import { Canvas } from "@react-three/fiber";
import { Bounds, GizmoHelper, GizmoViewport } from "@react-three/drei";
import * as THREE from "three";
import { CameraHelpNote, CameraRigLayer, CameraToolbar, type CameraApi } from "./cameraToolbar";

import type { ComponentReference, Cone, Head, Nozzle, ShellSection } from "./types";
import type { MeshPart, Selection } from "./geometryContract";
import { useCadBuild } from "./cad/cadClient";
import { useStore } from "./store";
import type { DimKey } from "./schematic";
import {
  componentFrames, nozzlePlacement, nozzleVisual, vesselProfile, vesselProfileChain,
  type ChainSource, type ComponentFrame,
} from "./vesselModel";

const COLOR_BODY = "#b8b8b8";
const COLOR_ACTIVE = "#4d8bff";
const COLOR_NOZZLE = "#a8a8a8";
const COLOR_FLANGE = "#8f8f8f";

// Tek koordinat çerçevesi: **model çerçevesi** — kap ekseni = Z, radyal düzlem = XY,
// θ = +X'ten itibaren. Backend `nozzles/position.py` ile aynı sözleşme.
// LatheGeometry Y ekseni etrafında döndürdüğü için gövde geometrisi bir kez
// rotateX(+90) ile bu çerçeveye alınır; başka hiçbir yerde eksen düzeltmesi yoktur.

function VesselBody({
  shell, leftHead, rightHead, shells, cones, sequence, heads, active,
}: {
  shell: ShellSection; shells: ShellSection[]; leftHead: Head; rightHead: Head; cones: Cone[];
  sequence: ComponentReference[]; heads: Head[]; active: DimKey;
}) {
  const geometry = useMemo(() => {
    const profile = sequence.length > 0
      ? vesselProfileChain(shells, heads, cones, sequence)
      : vesselProfile(shell, leftHead, rightHead);
    const pts = profile.map(
      (p) => new THREE.Vector2(Math.max(p.r, 0), p.z),
    );
    const g = new THREE.LatheGeometry(pts, 72);
    g.rotateX(Math.PI / 2); // lathe Y-eksenel → model Z-eksenel
    return g;
  }, [
    shell.inside_diameter, shell.tangent_length, shell.nominal_thickness,
    leftHead.type, leftHead.straight_flange_length, leftHead.inside_diameter,
    rightHead.type, rightHead.straight_flange_length, rightHead.inside_diameter,
    shells, cones, sequence, heads,
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
  nozzle, chain, frames, highlighted,
}: {
  nozzle: Nozzle; chain: ChainSource; frames: ComponentFrame[]; highlighted: boolean;
}) {
  const parts = useMemo(() => {
    // Her nozul kendi host çerçevesine göre yerleşir (aktif gövde kısıtı yok).
    const place = nozzlePlacement(chain, nozzle, frames);
    if ("error" in place) return null;

    const axis = new THREE.Vector3(...place.axis).normalize();
    const anchor = new THREE.Vector3(...place.position);

    // Silindir varsayılanı +Y; ekseni nozul yönüne çevir.
    const quat = new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(0, 1, 0), axis,
    );

    const wall = Math.max(place.frame.thickness, 1);
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
  }, [nozzle, chain, frames]);

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
        <meshStandardMaterial color="#5c5c5c" metalness={0.3} roughness={0.7}
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
          <meshStandardMaterial color="#5c5c5c" metalness={0.3} roughness={0.7}
            side={THREE.BackSide} />
        </mesh>
      )}
    </group>
  );
}

const KIND_COLOR: Record<MeshPart["kind"], string> = {
  shell: "#b8b8b8", cone: "#b0b4b8", head: "#b4b4b4", nozzle: "#a8a8a8", support: "#8a7f6e",
};

/** Worker (OCCT) mesh'leri: partId başına bir mesh; tık → seçim, seçili parça vurgulu. */
export function CadMeshes({
  meshes, selection, onSelect,
}: {
  meshes: MeshPart[]; selection: Selection | null; onSelect: (s: Selection) => void;
}) {
  const geos = useMemo(
    () => meshes.map((m) => {
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(m.positions, 3));
      g.setAttribute("normal", new THREE.BufferAttribute(m.normals, 3));
      g.setIndex(new THREE.BufferAttribute(m.indices, 1));
      let edges: THREE.BufferGeometry | null = null;
      if (m.edges && m.edges.length) {
        edges = new THREE.BufferGeometry();
        edges.setAttribute("position", new THREE.BufferAttribute(m.edges, 3));
      }
      return { g, edges };
    }),
    [meshes],
  );
  useEffect(() => () => geos.forEach(({ g, edges }) => { g.dispose(); edges?.dispose(); }), [geos]);

  return (
    <group>
      {meshes.map((m, i) => {
        const id = m.partId.slice(m.partId.indexOf(":") + 1);
        const selected = selection?.kind === m.kind && selection.id === id;
        return (
          <group key={m.partId}>
            <mesh geometry={geos[i].g}
              onClick={(e) => { e.stopPropagation(); onSelect({ kind: m.kind, id }); }}>
              <meshStandardMaterial color={selected ? COLOR_ACTIVE : KIND_COLOR[m.kind]}
                emissive={selected ? COLOR_ACTIVE : "#000000"} emissiveIntensity={selected ? 0.25 : 0}
                metalness={0.55} roughness={0.42} side={THREE.DoubleSide} />
            </mesh>
            {geos[i].edges && (
              <lineSegments geometry={geos[i].edges!}>
                <lineBasicMaterial color={selected ? "#1d4fb3" : "#3a3a3a"} />
              </lineSegments>
            )}
          </group>
        );
      })}
    </group>
  );
}

const BADGES: CSSProperties = {
  position: "absolute", top: 8, left: 8, zIndex: 5, display: "flex", gap: 6, flexWrap: "wrap",
  fontSize: 11, pointerEvents: "none",
};
const CHIP: CSSProperties = {
  padding: "2px 8px", borderRadius: 999, background: "rgba(20,20,20,.78)", color: "#fafafa",
  border: "1px solid rgba(255,255,255,.18)", pointerEvents: "auto",
};

export interface LivePreviewProps {
  shell: ShellSection;
  shells?: ShellSection[];
  heads: Head[];
  cones?: Cone[];
  componentSequence?: ComponentReference[];
  nozzles: Nozzle[];
  orientation?: string;
  active: DimKey;
  activeNozzle?: number;
}

export function LivePreview({
  shell, heads, nozzles, orientation, active, activeNozzle,
  shells = [shell], cones = [], componentSequence = [],
}: LivePreviewProps) {
  const leftHead = heads[0];
  const rightHead = heads[1] ?? heads[0];

  // Worker (OCCT) geometrisi; hazır olana dek aşağıdaki lathe+nozul çizimi yer tutucu kalır.
  const project = useStore((s) => s.project);
  const selection = useStore((s) => s.selection);
  const setSelection = useStore((s) => s.setSelection);
  const cad = useCadBuild(project, "preview");
  const useCad = cad.meshes.length > 0;

  if (!shell || !leftHead) {
    return (
      <div className="viewer-msg">
        <p>Geometri tanımlanmadı.</p>
      </div>
    );
  }

  const isVertical = orientation === "vertical";
  const nozzleActive = active === "nz" || active === "theta" || active === "nd";
  const cameraApi = useRef<CameraApi | null>(null);
  const chain = useMemo<ChainSource>(
    () => ({ shell_sections: shells, heads, cones, component_sequence: componentSequence }),
    [shells, heads, cones, componentSequence],
  );
  const frames = useMemo(() => componentFrames(chain), [chain]);

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
        <hemisphereLight args={["#eeeeee", "#1a1a1a", 0.4]} />

        <Bounds fit clip margin={1.3}>
          {/* Tek görüntüleme rotasyonu (model çerçevesi → sahne):
              yatay → θ=0° ekranda üst (2D şemadaki sözleşme),
              dikey → kap ekseni yukarı. */}
          <group rotation={isVertical ? [-Math.PI / 2, 0, 0] : [0, 0, Math.PI / 2]}>
            {useCad ? (
              <CadMeshes meshes={cad.meshes} selection={selection} onSelect={setSelection} />
            ) : (
              <>
                <VesselBody shell={shell} shells={shells} leftHead={leftHead} rightHead={rightHead}
                  cones={cones} sequence={componentSequence} heads={heads}
                  active={active} />
                {nozzles.map((nz, i) => (
                  <NozzleMesh
                    key={`${nz.tag}-${i}`}
                    nozzle={nz}
                    chain={chain}
                    frames={frames}
                    highlighted={nozzleActive && activeNozzle === i}
                  />
                ))}
              </>
            )}
          </group>
        </Bounds>

        <CameraRigLayer apiRef={cameraApi} orientation={isVertical ? "vertical" : "horizontal"} />
        <GizmoHelper alignment="bottom-right" margin={[64, 64]}>
          <GizmoViewport axisColors={["#ef5a63", "#37c98b", "#4aa8e0"]}
            labelColor="#fafafa" />
        </GizmoHelper>
      </Canvas>
      </div>

      <div style={BADGES} aria-live="polite">
        {(cad.status === "loading" || (cad.status === "building" && !useCad)) && (
          <span style={CHIP}>3D motor yükleniyor…</span>
        )}
        {cad.status === "error" && (
          <span style={{ ...CHIP, background: "rgba(160,40,40,.85)" }} title={cad.error ?? undefined}>
            3D motor hatası — basit önizleme
          </span>
        )}
        {cad.warnings.length > 0 && (
          <span style={{ ...CHIP, background: "rgba(150,100,10,.88)" }}
            title={cad.warnings.map((w) => w.message).join("\n")}>
            ⚠ {cad.warnings.length} uyarı
          </span>
        )}
      </div>

      <CameraToolbar apiRef={cameraApi} />
      <CameraHelpNote />

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
