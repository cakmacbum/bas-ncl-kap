import React, { useCallback, useRef, useState } from "react";
import { OrbitControls } from "@react-three/drei";
import { useThree } from "@react-three/fiber";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import * as THREE from "three";

type View = "iso" | "top" | "front" | "side";
export type CameraApi = { setView: (view: View) => void; fit: () => void; key: (key: string, shift: boolean) => void };

function CameraRig({ orientation, onReady, onManual, autoRotate }: {
  orientation?: "horizontal" | "vertical";
  onReady: (api: CameraApi) => void;
  onManual?: () => void;
  autoRotate?: boolean;
}) {
  const controls = useRef<OrbitControlsImpl>(null);
  const { camera, scene, size } = useThree();

  const fit = useCallback(() => {
    const box = new THREE.Box3();
    scene.traverse((item) => {
      if ((item as THREE.Mesh).isMesh) box.expandByObject(item);
    });
    if (box.isEmpty()) return;
    const center = box.getCenter(new THREE.Vector3());
    const sphere = box.getBoundingSphere(new THREE.Sphere());
    const distance = Math.max(1, sphere.radius / Math.sin(THREE.MathUtils.degToRad(
      (camera as THREE.PerspectiveCamera).fov / 2,
    )) * 1.2);
    const direction = new THREE.Vector3(1, 0.65, 1).normalize();
    camera.position.copy(center).addScaledVector(direction, distance);
    camera.near = Math.max(0.1, distance / 1000);
    camera.far = distance * 20;
    camera.updateProjectionMatrix();
    controls.current?.target.copy(center);
    controls.current?.update();
  }, [camera, scene, size]);

  const setView = useCallback((view: View) => {
    const box = new THREE.Box3();
    scene.traverse((item) => {
      if ((item as THREE.Mesh).isMesh) box.expandByObject(item);
    });
    if (box.isEmpty()) return;
    const center = box.getCenter(new THREE.Vector3());
    const sphere = box.getBoundingSphere(new THREE.Sphere());
    const distance = Math.max(1, sphere.radius * 2.7);
    const directions: Record<View, THREE.Vector3> = {
      iso: new THREE.Vector3(1, 0.65, 1).normalize(),
      top: new THREE.Vector3(0, 1, 0),
      front: new THREE.Vector3(1, 0, 0),
      side: new THREE.Vector3(0, 0, 1),
    };
    camera.position.copy(center).addScaledVector(directions[view], distance);
    camera.up.copy(view === "top" ? new THREE.Vector3(0, 0, -1) : new THREE.Vector3(0, 1, 0));
    camera.lookAt(center);
    controls.current?.target.copy(center);
    controls.current?.update();
  }, [camera, orientation, scene]);

  const key = useCallback((keyName: string, shift: boolean) => {
    const control = controls.current;
    if (!control) return;
    if (shift && keyName.startsWith("Arrow")) {
      const step = Math.max(1, control.getDistance() * 0.04);
      const direction = new THREE.Vector3();
      camera.getWorldDirection(direction);
      const right = new THREE.Vector3().crossVectors(direction, camera.up).normalize();
      const up = new THREE.Vector3().crossVectors(right, direction).normalize();
      const move = keyName === "ArrowLeft" ? right.clone().negate()
        : keyName === "ArrowRight" ? right
        : keyName === "ArrowUp" ? up : up.clone().negate();
      move.multiplyScalar(step);
      camera.position.add(move);
      control.target.add(move);
      control.update();
    } else if (keyName.startsWith("Arrow")) {
      const angle = Math.PI / 24;
      const offset = camera.position.clone().sub(control.target);
      const spherical = new THREE.Spherical().setFromVector3(offset);
      if (keyName === "ArrowLeft") spherical.theta += angle;
      if (keyName === "ArrowRight") spherical.theta -= angle;
      if (keyName === "ArrowUp") spherical.phi = Math.max(0.05, spherical.phi - angle);
      if (keyName === "ArrowDown") spherical.phi = Math.min(Math.PI - 0.05, spherical.phi + angle);
      camera.position.copy(control.target).add(new THREE.Vector3().setFromSpherical(spherical));
      control.update();
    } else if (["+", "=", "-"].includes(keyName)) {
      camera.position.lerp(control.target, keyName === "-" ? -0.1 : 0.1);
      control.update();
    }
  }, [camera]);

  React.useEffect(() => onReady({ setView, fit, key }), [fit, key, onReady, setView]);

  return <OrbitControls ref={controls} makeDefault enableDamping dampingFactor={0.08}
    autoRotate={autoRotate} autoRotateSpeed={0.8} onStart={onManual} />;
}

export function CameraRigLayer({ orientation, apiRef, onManual, autoRotate }: {
  orientation?: "horizontal" | "vertical";
  apiRef: React.MutableRefObject<CameraApi | null>;
  onManual?: () => void;
  autoRotate?: boolean;
}) {
  const [, rerender] = useState(0);
  const onReady = useCallback((api: CameraApi) => {
    apiRef.current = api;
    rerender((v) => v + 1);
  }, [apiRef]);
  return <CameraRig orientation={orientation} onReady={onReady} onManual={onManual} autoRotate={autoRotate} />;
}

export function CameraToolbar({ apiRef, onManual, onAutoRotateToggle, autoRotate }: {
  apiRef: React.MutableRefObject<CameraApi | null>;
  onManual?: () => void;
  onAutoRotateToggle?: () => void;
  autoRotate?: boolean;
}) {
  const onKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (!event.currentTarget.contains(event.target as Node)) return;
    if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "+", "-", "=", "f", "F", "1", "2", "3", "4"].includes(event.key)) {
      event.preventDefault();
      const key = event.key.toLowerCase();
      if (key === "f") apiRef.current?.fit();
      if (key === "1") apiRef.current?.setView("iso");
      if (key === "2") apiRef.current?.setView("top");
      if (key === "3") apiRef.current?.setView("front");
      if (key === "4") apiRef.current?.setView("side");
      if (event.key.startsWith("Arrow") || ["+", "=", "-"].includes(event.key)) {
        apiRef.current?.key(event.key, event.shiftKey);
      }
      onManual?.();
    }
  };

  return <>
    <div className="camera-toolbar" tabIndex={0} role="group" aria-label="3D kamera kontrolleri"
      onKeyDown={onKeyDown}>
      <div className="camera-toolbar__views" aria-label="Görünüş seçimi">
        {([ ["iso", "İzometrik", "İzo"], ["top", "Üst görünüş", "Üst"], ["front", "Ön görünüş", "Ön"], ["side", "Yan görünüş", "Yan"] ] as const).map(([view, title, label]) =>
          <button key={view} type="button" className="btn btn--sm" title={`${title} (${view === "iso" ? 1 : view === "top" ? 2 : view === "front" ? 3 : 4})`}
            onClick={() => { apiRef.current?.setView(view); onManual?.(); }}>{label}</button>
        )}
        <button type="button" className="btn btn--sm" title="Modeli ekrana sığdır (F)"
          onClick={() => { apiRef.current?.fit(); onManual?.(); }}>Sığdır</button>
      </div>
      {onAutoRotateToggle && <button type="button" className="btn btn--sm"
        aria-pressed={autoRotate} onClick={onAutoRotateToggle}>
        {autoRotate ? "Döndürmeyi durdur" : "Otomatik döndür"}
      </button>}
    </div>
  </>;
}

export function CameraHelpNote() {
  return <div className="camera-help" aria-label="3D modeli kullanma bilgisi">
    <strong>Modeli kullanma:</strong> Sol tuşla sürükle döndür · sağ tuşla (veya Shift + sol tuşla) kaydır · tekerlek/pinç ile yakınlaş.
    Görünüş ve Sığdır düğmelerini kullan; klavyede 1–4 görünüş, F sığdır.
  </div>;
}
