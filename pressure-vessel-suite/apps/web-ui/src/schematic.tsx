import { HEAD_TYPE_TR } from "./i18n";
import { chainIssues, componentFrames, headDepth, nozzlePlacement, type ChainSource, type ComponentFrame } from "./vesselModel";
import type { Nozzle } from "./types";

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
  /** Çok elemanlı zincir: ölçekli çerçeve profili; seçili parça/nozul vurgulanır. */
  chain?: ChainSource & {
    nozzles?: Nozzle[];
    selectedId?: string | null;
    selectedNozzle?: string | null;
    onSelect?: (kind: ComponentFrame["kind"], id: string) => void;
    onSelectNozzle?: (tag: string) => void;
  };
}

function ChainSchematic({ chain, orientation = "horizontal" }: {
  chain: NonNullable<Props["chain"]>;
  orientation?: "horizontal" | "vertical";
}) {
  const frames = componentFrames(chain);
  const VBW = 480, VBH = 320, pad = 42;
  const total = Math.max(frames.length ? frames[frames.length - 1].zEnd : 1, 1);
  const maxR = Math.max(...frames.map((f) => Math.max(f.rOutStart, f.rOutEnd)), 1);
  const scale = Math.min((VBW - 2 * pad) / total, (VBH - 120) / (2 * maxR));
  const cy = 165;
  const X = (z: number) => pad + z * scale;
  const issues = chainIssues(chain, frames);

  const outline = (f: ComponentFrame): string => {
    const t = f.thickness;
    let top: [number, number][];
    if (f.kind === "head" && f.head) {
      const { side, domeHeight: h, sf } = f.head;
      const ri = side === "left" ? f.rInEnd : f.rInStart;
      const N = 14;
      top = [];
      if (h <= 0) {
        const w = Math.max(sf, t, 3 / scale);
        top = side === "left" ? [[f.zStart, ri + t], [f.zStart + w, ri + t]] : [[f.zEnd - w, ri + t], [f.zEnd, ri + t]];
      } else if (side === "left") {
        for (let i = 0; i <= N; i++) {
          const u = i / N;
          top.push([f.zStart + h * (1 - Math.cos((u * Math.PI) / 2)), h > 0 ? (ri + t) * Math.sin((u * Math.PI) / 2) : ri + t]);
        }
        if (sf > 0) top.push([f.zEnd, ri + t]);
      } else {
        if (sf > 0) top.push([f.zStart, ri + t]);
        for (let i = 0; i <= N; i++) {
          const u = i / N;
          top.push([f.zStart + sf + h * Math.sin((u * Math.PI) / 2), h > 0 ? (ri + t) * Math.cos((u * Math.PI) / 2) : ri + t]);
        }
      }
    } else {
      top = [[f.zStart, f.rOutStart], [f.zEnd, f.rOutEnd]];
    }
    const upper = top.map(([z, r]) => `${X(z).toFixed(1)},${(cy - r * scale).toFixed(1)}`);
    const lower = [...top].reverse().map(([z, r]) => `${X(z).toFixed(1)},${(cy + r * scale).toFixed(1)}`);
    return [...upper, ...lower].join(" ");
  };

  const nozzles = (chain.nozzles ?? []).map((nz, i) => {
    const res = nozzlePlacement(chain, nz, frames);
    return { nz, i, res };
  });

  return (
    <svg className="schematic" viewBox={`0 0 ${VBW} ${VBH}`} role="img"
      aria-label="Çok elemanlı kap zinciri kesit şeması">
      <text x={pad} y={22} className="sch-title">Eleman zinciri · {orientation === "vertical" ? "dikey" : "yatay"} kesit</text>
      {frames.map((f) => {
        const selected = chain.selectedId === f.id;
        const bad = issues.some((x) => x.id === f.id && x.code === "DIAMETER_MISMATCH");
        const fill = f.kind === "cone" ? "var(--review-bg)" : "var(--panel-2)";
        const x0 = X(f.zStart);
        const x1 = X(f.zEnd);
        const dTop = cy - Math.max(f.rOutStart, f.rOutEnd) * scale;
        return (
          <g key={f.id} className={`sch-chain-part${chain.onSelect ? " is-clickable" : ""}`}
            onClick={chain.onSelect ? () => chain.onSelect!(f.kind, f.id) : undefined}>
            <polygon className={`sch-part${selected ? " sch-active" : ""}`} points={outline(f)} fill={fill}
              style={bad ? { stroke: "var(--fail)", strokeWidth: 2 } : undefined} />
            {f.kind !== "head" && (
              <polyline className="sch-tangent" fill="none"
                points={`${X(f.zStart)},${cy - f.rInStart * scale} ${X(f.zEnd)},${cy - f.rInEnd * scale}`} />
            )}
            <line className="sch-tangent" x1={x0} y1={dTop - 5} x2={x0} y2={cy + (cy - dTop) + 5} />
            <text className={`sch-small${selected ? " sch-tag sch-active" : ""}`} x={(x0 + x1) / 2}
              y={cy + (cy - dTop) + 20} textAnchor="middle">{f.id}</text>
            {f.kind !== "head" && (
              <text className="sch-small" x={(x0 + x1) / 2} y={dTop - 8} textAnchor="middle">
                {f.kind === "cone"
                  ? `Ø${+(2 * f.rInStart).toFixed(0)}→${+(2 * f.rInEnd).toFixed(0)}`
                  : `Ø${+(2 * f.rInStart).toFixed(0)}`}
              </text>
            )}
          </g>
        );
      })}
      {nozzles.map(({ nz, i, res }) => {
        if ("error" in res) return null;
        const sel = chain.selectedNozzle === nz.tag;
        const x = X(res.position[2]);
        const rr = Math.max((nz.outside_diameter / 2) * scale, 3);
        const yTop = cy - res.rAtAnchor * scale - res.frame.thickness * scale;
        const lift = 16 + (i % 3) * 8;
        return (
          <g key={nz.tag} className={chain.onSelectNozzle ? "sch-chain-part is-clickable" : undefined}
            onClick={chain.onSelectNozzle ? () => chain.onSelectNozzle!(nz.tag) : undefined}>
            <rect className={sel ? "sch-part sch-active" : "sch-part"} x={x - rr} y={yTop - lift} width={2 * rr} height={lift}
              fill="var(--panel-raised)" />
            <text className={sel ? "sch-tag sch-active" : "sch-tag"} x={x} y={yTop - lift - 4} textAnchor="middle">{nz.tag}</text>
          </g>
        );
      })}
      <text className="sch-small" x={VBW - pad} y={VBH - 14} textAnchor="end">
        {frames.length} eleman · toplam {+(total).toFixed(0)} mm · ölçekli profil
      </text>
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

  if (props.chain && (props.chain.component_sequence.length > 3 || props.chain.cones.length > 0)) {
    return <ChainSchematic chain={props.chain} orientation={orientation} />;
  }

  const VBW = 480, VBH = 320;
  const padL = 78, padR = 34, padT = 74, padB = 60;
  const availW = VBW - padL - padR;
  const availH = VBH - padT - padB;

  // Sol ve sağ bombe derinlikleri (tip bazlı)
  const leftHD = headDepth(leftDi, leftHeadType, leftStraightFlange);
  const rightHD = headDepth(rightDi, rightHeadType, rightStraightFlange);

  const totalLenMM = Math.max(L + leftHD + rightHD, 1);
  const dImm = Math.max(di, leftDi, rightDi, 1);

  const isVertical = orientation === "vertical";

  // Dikey: genişlik/yükseklik takası
  const s = isVertical
    ? Math.min(availW / dImm, availH / totalLenMM)
    : Math.min(availW / totalLenMM, availH / dImm);

  const bodyH = Math.max(di, 1) * s;
  const cY = padT + availH / 2;

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
