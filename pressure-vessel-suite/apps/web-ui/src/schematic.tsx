import React from "react";
import { HEAD_TYPE_TR, NOZZLE_TYPE_TR } from "./i18n";
import { headDepth } from "./vesselModel";
import type { ComponentReference, Cone, Head, ShellSection } from "./types";

// Kabın ölçülü kesit şeması — geometri girdilerinden canlı üretilir.
// Düzenlenen alan `active` ile vurgulanır. Sadece görsel/eğitseldir (K2: ölçü kaynağı project data).

export type DimKey =
  | "Di" | "L" | "t" | "sf" | "headType" | "headT" | "headDi"
  | "nz" | "theta" | "nd" | "";

interface NozzleInfo {
  tag: string;
  z: number;         // eksenel konum (mm)
  theta: number;     // çevresel açı (derece)
  od: number;        // dış çap (mm)
  host: string;      // "SHELL-01" | "HEAD-L" | "HEAD-R"
  nozzle_type?: string;
}

interface Props {
  leftDi: number;
  rightDi: number;
  di: number;             // iç çap (mm)
  L: number;              // teğet boyu (mm)
  t: number;              // et kalınlığı (mm)
  straightFlange: number; // düz flanş (mm)
  leftStraightFlange?: number;
  rightStraightFlange?: number;
  leftHeadType: string;
  rightHeadType: string;
  leftHeadT?: number;     // sol bombe kalınlığı (mm)
  rightHeadT?: number;    // sağ bombe kalınlığı (mm)
  nozzles: NozzleInfo[];
  activeNozzle?: number;  // aktif nozul index'i
  active: DimKey;
  orientation?: "horizontal" | "vertical";
  chain?: {
    sequence: ComponentReference[];
    shells: ShellSection[];
    heads: Head[];
    cones: Cone[];
  };
}

function ChainSchematic({ chain, orientation = "horizontal" }: {
  chain: NonNullable<Props["chain"]>;
  orientation?: "horizontal" | "vertical";
}) {
  const VBW = 480, VBH = 320, pad = 42;
  const byId = {
    shell: new Map(chain.shells.map((x) => [x.section_id, x])),
    head: new Map(chain.heads.map((x) => [x.head_id, x])),
    cone: new Map(chain.cones.map((x) => [x.cone_id, x])),
  };
  const lengthOf = (ref: ComponentReference) => {
    if (ref.component_type === "shell") return byId.shell.get(ref.component_id)?.tangent_length ?? 1;
    if (ref.component_type === "cone") return byId.cone.get(ref.component_id)?.length ?? 1;
    const h = byId.head.get(ref.component_id);
    return h ? headDepth(h.inside_diameter, h.type, h.straight_flange_length ?? 0) : 1;
  };
  const diameterOf = (ref: ComponentReference) => {
    if (ref.component_type === "shell") return byId.shell.get(ref.component_id)?.inside_diameter ?? 1;
    if (ref.component_type === "cone") {
      const c = byId.cone.get(ref.component_id);
      return c ? Math.max(c.large_diameter, c.small_diameter) : 1;
    }
    return byId.head.get(ref.component_id)?.inside_diameter ?? 1;
  };
  const total = Math.max(chain.sequence.reduce((sum, ref) => sum + lengthOf(ref), 0), 1);
  const maxD = Math.max(...chain.sequence.map(diameterOf), 1);
  const scale = Math.min((VBW - 2 * pad) / total, (VBH - 110) / maxD);
  const cy = 160;
  let cursor = pad;
  const parts = chain.sequence.map((ref) => {
    const len = lengthOf(ref) * scale;
    const d = diameterOf(ref) * scale;
    const top = cy - d / 2;
    const item = { ref, x: cursor, len, top, d };
    cursor += len;
    return item;
  });
  return (
    <svg className="schematic" viewBox={`0 0 ${VBW} ${VBH}`} role="img"
      aria-label="Çok elemanlı kap zinciri kesit şeması">
      <text x={pad} y={22} className="sch-title">Eleman zinciri · {orientation === "vertical" ? "dikey" : "yatay"} kesit</text>
      {parts.map(({ ref, x, len, top, d }, index) => {
        const label = ref.component_id;
        const isCone = ref.component_type === "cone";
        const isLeftHead = ref.component_type === "head" && index === 0;
        const isRightHead = ref.component_type === "head" && index === parts.length - 1;
        const cone = isCone ? byId.cone.get(ref.component_id) : undefined;
        const leftD = cone?.large_diameter ?? diameterOf(ref);
        const rightD = cone?.small_diameter ?? diameterOf(ref);
        const leftH = leftD * scale;
        const rightH = rightD * scale;
        const fill = ref.component_type === "cone" ? "var(--review-bg)" : "var(--panel-2)";
        return (
          <g key={`${ref.component_type}-${ref.component_id}`}>
            {ref.component_type === "head" ? (
              <path className="sch-part" d={isLeftHead
                ? `M ${x + len} ${cy - d / 2} Q ${x + len * 0.08} ${cy} ${x + len} ${cy + d / 2} Z`
                : isRightHead
                  ? `M ${x} ${cy - d / 2} Q ${x + len * 0.92} ${cy} ${x} ${cy + d / 2} Z`
                  : `M ${x} ${cy - d / 2} L ${x + len} ${cy - d / 2} L ${x + len} ${cy + d / 2} L ${x} ${cy + d / 2} Z`} fill={fill} />
            ) : isCone ? (
              <polygon className="sch-part" points={`${x},${cy - leftH / 2} ${x + len},${cy - rightH / 2} ${x + len},${cy + rightH / 2} ${x},${cy + leftH / 2}`} fill={fill} />
            ) : (
              <rect className="sch-part" x={x} y={top} width={len} height={d} fill={fill} />
            )}
            <line className="sch-tangent" x1={x} y1={top - 5} x2={x} y2={cy + d / 2 + 5} />
            <text className="sch-small" x={x + len / 2} y={cy + d / 2 + 24} textAnchor="middle">{label}</text>
          </g>
        );
      })}
      <text className="sch-small" x={VBW - pad} y={VBH - 20} textAnchor="end">{chain.sequence.length} eleman · ölçeksiz görsel profil</text>
    </svg>
  );
}

// Bombe derinliği paylaşılan modülden gelir (2D şema, 3D önizleme ve ölçü
// etiketleri aynı kaynağı kullanır — K2).

// Bombe profil SVG path'i üret
function headPath(
  type: string,
  side: "left" | "right",
  x: number,       // teğet çizgisi x koordinatı
  topY: number,
  botY: number,
  hd: number,       // bombe derinliği (px)
  bodyH: number,    // gövde yüksekliği (px)
): string {
  const sweep = side === "left" ? 0 : 1;
  const dir = side === "left" ? -1 : 1;

  switch (type) {
    case "elliptical": {
      // 2:1 elips yayı — standart
      return `M ${x} ${topY} A ${hd} ${bodyH / 2} 0 0 ${sweep} ${x} ${botY}`;
    }
    case "torisferik":
    case "torispherical": {
      // Torisferik: daha sığ, knuckle etkisi — iki arc
      const knuckle = hd * 0.35;
      const crown = hd * 0.85;
      const midY = (topY + botY) / 2;
      // Üst knuckle → crown → alt knuckle
      return `M ${x} ${topY} Q ${x + dir * knuckle} ${topY + bodyH * 0.15} ${x + dir * crown} ${midY} Q ${x + dir * knuckle} ${botY - bodyH * 0.15} ${x} ${botY}`;
    }
    case "hemispherical": {
      // Yarım daire — derinlik = yarıçap
      const r = bodyH / 2;
      return `M ${x} ${topY} A ${r} ${r} 0 0 ${sweep} ${x} ${botY}`;
    }
    case "flat": {
      // Düz kapak — dik çizgi (iç cidar hattı)
      return `M ${x} ${topY} L ${x} ${botY}`;
    }
    default:
      return `M ${x} ${topY} A ${hd} ${bodyH / 2} 0 0 ${sweep} ${x} ${botY}`;
  }
}

// Düz bombe için dolgu dikdörtgeni
function flatHeadRect(
  side: "left" | "right",
  x: number,
  topY: number,
  botY: number,
  hd: number,
  wall: number,
): { x: number; y: number; w: number; h: number } | null {
  if (side === "left") {
    return { x: x - Math.max(hd, wall * 2), y: topY, w: Math.max(hd, wall * 2), h: botY - topY };
  }
  return { x: x, y: topY, w: Math.max(hd, wall * 2), h: botY - topY };
}

export function VesselSchematic(props: Props) {
  const {
    di, leftDi, rightDi, L, t, straightFlange,
    leftStraightFlange = straightFlange, rightStraightFlange = straightFlange,
    leftHeadType, rightHeadType,
    leftHeadT, rightHeadT,
    nozzles, activeNozzle,
    active, orientation = "horizontal",
  } = props;

  if (props.chain && props.chain.sequence.length > 3) {
    return <ChainSchematic chain={props.chain} orientation={orientation} />;
  }

  const VBW = 480, VBH = 320;
  const padL = 78, padR = 34, padT = 74, padB = 60;
  const availW = VBW - padL - padR;
  const availH = VBH - padT - padB;

  // Sol ve sağ bombe derinlikleri (tip bazlı)
  const leftHD = headDepth(leftDi, leftHeadType, leftStraightFlange);
  const rightHD = headDepth(rightDi, rightHeadType, rightStraightFlange);
  const maxHD = Math.max(leftHD, rightHD);

  const totalLenMM = Math.max(L + leftHD + rightHD, 1);
  const dImm = Math.max(di, leftDi, rightDi, 1);

  const isVertical = orientation === "vertical";

  // Dikey: genişlik/yükseklik takası
  const s = isVertical
    ? Math.min(availW / dImm, availH / totalLenMM)
    : Math.min(availW / totalLenMM, availH / dImm);

  const bodyH = Math.max(di, 1) * s;
  const cY = padT + availH / 2;
  const cX = padL + availW / 2;

  // Yatay düzen (dikeyde x/y rolleri swap edilir)
  const x0 = padL + leftHD * s;          // sol teğet çizgisi
  const x1 = x0 + L * s;                 // sağ teğet çizgisi
  const topY = cY - bodyH / 2;
  const botY = cY + bodyH / 2;
  const leftTopY = cY - Math.max(leftDi, 1) * s / 2;
  const leftBotY = cY + Math.max(leftDi, 1) * s / 2;
  const rightTopY = cY - Math.max(rightDi, 1) * s / 2;
  const rightBotY = cY + Math.max(rightDi, 1) * s / 2;
  const lhd = leftHD * s;
  const rhd = rightHD * s;
  const wall = Math.max(t * s, 2.5);

  // Bombe path'leri (tip bazlı)
  const leftHeadPath = headPath(leftHeadType, "left", x0, leftTopY, leftBotY, lhd, leftBotY - leftTopY);
  const rightHeadPath = headPath(rightHeadType, "right", x1, rightTopY, rightBotY, rhd, rightBotY - rightTopY);

  // Düz bombe dikdörtgenleri
  const leftFlat = leftHeadType === "flat" ? flatHeadRect("left", x0, leftTopY, leftBotY, lhd, wall) : null;
  const rightFlat = rightHeadType === "flat" ? flatHeadRect("right", x1, rightTopY, rightBotY, rhd, wall) : null;

  const A = (k: DimKey) => (active === k ? "sch-dim sch-active" : "sch-dim");
  const P = (k: DimKey) => (active === k ? "sch-part sch-active" : "sch-part");

  // Bombe vurgu kontrolü
  const isHeadActive = active === "headType" || active === "headT" || active === "headDi" || active === "sf";

  // Başlık metni
  const leftLabel = HEAD_TYPE_TR[leftHeadType] ?? leftHeadType;
  const rightLabel = HEAD_TYPE_TR[rightHeadType] ?? rightHeadType;
  const headLabel = leftHeadType === rightHeadType
    ? `${leftLabel} bombe`
    : `Sol: ${leftLabel} · Sağ: ${rightLabel}`;

  return (
    <svg className="schematic" viewBox={`0 0 ${VBW} ${VBH}`} role="img"
      aria-label="Kap kesit şeması">
      {/* ---- Gövde ---- */}
      <rect className={P("t")} x={x0} y={topY} width={L * s} height={bodyH}
        fill="var(--panel-2)" />
      {/* iç cidar (et kalınlığı) */}
      <rect x={x0} y={topY + wall} width={L * s} height={bodyH - 2 * wall}
        fill="var(--bg)" stroke="none" />

      {/* ---- Bombeler ---- */}
      {leftFlat ? (
        <rect className={isHeadActive ? "sch-part sch-active" : "sch-part"}
          x={leftFlat.x} y={leftFlat.y} width={leftFlat.w} height={leftFlat.h}
          fill="var(--panel-2)" />
      ) : (
        <path className={isHeadActive ? "sch-part sch-active" : "sch-part"}
          d={leftHeadPath} fill="var(--panel-2)" />
      )}
      {rightFlat ? (
        <rect className={isHeadActive ? "sch-part sch-active" : "sch-part"}
          x={rightFlat.x} y={rightFlat.y} width={rightFlat.w} height={rightFlat.h}
          fill="var(--panel-2)" />
      ) : (
        <path className={isHeadActive ? "sch-part sch-active" : "sch-part"}
          d={rightHeadPath} fill="var(--panel-2)" />
      )}

      {/* teğet çizgileri (ince kesikli) */}
      <line className="sch-tangent" x1={x0} y1={topY - 8} x2={x0} y2={botY + 8} />
      <line className="sch-tangent" x1={x1} y1={topY - 8} x2={x1} y2={botY + 8} />

      {/* ---- Nozullar (çoklu) ---- */}
      {nozzles.map((nz, idx) => {
        const nzX = x0 + Math.max(0, Math.min(nz.z, L)) * s;
        const nzW = Math.max(nz.od * s, 6);
        const nzTop = topY - 34 - (idx * 18); // üst üste binmeyi önle
        const isActive = active === "nd" || activeNozzle === idx;
        const hostOnHead = nz.host === "HEAD-L" || nz.host === "HEAD-R";
        const tag = nz.tag || `N${idx + 1}`;

        if (hostOnHead) {
          // Bombe üzerindeki nozul — bombe ucunda göster
          const headX = nz.host === "HEAD-L" ? x0 - lhd * 0.5 : x1 + rhd * 0.5;
          return (
            <g key={idx}>
              <line className={isActive ? "sch-part sch-active" : "sch-part"}
                x1={headX - nzW / 2} y1={topY - 20} x2={headX + nzW / 2} y2={topY - 20}
                stroke="var(--line-strong)" strokeWidth={2} />
              <text className={isActive ? "sch-tag sch-active" : "sch-tag"}
                x={headX} y={topY - 26} textAnchor="middle">
                {tag} · Ø{nz.od}
              </text>
            </g>
          );
        }

        return (
          <g key={idx}>
            <rect className={isActive ? "sch-part sch-active" : "sch-part"}
              x={nzX - nzW / 2} y={nzTop} width={nzW} height={topY - nzTop}
              fill="var(--panel-raised)" />
            <text className={isActive ? "sch-tag sch-active" : "sch-tag"}
              x={nzX} y={nzTop - 5} textAnchor="middle">
              {tag} · Ø{nz.od}
            </text>
          </g>
        );
      })}

      {/* ---- Ölçüler ---- */}
      {/* İç çap D_i (sol dikey) */}
      <g className={A("Di")}>
        <line x1={padL - 20} y1={topY} x2={padL - 20} y2={botY} markerStart="url(#a)" markerEnd="url(#a)" />
        <line x1={padL - 20} y1={topY} x2={x0} y2={topY} className="sch-ext" />
        <line x1={padL - 20} y1={botY} x2={x0} y2={botY} className="sch-ext" />
        <text x={padL - 26} y={cY} textAnchor="end" dominantBaseline="middle"
          transform={`rotate(-90 ${padL - 26} ${cY})`}>Ø iç {di} mm</text>
      </g>

      {/* Teğet boyu L (alt) */}
      <g className={A("headDi")}>
        <line x1={x0 - 8} y1={leftTopY} x2={x0 - 8} y2={leftBotY} markerStart="url(#a)" markerEnd="url(#a)" />
        <line x1={x0 - 8} y1={leftTopY} x2={x0} y2={leftTopY} className="sch-ext" />
        <line x1={x0 - 8} y1={leftBotY} x2={x0} y2={leftBotY} className="sch-ext" />
        <text x={x0 - 12} y={cY - 4} textAnchor="end" className="sch-small">Sol Di {leftDi} mm</text>
        <line x1={x1 + 8} y1={rightTopY} x2={x1 + 8} y2={rightBotY} markerStart="url(#a)" markerEnd="url(#a)" />
        <line x1={x1} y1={rightTopY} x2={x1 + 8} y2={rightTopY} className="sch-ext" />
        <line x1={x1} y1={rightBotY} x2={x1 + 8} y2={rightBotY} className="sch-ext" />
        <text x={x1 + 12} y={cY - 4} textAnchor="start" className="sch-small">Sag Di {rightDi} mm</text>
      </g>

      <g className={A("L")}>
        <line x1={x0} y1={botY + 30} x2={x1} y2={botY + 30} markerStart="url(#a)" markerEnd="url(#a)" />
        <line x1={x0} y1={botY} x2={x0} y2={botY + 34} className="sch-ext" />
        <line x1={x1} y1={botY} x2={x1} y2={botY + 34} className="sch-ext" />
        <text x={(x0 + x1) / 2} y={botY + 44} textAnchor="middle">Teğet boyu {L} mm</text>
      </g>

      {/* Et kalınlığı t (sağ üst leader) */}
      <g className={A("t")}>
        <line x1={x1 - 4} y1={topY + wall / 2} x2={x1 + 26} y2={topY - 20} className="sch-leader" />
        <text x={x1 + 28} y={topY - 22} textAnchor="start">t = {t} mm</text>
      </g>

      {/* Bombe kalınlığı (sol bombe üst leader) */}
      {(leftHeadT != null || rightHeadT != null) && (
        <g className={A("headT")}>
          <line x1={x0 + 4} y1={topY + wall / 2} x2={x0 - 26} y2={topY - 20} className="sch-leader" />
          <text x={x0 - 28} y={topY - 22} textAnchor="end">
            bombe t = {leftHeadT ?? rightHeadT} mm
          </text>
        </g>
      )}

      {/* Düz flanş (sağ bombe dibi) */}
      <g className={A("sf")}>
        <line x1={x0 - lhd} y1={leftBotY + 12} x2={x0} y2={leftBotY + 12} markerStart="url(#a)" markerEnd="url(#a)" />
        <text x={x0 - lhd / 2} y={leftBotY + 10} textAnchor="middle" className="sch-small">sol etek {leftStraightFlange}</text>
        <line x1={x1} y1={rightBotY + 12} x2={x1 + rhd} y2={rightBotY + 12} markerStart="url(#a)" markerEnd="url(#a)" />
        <text x={x1 + rhd / 2} y={rightBotY + 10} textAnchor="middle" className="sch-small">sağ etek {rightStraightFlange}</text>
      </g>

      {/* İlk nozul z ölçüsü (üst) — yalnızca en az 1 nozul varsa */}
      {nozzles.length > 0 && (() => {
        const nz = nozzles[0];
        const nzX = x0 + Math.max(0, Math.min(nz.z, L)) * s;
        const nzTop = topY - 34;
        return (
          <g className={A("nz")}>
            <line x1={x0} y1={nzTop - 16} x2={nzX} y2={nzTop - 16} markerStart="url(#a)" markerEnd="url(#a)" />
            <line x1={x0} y1={topY} x2={x0} y2={nzTop - 20} className="sch-ext" />
            <line x1={nzX} y1={nzTop} x2={nzX} y2={nzTop - 20} className="sch-ext" />
            <text x={(x0 + nzX) / 2} y={nzTop - 20} textAnchor="middle" className="sch-small">z = {nz.z}</text>
          </g>
        );
      })()}

      {/* θ kesit göstergesi (sağ üst mini daire) — aktif nozulun açısı */}
      {nozzles.length > 0 && (() => {
        const nz = nozzles[activeNozzle ?? 0] ?? nozzles[0];
        return (
          <g className={A("theta")} transform={`translate(${VBW - 42} ${44})`}>
            <circle r="20" fill="var(--panel-2)" stroke="var(--line-strong)" />
            <line x1="0" y1="0" x2="0" y2="-20" className="sch-ext" />
            <line x1="0" y1="0"
              x2={20 * Math.sin((nz.theta * Math.PI) / 180)}
              y2={-20 * Math.cos((nz.theta * Math.PI) / 180)} />
            <text x="0" y="34" textAnchor="middle" className="sch-small">θ = {nz.theta}°</text>
          </g>
        );
      })()}

      {/* başlık */}
      <text x={padL} y={20} className="sch-title">
        {headLabel} · {isVertical ? "dikey" : "yatay"} kesit
      </text>

      <defs>
        <marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
          <path d="M1,1 L7,4 L1,7" fill="none" stroke="currentColor" strokeWidth="1" />
        </marker>
      </defs>
    </svg>
  );
}
