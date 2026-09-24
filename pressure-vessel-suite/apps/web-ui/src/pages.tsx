import React, { useState } from "react";
import { useStore } from "./store";
import { api } from "./api";
import {
  Panel,
  NumField,
  TextField,
  SelectField,
  StatusBadge,
  ResultRow,
  AccordionSection,
  SegmentTabs,
} from "./components";
import { CALC_TYPE_TR, HEAD_TYPE_TR, NOZZLE_TYPE_TR, ORIENTATION_TR, SUPPORT_TYPE_TR, tr } from "./i18n";
import type { CalcResult, VesselProject } from "./types";
import { VesselViewer, type ModelDims } from "./viewer";
import { VesselSchematic, type DimKey } from "./schematic";
import { LivePreview } from "./livePreview";
import {
  CUSTOM, catalog, dimsFor, matchDims, sizeOptions, wallOptions,
} from "./nozzleCatalog";
import { headDepth } from "./vesselModel";
import { geometryIssues, geometrySignature } from "./geometryValidation";

function PageHead({ kicker, title, desc }: { kicker: string; title: string; desc: string }) {
  return (
    <div className="page__head">
      <div className="page__kicker">{kicker}</div>
      <h1 className="page__title">{title}</h1>
      <p className="page__desc">{desc}</p>
    </div>
  );
}

function DimRow({ k, v }: { k: string; v: string }) {
  return (
    <div className="dim-row">
      <span>{k}</span>
      <b>{v}</b>
    </div>
  );
}

function NextButtons({ onNext, nextLabel }: { onNext: () => void; nextLabel?: string }) {
  const { step, setStep } = useStore();
  return (
    <div className="btn-row">
      {step > 0 && (
        <button className="btn btn--ghost" onClick={() => setStep(step - 1)}>
          ← Geri
        </button>
      )}
      <button className="btn btn--primary" onClick={onNext}>
        {nextLabel ?? "İleri →"}
      </button>
    </div>
  );
}

// ============================================================ 1. Yeni Proje
export function NewProjectPage() {
  const { project, setProject, setStep, loadProject, dirty } = useStore();
  const [savedProjects, setSavedProjects] = useState<import("./types").ProjectSummary[]>([]);
  const [projectBusy, setProjectBusy] = useState(false);
  const [projectError, setProjectError] = useState<string | null>(null);
  const refreshProjects = async () => {
    setProjectBusy(true);
    setProjectError(null);
    try { setSavedProjects(await api.listProjects()); }
    catch (e: any) { setProjectError(e.message ?? "Projeler alınamadı"); }
    finally { setProjectBusy(false); }
  };
  const openProject = async (id: string) => {
    setProjectBusy(true);
    setProjectError(null);
    try { loadProject(id, await api.getProject(id)); }
    catch (e: any) { setProjectError(e.message ?? "Proje açılamadı"); }
    finally { setProjectBusy(false); }
  };
  const p = project;
  return (
    <div className="page page--project">
      <PageHead
        kicker="Adım 01 / 06"
        title="Her güvenilir tasarım, doğru girdilerle başlar."
        desc="Projenizi tanımlayın, tasarım koşullarını belirleyin ve basınçlı kabınızı adım adım değerlendirin."
      />
      <div className="project-workspace">
      <div className="project-workspace__form">
      <Panel title="Kayıtlı Projeler" meta="API çalışma alanı"
        desc="Sunucuda kayıtlı bir projeyi açın.">
        <div style={{ display: "flex", alignItems: "end", gap: 12, flexWrap: "wrap" }}>
          <button className="btn btn--ghost" type="button" onClick={refreshProjects} disabled={projectBusy}>
            {projectBusy ? "Yükleniyor…" : "Projeleri Yenile"}
          </button>
          {savedProjects.length > 0 && <SelectField label="Proje aç" value=""
            options={[{ value: "", label: "Proje seçin…" }, ...savedProjects.map((p) => ({ value: p.id, label: `${p.project_number} · ${p.project_name} · Rev ${p.revision}` }))]}
            onChange={(id) => { if (id && (!dirty || window.confirm("Kaydedilmemiş değişiklikler var. Başka projeyi açmak istiyor musunuz?"))) void openProject(id); }} />}
        </div>
        {projectError && <div className="alert alert--warn" role="alert">{projectError}</div>}
      </Panel>
      <Panel title="Proje Kimliği" meta="genel bilgiler"
        desc="Proje kimliği ve hesap standardı (ASME VIII-1 veya EN 13445).">
        <div className="grid">
          <TextField label="Proje Numarası" value={p.project_number}
            onChange={(v) => setProject((x) => ({ ...x, project_number: v }))} />
          <TextField label="Proje Adı" value={p.project_name}
            onChange={(v) => setProject((x) => ({ ...x, project_name: v }))} />
          <TextField label="Müşteri" value={p.customer ?? ""}
            onChange={(v) => setProject((x) => ({ ...x, customer: v }))} />
          <TextField label="Revizyon" value={p.revision}
            onChange={(v) => setProject((x) => ({ ...x, revision: v }))} />
        </div>
      </Panel>
      <Panel title="Hesap Rotası" meta="standart ve yönelim"
        desc="Hesap standardı ve kap yönelimi (yatay/dikey).">
        <div className="grid">
          <SelectField label="Hesap Standardı" value={p.calculation_code}
            options={[
              { value: "ASME VIII-1", label: "ASME VIII Division 1" },
              { value: "EN 13445", label: "EN 13445" },
            ]}
            onChange={(v) => setProject((x) => ({ ...x, calculation_code: v }))} />
          <TextField label="Standart Sürümü" value={p.code_edition}
            onChange={(v) => setProject((x) => ({ ...x, code_edition: v }))} />
          <SelectField label="Kap Yönelimi" value={p.orientation}
            options={[
              { value: "horizontal", label: "Yatay" },
              { value: "vertical", label: "Dikey" },
            ]}
            onChange={(v) => setProject((x) => ({ ...x, orientation: v }))} />
          {p.calculation_code === "EN 13445" && (
            <p className="field__hint" style={{ gridColumn: "1 / -1", color: "var(--review)" }}>
              EN 13445 motoru seçildi. Kapsamı tamamlanmamış modüller REVIEW_REQUIRED veya
              NOT_CALCULATED dönebilir; sonuçlar yetkili mühendis doğrulaması olmadan nihai tasarım kararı değildir.
            </p>
          )}
        </div>
      </Panel>
      <NextButtons onNext={() => setStep(1)} nextLabel="Tasarım koşullarına devam et →" />
      </div>
      <aside className="project-preview" aria-label="Proje özeti">
        <div className="project-preview__heading"><span>TEKNİK ÖNİZLEME</span><span className="preview-dot">Girdilere bağlı</span></div>
        <h2>{p.project_name || "Yeni Basınçlı Kap"}</h2>
        <p>{ORIENTATION_TR[p.orientation] ?? p.orientation} kap · {p.materials[0]?.material_designation}</p>
        <VesselSchematic di={p.shell_sections[0].inside_diameter ?? 0}
          leftDi={p.heads[0].inside_diameter}
          rightDi={(p.heads[1] ?? p.heads[0]).inside_diameter}
          L={p.shell_sections[0].tangent_length} t={p.shell_sections[0].nominal_thickness}
          straightFlange={p.heads[0].straight_flange_length}
          leftStraightFlange={p.heads[0].straight_flange_length}
          rightStraightFlange={(p.heads[1] ?? p.heads[0]).straight_flange_length}
          leftHeadType={p.heads[0].type} rightHeadType={(p.heads[1] ?? p.heads[0]).type}
          orientation={p.orientation as "horizontal" | "vertical"} active=""
          nozzles={p.nozzles.map(n => ({tag: n.tag, z: n.axial_position, theta: n.circumferential_angle, od: n.outside_diameter, host: n.host_component_id, nozzle_type: n.nozzle_type}))} />
        <div className="project-preview__metrics">
          <div><span>Tasarım basıncı</span><strong>{p.design_conditions.design_pressure}<small> MPa</small></strong></div>
          <div><span>Tasarım sıcaklığı</span><strong>{p.design_conditions.design_temperature}<small> °C</small></strong></div>
          <div><span>İç çap</span><strong>{p.shell_sections[0].inside_diameter}<small> mm</small></strong></div>
          <div><span>Gövde uzunluğu</span><strong>{p.shell_sections[0].tangent_length}<small> mm</small></strong></div>
        </div>
        <div className="project-preview__note">Önizleme mevcut geometri girdilerini gösterir. Hesap sonucu veya imalat çizimi değildir.</div>
        <button className="btn btn--ghost" onClick={() => setStep(2)}>Geometriyi düzenle ↗</button>
      </aside>
      </div>
    </div>
  );
}

// ============================================================ 2. Tasarım Koşulları
export function ConditionsPage() {
  const { project, setProject, patchConditions, setStep } = useStore();
  const dc = project.design_conditions;
  return (
    <div className="page">
      <PageHead
        kicker="Adım 02 / 06"
        title="Tasarım Koşulları"
        desc="Basınç, sıcaklık ve korozyon payları. Çalışma / tasarım / PS ayrı değerlerdir."
      />
      <Panel title="Basınçlar" meta="MPa"
        desc="Çalışma, tasarım ve azami izin verilen basınç değerleri.">
        <div className="grid">
          <NumField label="Çalışma Basıncı" unit="MPa" value={dc.operating_pressure}
            onChange={(v) => patchConditions({ operating_pressure: v })} />
          <NumField label="Tasarım Basıncı" unit="MPa" value={dc.design_pressure}
            onChange={(v) => patchConditions({ design_pressure: v })}
            hint="Hesaplarda kullanılan basınç" />
          <NumField label="Azami İzin Verilen (PS)" unit="MPa"
            value={dc.maximum_allowable_pressure_ps}
            onChange={(v) => patchConditions({ maximum_allowable_pressure_ps: v })}
            hint="PED / isim plakası" />
        </div>
      </Panel>
      <Panel title="Basınç Tahliye Sistemi" meta="UG-125–136"
        desc="Emniyet vanası/patlama diski ayarını girin. Kapasite sertifikası olmadan sonuç nihai PASS değildir.">
        <div className="grid">
          <SelectField label="Tahliye sistemi" value={project.pressure_relief?.enabled ? "enabled" : "disabled"}
            options={[{ value: "disabled", label: "Tanımlı değil" }, { value: "enabled", label: "Etkin" }]}
            onChange={(v) => setProject((x) => ({
              ...x,
              pressure_relief: v === "enabled"
                ? (x.pressure_relief ?? { enabled: true, protected_mawp_mpa: null, accumulation_limit_percent: 10, devices: [{ device_id: "RV-1", device_type: "safety_valve", set_pressure_mpa: x.design_conditions.design_pressure, accumulation_percent: null, certified_capacity_kg_s: null }] })
                : { ...(x.pressure_relief ?? { accumulation_limit_percent: 10, devices: [] }), enabled: false },
            }))} />
          <NumField label="Korunan MAWP" unit="MPa" value={project.pressure_relief?.protected_mawp_mpa ?? 0}
            onChange={(v) => setProject((x) => ({ ...x, pressure_relief: { ...(x.pressure_relief ?? { enabled: true, accumulation_limit_percent: 10, devices: [] }), enabled: true, protected_mawp_mpa: v > 0 ? v : null } }))}
            hint="Boş bırakılırsa hesaplanan global MAWP kullanılır" />
          <NumField label="İzin verilen accumulation" unit="%" value={project.pressure_relief?.accumulation_limit_percent ?? 10}
            onChange={(v) => setProject((x) => ({ ...x, pressure_relief: { ...(x.pressure_relief ?? { enabled: true, devices: [] }), enabled: true, accumulation_limit_percent: v } }))} />
          {project.pressure_relief?.enabled && project.pressure_relief.devices[0] && (
            <>
              <SelectField label="Cihaz tipi" value={project.pressure_relief.devices[0].device_type}
                options={[{ value: "safety_valve", label: "Emniyet vanası" }, { value: "rupture_disk", label: "Patlama diski" }]}
                onChange={(v) => setProject((x) => ({ ...x, pressure_relief: { ...x.pressure_relief!, devices: [{ ...x.pressure_relief!.devices[0], device_type: v as "safety_valve" | "rupture_disk" }, ...x.pressure_relief!.devices.slice(1)] } }))} />
              <NumField label="Set / burst basıncı" unit="MPa" value={project.pressure_relief.devices[0].set_pressure_mpa ?? project.pressure_relief.devices[0].burst_pressure_mpa ?? 0}
                onChange={(v) => setProject((x) => ({ ...x, pressure_relief: { ...x.pressure_relief!, devices: [{ ...x.pressure_relief!.devices[0], set_pressure_mpa: v > 0 ? v : null, burst_pressure_mpa: null }, ...x.pressure_relief!.devices.slice(1)] } }))} />
            </>
          )}
        </div>
        {project.pressure_relief?.enabled && <p className="field__hint" style={{ color: "var(--review)" }}>Kapasite, blowdown ve senaryo doğrulaması yetkin mühendis/üretici verisiyle tamamlanmalıdır.</p>}
      </Panel>
      <Panel title="Sıcaklıklar" meta="°C"
        desc="Çalışma, tasarım ve hidrotest sıcaklıkları.">
        <div className="grid">
          <NumField label="Çalışma Sıcaklığı" unit="°C" value={dc.operating_temperature}
            onChange={(v) => patchConditions({ operating_temperature: v })} />
          <NumField label="Tasarım Sıcaklığı" unit="°C" value={dc.design_temperature}
            onChange={(v) => patchConditions({ design_temperature: v })} />
          <NumField label="Asgari Tasarım Sıcaklığı" unit="°C"
            value={dc.minimum_design_temperature}
            onChange={(v) => patchConditions({ minimum_design_temperature: v })} />
          <NumField label="Hidrotest Sıcaklığı" unit="°C" value={dc.hydrotest_temperature}
            onChange={(v) => patchConditions({ hydrotest_temperature: v })} />
          <NumField label="Darbe Testi Sıcaklığı" unit="°C"
            value={dc.impact_test_temperature_C ?? 0}
            onChange={(v) => patchConditions({ impact_test_temperature_C: v !== 0 ? v : null })}
            hint="0 = darbe testi yapılmadı"
            help="Charpy darbe testinin yapıldığı sıcaklık. Girilirse UCS-66 muafiyet değerlendirmesinde kullanılır." />
        </div>
      </Panel>
      <Panel title="Dış Basınç / Vakum" meta="UG-28 / UG-33"
        desc="Dış basınç veya vakum koşulu girilmezse UG-28/UG-33 stabilite kontrolü hiç çalışmaz.">
        <div className="grid">
          <NumField label="Dış Basınç" unit="MPa" value={dc.external_pressure}
            onChange={(v) => patchConditions({ external_pressure: v })}
            help="Kabın dışından etki eden basınç. 0 bırakılırsa UG-28 kontrolü yapılmaz." />
          <SelectField label="Vakum Koşulu"
            value={dc.vacuum_condition ? "1" : "0"}
            options={[{ value: "0", label: "Yok" }, { value: "1", label: "Var" }]}
            onChange={(v) => patchConditions({ vacuum_condition: v === "1" })}
            help="Kap tam vakuma maruz kalabiliyorsa 'Var' seçin — 0.1013 MPa dış basınç olarak değerlendirilir." />
        </div>
      </Panel>
      <Panel title="Akışkan" meta="statik kafa"
        desc="Sıvı sütununun MAWP'ye etkisi bu değerden hesaplanır.">
        <div className="grid">
          <NumField label="Akışkan Yoğunluğu" unit="kg/m³" value={dc.fluid_density_kg_m3}
            onChange={(v) => patchConditions({ fluid_density_kg_m3: v })}
            hint="0 = statik kafa düzeltmesi uygulanmaz"
            help="Su için 1000. 0 bırakılırsa sıvı sütunu basıncı MAWP'den düşülmez ve bu varsayım sonuçlara yazılır." />
        </div>
      </Panel>
      <Panel title="Korozyon Payı" meta="mm"
        desc="Ömür boyunca kaybolacağı varsayılan kalınlık payı.">
        <div className="grid">
          <NumField label="İç Korozyon Payı" unit="mm"
            value={dc.corrosion_allowance_internal}
            onChange={(v) => patchConditions({ corrosion_allowance_internal: v })} />
          <NumField label="Dış Korozyon Payı" unit="mm"
            value={dc.corrosion_allowance_external}
            onChange={(v) => patchConditions({ corrosion_allowance_external: v })} />
        </div>
      </Panel>
      <NextButtons onNext={() => setStep(2)} />
    </div>
  );
}

// ============================================================ 3. Geometri
export function GeometryPage() {
  const { project, setProject, setStep } = useStore();
  const [activeShellId, setActiveShellId] = useState(project.shell_sections[0]?.section_id ?? "");
  const [activeMaterialId, setActiveMaterialId] = useState(project.materials[0]?.material_id ?? "");
  const [activeWeldId, setActiveWeldId] = useState(project.welds[0]?.joint_id ?? "");
  const shell = project.shell_sections.find((item) => item.section_id === activeShellId) ?? project.shell_sections[0];
  const mat = project.materials.find((item) => item.material_id === activeMaterialId) ?? project.materials[0];
  const weld = project.welds.find((item) => item.joint_id === activeWeldId) ?? project.welds[0];

  const setShell = (patch: Partial<typeof shell>) =>
    setProject((x) => {
      const linked = (x.diameter_relation ?? "linked") === "linked";
      const heads = linked && patch.inside_diameter != null
        ? x.heads.map((head) => ({ ...head, inside_diameter: patch.inside_diameter as number }))
        : x.heads;
      return {
        ...x,
        shell_sections: x.shell_sections.map((section, index) =>
          section.section_id === shell.section_id ? { ...section, ...patch } : section
        ),
        heads,
      };
    });
  const setHead = (i: number, patch: Partial<(typeof project.heads)[0]>) =>
    setProject((x) => ({
      ...x,
      heads: x.heads.map((h, idx) => (idx === i ? { ...h, ...patch } : h)),
    }));
  const setMat = (patch: Partial<typeof mat>) =>
    setProject((x) => ({
      ...x,
      materials: x.materials.map((item, index) =>
        item.material_id === mat.material_id ? { ...item, ...patch } : item
      ),
    }));
  const setWeld = (patch: Partial<typeof weld>) =>
    setProject((x) => ({
      ...x,
      welds: x.welds.map((item, index) =>
        item.joint_id === weld.joint_id ? { ...item, ...patch } : item
      ),
    }));

  const addShell = () => setProject((x) => {
    const n = x.shell_sections.length + 1;
    const source = x.shell_sections[x.shell_sections.length - 1] ?? x.shell_sections[0];
    const sectionId = `SHELL-${String(n).padStart(2, "0")}`;
    const next = { ...source, section_id: sectionId };
    const sequence = [...(x.component_sequence ?? [])];
    sequence.splice(Math.max(0, sequence.length - 1), 0, { component_type: "shell" as const, component_id: sectionId });
    setActiveShellId(sectionId);
    return { ...x, shell_sections: [...x.shell_sections, next], component_sequence: sequence };
  });

  const addCone = () => setProject((x) => {
    const n = x.cones.length + 1;
    const lastShell = x.shell_sections[x.shell_sections.length - 1];
    const diameter = lastShell?.inside_diameter ?? 1000;
    const coneId = `CONE-${String(n).padStart(2, "0")}`;
    const cone = {
      cone_id: coneId,
      large_diameter: diameter,
      small_diameter: Math.max(1, diameter - 200),
      half_apex_angle: 15,
      length: 500,
      nominal_thickness: lastShell?.nominal_thickness ?? 12,
      material_id: lastShell?.material_id ?? "MAT-01",
      weld_joint_id: lastShell?.weld_joint_id ?? "WJ-01",
      internal_corrosion_allowance: lastShell?.internal_corrosion_allowance ?? 2,
      mill_tolerance: lastShell?.mill_tolerance ?? 12.5,
    };
    const sequence = [...(x.component_sequence ?? [])];
    sequence.splice(Math.max(0, sequence.length - 1), 0, { component_type: "cone" as const, component_id: coneId });
    return { ...x, cones: [...x.cones, cone], component_sequence: sequence };
  });

  const headOpts = Object.entries(HEAD_TYPE_TR).map(([value, label]) => ({ value, label }));
  const nozzleTypeOpts = Object.entries(NOZZLE_TYPE_TR).map(([value, label]) => ({ value, label }));
  const componentLabel = (ref: VesselProject["component_sequence"][0]) =>
    `${ref.component_type === "head" ? "Bombe" : ref.component_type === "shell" ? "Gövde" : "Koni"} (${ref.component_id})`;
  const hostOpts = (project.component_sequence ?? []).map((ref) => ({ value: ref.component_id, label: componentLabel(ref) }));
  const materialOpts = project.materials.map((m) => ({ value: m.material_id, label: `${m.material_id} — ${m.material_designation}` }));
  const weldOpts = project.welds.map((w) => ({ value: w.joint_id, label: `${w.joint_id} — ${w.joint_type}` }));

  const [active, setActive] = useState<DimKey>("");
  const [activeNozzle, setActiveNozzle] = useState<number>(0);
  const dim = (k: DimKey) => ({ onFocus: () => setActive(k), onBlur: () => setActive("") });
  const leftHead = project.heads[0];
  const rightHead = project.heads[1] ?? project.heads[0];
  const issues = geometryIssues(project);
  const issueSignature = geometrySignature(project);
  const [acceptedIssueSignature, setAcceptedIssueSignature] = useState<string | null>(null);
  React.useEffect(() => {
    setAcceptedIssueSignature(null);
  }, [issueSignature]);
  const proceedToResults = () => {
    const blocking = issues.filter((issue) => issue.blocking);
    if (blocking.length > 0) return;
    if (issues.length > 0 && acceptedIssueSignature !== issueSignature) {
      setAcceptedIssueSignature(issueSignature);
      return;
    }
    setStep(3);
  };

  // Dar form: tek bölüm açık (akordeon)
  const [openSection, setOpenSection] = useState<string>("shell");
  const toggleSection = (id: string) =>
    setOpenSection((cur) => (cur === id ? "" : id));
  const sec = (id: string) => ({
    id, open: openSection === id, onToggle: toggleSection,
  });

  // Büyük önizleme: ölçülü kesit / anlık 3D / kesin CadQuery modeli
  const [previewTab, setPreviewTab] = useState<"2d" | "3d" | "exact">("3d");
  const [exactUrl, setExactUrl] = useState<string | null>(null);
  const [exactBusy, setExactBusy] = useState(false);
  const [exactErr, setExactErr] = useState<string | null>(null);

  const loadExact = async () => {
    setExactBusy(true);
    setExactErr(null);
    try {
      const id = await ensureSaved();
      setExactUrl(`${api.stlUrl(id)}?t=${Date.now()}`);
      setPreviewTab("exact");
    } catch (e: any) {
      setExactErr(e.message ?? "Kesin model yüklenemedi");
    } finally {
      setExactBusy(false);
    }
  };

  // Nozul yardımcıları (store'dan)
  const addNozzle = useStore((s) => s.addNozzle);
  const removeNozzle = useStore((s) => s.removeNozzle);
  const updateNozzle = useStore((s) => s.updateNozzle);

  // Destek yardımcıları (store'dan)
  const addSupport = useStore((s) => s.addSupport);
  const removeSupport = useStore((s) => s.removeSupport);
  const updateSupport = useStore((s) => s.updateSupport);
  const addMaterial = useStore((s) => s.addMaterial);
  const removeMaterial = useStore((s) => s.removeMaterial);
  const addWeld = useStore((s) => s.addWeld);
  const removeWeld = useStore((s) => s.removeWeld);
  const duplicateComponent = useStore((s) => s.duplicateComponent);
  const removeComponent = useStore((s) => s.removeComponent);
  const moveComponent = useStore((s) => s.moveComponent);
  const [activeSupport, setActiveSupport] = useState<number>(0);
  const saddleCount = project.supports.filter((s) => s.type === "saddle").length;

  // Şemaya geçirilecek nozul listesi
  const schematicNozzles = project.nozzles.map((nz, i) => ({
    tag: nz.tag,
    z: nz.axial_position,
    theta: nz.circumferential_angle,
    od: nz.outside_diameter,
    host: nz.host_component_id,
    nozzle_type: nz.nozzle_type,
  }));

  return (
    <div className="page page--wide">
      <PageHead
        kicker="Adım 03 / 06"
        title="Kap Geometrisi"
        desc="Değeri yazarken sağdaki canlı şema güncellenir; düzenlediğin ölçü şemada vurgulanır. Alan başlıklarındaki (?) işaretine gelerek ne olduğunu görebilirsin."
      />
      <div className="geo-layout">
        <div className="geo-forms">
          <AccordionSection id="components" open title="Eleman Zinciri" meta={`${project.component_sequence?.length ?? 0} eleman`}
            onToggle={() => undefined} desc="Basınç taşıyan bileşenler kalıcı kimlikleriyle ve hesap sırasıyla tutulur.">
            <div style={{ display: "grid", gap: 8 }}>
              {(project.component_sequence ?? []).map((ref, index) => (
                <div key={`${ref.component_type}-${ref.component_id}`} className="derived-dims" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span>{index + 1}. {ref.component_type === "head" ? "Bombe" : ref.component_type === "shell" ? "Silindir" : "Koni"} <b>{ref.component_id}</b></span>
                  <span style={{ display: "flex", gap: 4 }}>
                    {ref.component_type === "shell" && <button type="button" className="ghost-btn" onClick={() => setActiveShellId(ref.component_id)}>Düzenle</button>}
                    <button type="button" className="ghost-btn" onClick={() => moveComponent(index, -1)} disabled={index === 0}>↑</button>
                    <button type="button" className="ghost-btn" onClick={() => moveComponent(index, 1)} disabled={index === (project.component_sequence?.length ?? 1) - 1}>↓</button>
                    <button type="button" className="ghost-btn" onClick={() => duplicateComponent(ref)}>Kopyala</button>
                    <button type="button" className="ghost-btn" onClick={() => removeComponent(ref)}>Sil</button>
                  </span>
                </div>
              ))}
              <div style={{ display: "flex", gap: 8 }}>
                <button type="button" className="ghost-btn" onClick={addShell}>Silindir ekle</button>
                <button type="button" className="ghost-btn" onClick={addCone}>Koni ekle</button>
              </div>
            </div>
          </AccordionSection>
          <AccordionSection {...sec("shell")} title="Silindirik Gövde" meta={shell.section_id}
            desc="Kabın ana silindirik kabuğu — iç çap, uzunluk ve et kalınlığı.">
            <div className="grid">
              <NumField label="İç Çap" unit="mm" value={shell.inside_diameter ?? 0}
                onChange={(v) => setShell({ inside_diameter: v })} {...dim("Di")}
                help="Kabın iç çapı (D_i). Silindirik gövdenin iç yüzeyleri arasındaki mesafe. Et kalınlığı bunun dışına eklenir." />
              <NumField label="Teğet Uzunluğu" unit="mm" value={shell.tangent_length}
                onChange={(v) => setShell({ tangent_length: v })} {...dim("L")}
                help="Silindirik gövdenin boyu — iki bombenin başladığı teğet çizgileri arası. Bombeler bu boya eklenir." />
              <NumField label="Nominal Kalınlık" unit="mm" value={shell.nominal_thickness}
                onChange={(v) => setShell({ nominal_thickness: v })} {...dim("t")}
                help="Gövde sac et kalınlığı (t). Hesap gerekli minimumu bulur; senin seçtiğin bundan büyük olmalı." />
              <NumField label="İç Korozyon Payı" unit="mm"
                value={shell.internal_corrosion_allowance}
                onChange={(v) => setShell({ internal_corrosion_allowance: v })}
                help="Ömür boyunca korozyonla kaybolacağı varsayılan kalınlık; gerekli et kalınlığına eklenir." />
              <NumField label="Sac Toleransı" unit="%" value={shell.mill_tolerance}
                onChange={(v) => setShell({ mill_tolerance: v })}
                help="Sac üreticisinin negatif kalınlık toleransı (ör. %12.5). Gerekli kalınlığa pay olarak eklenir." />
              <NumField label="UG-28 A Faktörü" value={shell.ug28_strain_factor_a ?? 0}
                onChange={(v) => setShell({ ug28_strain_factor_a: v > 0 ? v : null })}
                hint="0 = girilmedi (dış basınç bloke)"
                help="ASME VIII-1 Şekil G'den L/Do ve Do/t ile okunan birim şekil değiştirme faktörü. Lisanslı standart baskısından okunur; program bu çizelgeyi içermez (K6)." />
              <NumField label="UG-28 B Faktörü" unit="MPa" value={shell.ug28_allowable_stress_b ?? 0}
                onChange={(v) => setShell({ ug28_allowable_stress_b: v > 0 ? v : null })}
                hint="0 = girilmedi"
                help="A faktörü ve tasarım sıcaklığıyla malzeme çizelgesinden okunan B değeri." />
              <SelectField label="Malzeme" value={shell.material_id} options={materialOpts}
                onChange={(v) => setShell({ material_id: v })} />
              <SelectField label="Kaynak Birleşimi" value={shell.weld_joint_id ?? ""}
                options={[{ value: "", label: "— yok —" }, ...weldOpts]}
                onChange={(v) => setShell({ weld_joint_id: v || null })} />
            </div>
              <SelectField label="Gövde–bombe çap ilişkisi"
                value={project.diameter_relation ?? "linked"}
                options={[
                  { value: "linked", label: "Bağlı — gövde çapını bombelere uygula" },
                  { value: "independent", label: "Bağımsız — farklı çaplara izin ver" },
                ]}
                onChange={(v) => setProject((x) => ({
                  ...x,
                  diameter_relation: v as "linked" | "independent",
                  heads: v === "linked"
                    ? x.heads.map((head) => ({ ...head, inside_diameter: x.shell_sections[0].inside_diameter ?? head.inside_diameter }))
                    : x.heads,
                }))}
                help="Bağlı modda gövde iç çapı değiştiğinde sol ve sağ bombe çapları otomatik güncellenir. Bağımsız modda farklı çap girebilirsiniz; bu durumda geçiş uyarısı gösterilir." />
              <div className="derived-dims" aria-label="Gövde türetilmiş ölçüleri">
                <span>Gövde dış çapı</span><b>{((shell.inside_diameter ?? 0) + 2 * shell.nominal_thickness).toFixed(1)} mm</b>
                <span>Gövde dış yarıçapı</span><b>{((shell.inside_diameter ?? 0) / 2 + shell.nominal_thickness).toFixed(1)} mm</b>
              </div>
          </AccordionSection>

          {project.heads.map((h, i) => (
            <AccordionSection key={h.head_id}
              {...sec(i === 0 ? "headL" : "headR")}
              title={i === 0 ? "Sol Bombe" : "Sağ Bombe"}
              meta={h.head_id}
              desc={i === 0
                ? "Silindirin sol ucunu kapatan kubbe — tip, çap ve kalınlık."
                : "Silindirin sağ ucunu kapatan kubbe — tip, çap ve kalınlık."}>
              <div className="grid">
                <SelectField label="Bombe Tipi" value={h.type} options={headOpts}
                  onChange={(v) => setHead(i, { type: v as typeof h.type })} {...dim("headType")}
                  help="Bombenin biçimi: Elipsoidal (2:1) en yaygın; torisferik daha sığ; yarım küresel en dayanıklı." />
                <NumField label="İç Çap" unit="mm" value={h.inside_diameter}
                  onChange={(v) => setHead(i, { inside_diameter: v })} {...dim("headDi")}
                  help="Bombenin iç çapı — genelde gövde iç çapıyla aynı." />
                <NumField label="Nominal Kalınlık" unit="mm" value={h.nominal_thickness}
                  onChange={(v) => setHead(i, { nominal_thickness: v })} {...dim("headT")}
                  help="Bombe sac et kalınlığı." />
                <NumField label="Düz Flanş Boyu" unit="mm" value={h.straight_flange_length}
                  onChange={(v) => setHead(i, { straight_flange_length: v })} {...dim("sf")}
                  help="Bombenin gövdeye kaynaklandığı düz silindirik etek boyu." />
                <NumField label="UG-33 A Faktörü" value={h.ug28_strain_factor_a ?? 0}
                  onChange={(v) => setHead(i, { ug28_strain_factor_a: v > 0 ? v : null })}
                  hint="0 = girilmedi (dış basınç bloke)"
                  help="ASME VIII-1 Şekil G'den okunan birim şekil değiştirme faktörü. Lisanslı standart baskısından okunur (K6)." />
                <NumField label="UG-33 B Faktörü" unit="MPa" value={h.ug28_allowable_stress_b ?? 0}
                  onChange={(v) => setHead(i, { ug28_allowable_stress_b: v > 0 ? v : null })}
                  hint="0 = girilmedi"
                  help="A faktörü ve tasarım sıcaklığıyla malzeme çizelgesinden okunan B değeri." />
                <SelectField label="Malzeme" value={h.material_id} options={materialOpts}
                  onChange={(v) => setHead(i, { material_id: v })} />
                <SelectField label="Kaynak Birleşimi" value={h.weld_joint_id ?? ""}
                  options={[{ value: "", label: "— yok —" }, ...weldOpts]}
                  onChange={(v) => setHead(i, { weld_joint_id: v || null })} />

                {/* Düz kapak için UG-34 C katsayısı */}
                <div className="derived-dims" aria-label="Bombe türetilmiş ölçüleri">
                  <span>Dış çap</span><b>{(h.inside_diameter + 2 * h.nominal_thickness).toFixed(1)} mm</b>
                  <span>Kubbe derinliği</span><b>{headDepth(h.inside_diameter, h.type, h.straight_flange_length).toFixed(1)} mm</b>
                  <span>Gövde farkı</span><b>{(h.inside_diameter - (shell.inside_diameter ?? 0)).toFixed(1)} mm</b>
                </div>
                {h.type === "flat" && (
                  <NumField
                    label="Düz Kapak C Katsayısı (UG-34)"
                    value={h.flat_attachment_factor ?? 0}
                    onChange={(v) => setHead(i, { flat_attachment_factor: v })}
                    help="Şekil UG-34 bağlantı tipine göre; ör. kaynaklı 0.33, cıvatalı ~0.20/0.13. Kullanıcı girer."
                  />
                )}

                {/* Torisferik için taç ve mafsal yarıçapı */}
                {h.type === "torispherical" && (
                  <>
                    <NumField label="Taç Yarıçapı (Crown Radius)" unit="mm"
                      value={h.crown_radius ?? 0}
                      onChange={(v) => setHead(i, { crown_radius: v })}
                      help="Torisferik bombenin taç (kubbe) yarıçapı. Genelde iç çapın 1.0 katı." />
                    <NumField label="Mafsal Yarıçapı (Knuckle Radius)" unit="mm"
                      value={h.knuckle_radius ?? 0}
                      onChange={(v) => setHead(i, { knuckle_radius: v })}
                      help="Torisferik bombenin mafsal (birleşme) yarıçapı. Genelde iç çapın %6-10'u." />
                  </>
                )}
              </div>
            </AccordionSection>
          ))}

          {project.cones.map((cone) => (
            <AccordionSection key={cone.cone_id} {...sec(`cone-${cone.cone_id}`)} title="Konik Bölüm" meta={cone.cone_id}
              desc="Koni büyük/küçük çap, uzunluk ve yarı tepe açısı.">
              <div className="grid">
                <NumField label="Büyük Çap" unit="mm" value={cone.large_diameter}
                  onChange={(v) => setProject((x) => ({ ...x, cones: x.cones.map((item) => item.cone_id === cone.cone_id ? { ...item, large_diameter: v } : item) }))} />
                <NumField label="Küçük Çap" unit="mm" value={cone.small_diameter}
                  onChange={(v) => setProject((x) => ({ ...x, cones: x.cones.map((item) => item.cone_id === cone.cone_id ? { ...item, small_diameter: v } : item) }))} />
                <NumField label="Uzunluk" unit="mm" value={cone.length}
                  onChange={(v) => setProject((x) => ({ ...x, cones: x.cones.map((item) => item.cone_id === cone.cone_id ? { ...item, length: v } : item) }))} />
                <NumField label="Yarı Tepe Açısı" unit="°" value={cone.half_apex_angle}
                  onChange={(v) => setProject((x) => ({ ...x, cones: x.cones.map((item) => item.cone_id === cone.cone_id ? { ...item, half_apex_angle: v } : item) }))}
                  help="30° üzeri knuckle/özel analiz, 60° üzeri Appendix 1-8 kapsam dışıdır." />
                <NumField label="Nominal Kalınlık" unit="mm" value={cone.nominal_thickness}
                  onChange={(v) => setProject((x) => ({ ...x, cones: x.cones.map((item) => item.cone_id === cone.cone_id ? { ...item, nominal_thickness: v } : item) }))} />
              </div>
            </AccordionSection>
          ))}

          {/* ---- Nozullar (çoklu) ---- */}
          <AccordionSection {...sec("nozzles")} title="Nozullar"
            meta={`${project.nozzles.length} adet`}
            desc="Kaba bağlanan ağız/branşman (giriş-çıkış, drenaj, manway…). Her nozul gövde veya bombe üzerinde z, θ, α ile konumlanır.">
            {/* Nozul kartları */}
            <div className="nozzle-list">
              {project.nozzles.map((nz, i) => (
                <div key={i}
                  className={`nozzle-card${activeNozzle === i ? " nozzle-card--active" : ""}`}
                  onClick={() => setActiveNozzle(i)}>
                  <div className="nozzle-card__head">
                    <span className="nozzle-card__tag">{nz.tag || `N${i + 1}`}</span>
                    <span className="nozzle-card__type">{NOZZLE_TYPE_TR[nz.nozzle_type] ?? nz.nozzle_type}</span>
                    <span className="nozzle-card__host">{nz.host_component_id}</span>
                    {project.nozzles.length > 1 && (
                      <button className="nozzle-card__del" title="Nozulu sil"
                        onClick={(e) => { e.stopPropagation(); removeNozzle(i); }}>
                        ✕
                      </button>
                    )}
                  </div>
                </div>
              ))}
              <button className="btn btn--ghost nozzle-add" onClick={addNozzle}>
                ＋ Nozul Ekle
              </button>
            </div>

            {/* Seçili nozul düzenleme */}
            {project.nozzles[activeNozzle] && (() => {
              const nz = project.nozzles[activeNozzle];
              const setNoz = (patch: Partial<typeof nz>) => updateNozzle(activeNozzle, patch);

              // Host bombe mi? → konum "yerleşim çapı" ile verilir.
              const onHead = project.heads.some((h) => h.head_id === nz.host_component_id);
              const hostHead = project.heads.find((h) => h.head_id === nz.host_component_id);

              // Katalog eşleşmesi — elle değiştirilmişse "Özel ölçü".
              const matched = matchDims(nz.outside_diameter, nz.neck_thickness);
              const sizeVal = matched?.label ?? CUSTOM;
              const seriesVal = matched?.series ?? catalog.wallSeries[0];
              const applySize = (label: string, series: string) => {
                const d = dimsFor(label, series);
                if (d) setNoz(d);
              };

              return (
                <div className="grid" style={{ marginTop: 14 }}>
                  <TextField label="Etiket (Tag)" value={nz.tag}
                    help="Nozulun imalat, hesap ve rapor üzerindeki benzersiz etiketi; örneğin N1 veya N2."
                    onChange={(v) => setNoz({ tag: v })} />
                  <SelectField label="Nozul Tipi" value={nz.nozzle_type}
                    options={nozzleTypeOpts}
                    onChange={(v) => setNoz({ nozzle_type: v })}
                    help="Nozulun konstrüksiyon tipi — flanşlı, manşon, soket kaynaklı, manway vb." />
                  <SelectField label="Host Bileşen" value={nz.host_component_id}
                    options={hostOpts}
                    onChange={(v) => setNoz({ host_component_id: v })}
                    help="Nozulun bağlı olduğu bileşen: gövde veya bombelerden biri." />

                  {onHead ? (
                    <NumField label="Yerleşim Çapı (bombe merkezinden)" unit="mm"
                      value={nz.head_position_diameter ?? 0}
                      onChange={(v) => setNoz({ head_position_diameter: v > 0 ? v : null })}
                      {...dim("nz")}
                      hint={hostHead
                        ? `0 = tam tepe · en fazla ${hostHead.inside_diameter} mm`
                        : undefined}
                      help="Nozul ekseninin bombe merkez ekseninden uzaklığının iki katı — imalat çiziminden okunan ölçü. 0 bırakılırsa nozul bombe tepesine oturur." />
                  ) : (
                    <NumField label="Eksenel Konum (z)" unit="mm" value={nz.axial_position}
                      onChange={(v) => setNoz({ axial_position: v })} {...dim("nz")}
                      help="Nozulun sol teğet çizgisinden itibaren gövde ekseni boyunca uzaklığı." />
                  )}

                  <NumField label="Çevresel Açı (θ)" unit="°" value={nz.circumferential_angle}
                    onChange={(v) => setNoz({ circumferential_angle: v })} {...dim("theta")}
                    help="Nozulun kesitte saat yönündeki açısı. 0° = tam üst, 90° = yan." />
                  <NumField label="Eğim Açısı (α)" unit="°" value={nz.inclination_angle}
                    onChange={(v) => setNoz({ inclination_angle: v })}
                    help={onHead
                      ? "Nozulun bombe yüzey normaline göre eğimi. 0° = yüzeye dik, 30° = 30° eğik."
                      : "Nozulun gövdeye göre eğim açısı. 0° = dik (radyal), 90° = teğetsel."} />

                  <SelectField label="Anma Çapı (katalog)"
                    value={sizeVal}
                    options={[...sizeOptions, { value: CUSTOM, label: "Özel ölçü (elle)" }]}
                    onChange={(v) => { if (v !== CUSTOM) applySize(v, seriesVal); }}
                    help="Katalogdan boy seçilince dış çap, iç çap ve et kalınlığı otomatik dolar. Alanları elle değiştirirsen 'Özel ölçü'ye döner." />
                  <SelectField label="Et Serisi"
                    value={seriesVal}
                    options={wallOptions}
                    onChange={(v) => { if (sizeVal !== CUSTOM) applySize(sizeVal, v); }}
                    help="Boru et kalınlığı serisi. Yalnızca katalogdan bir anma çapı seçiliyken etkilidir." />
                  <SelectField label="Nozul Malzemesi" value={nz.material_id} options={materialOpts}
                    onChange={(v) => setNoz({ material_id: v })} />
                  {!catalog.verified && (
                    <p className="field__hint" style={{ gridColumn: "1 / -1", color: "var(--review)" }}>
                      ⚠ Katalog değerleri henüz <b>doğrulanmadı</b> — imalat öncesi
                      tedarikçi/çizim verisiyle karşılaştırın (kaynak: {catalog.source},
                      rev. {catalog.revision}).
                    </p>
                  )}

                  <NumField label="Dış Çap" unit="mm" value={nz.outside_diameter}
                    onChange={(v) => setNoz({ outside_diameter: v, size_designation: null })} {...dim("nd")}
                    help="Nozul borusunun dış çapı." />
                  <NumField label="İç Çap" unit="mm" value={nz.inside_diameter}
                    onChange={(v) => setNoz({ inside_diameter: v, size_designation: null })} {...dim("nd")}
                    help="Nozul borusunun iç çapı — açıklık takviye hesabında kullanılır." />
                  <NumField label="Boyun Kalınlığı" unit="mm" value={nz.neck_thickness}
                    onChange={(v) => setNoz({ neck_thickness: v, size_designation: null })}
                    help="Nozul borusunun et kalınlığı; takviye alanına katkı sağlar." />
                  <div className="derived-dims" aria-label="Nozul türetilmiş ölçüleri">
                    <span>Hesaplanan et</span><b>{((nz.outside_diameter - nz.inside_diameter) / 2).toFixed(2)} mm</b>
                    <span>Toplam nozul boyu</span><b>{(nz.inside_projection + nz.outside_projection).toFixed(1)} mm</b>
                    <span>Açıklık çapı</span><b>{nz.inside_diameter.toFixed(1)} mm</b>
                  </div>
                  <NumField label="İç Çıkıntı" unit="mm" value={nz.inside_projection}
                    onChange={(v) => setNoz({ inside_projection: v })}
                    help="Nozulun kabın içine doğru uzanma mesafesi." />
                  <NumField label="Dış Çıkıntı" unit="mm" value={nz.outside_projection}
                    onChange={(v) => setNoz({ outside_projection: v })}
                    help="Nozulun kabın dışına doğru uzanma mesafesi." />
                  <NumField label="Takviye Pedi Dış Çapı" unit="mm" value={nz.reinforcement_pad_od ?? 0}
                    onChange={(v) => setNoz({ reinforcement_pad_od: v, reinforcement_pad: v > 0 })}
                    help="Açıklığı güçlendiren halka pedin dış çapı. 0 = ped yok." />
                  <NumField label="Pedi Kalınlığı" unit="mm" value={nz.reinforcement_pad_thickness ?? 0}
                    onChange={(v) => setNoz({ reinforcement_pad_thickness: v })}
                    help="Takviye pedi sac kalınlığı." />
                </div>
              );
            })()}
          </AccordionSection>

          {/* ---- Destekler (çoklu) ---- */}
          <AccordionSection {...sec("supports")} title="Destekler"
            meta={`${project.supports.length} adet`}
            desc="Kabı taşıyan eyer (saddle), etek (skirt) veya ayak (leg). Tanımlanmazsa destek gerilme kontrolü hiç yapılmaz.">
            <div className="nozzle-list">
              {project.supports.map((sup, i) => (
                <div key={i}
                  className={`nozzle-card${activeSupport === i ? " nozzle-card--active" : ""}`}
                  onClick={() => setActiveSupport(i)}>
                  <div className="nozzle-card__head">
                    <span className="nozzle-card__tag">{sup.support_id}</span>
                    <span className="nozzle-card__type">{SUPPORT_TYPE_TR[sup.type] ?? sup.type}</span>
                    {project.supports.length > 0 && (
                      <button className="nozzle-card__del" title="Desteği sil"
                        onClick={(e) => { e.stopPropagation(); removeSupport(i); }}>
                        ✕
                      </button>
                    )}
                  </div>
                </div>
              ))}
              <button className="btn btn--ghost btn--sm nozzle-add" onClick={addSupport}>
                + Destek Ekle
              </button>
            </div>

            {project.supports.length > 0 && activeSupport < project.supports.length && (() => {
              const sup = project.supports[activeSupport];
              const setSup = (patch: Partial<typeof sup>) => updateSupport(activeSupport, patch);
              return (
                <div className="grid" style={{ marginTop: 12 }}>
                  <SelectField label="Destek Tipi"
                    value={sup.type}
                    options={[
                      { value: "saddle", label: "Eyer (saddle)" },
                      { value: "skirt", label: "Etek (skirt)" },
                      { value: "leg", label: "Ayak (leg)" },
                    ]}
                    onChange={(v) => setSup({ type: v as typeof sup.type })}
                    help="Kabı taşıyan destek türü: eyer, etek veya ayak. Seçim, aşağıdaki destek ölçülerini ve kontrolünü belirler." />
                  <SelectField label="Destek Malzemesi" value={sup.material_id} options={materialOpts}
                    onChange={(v) => setSup({ material_id: v })} />
                  <NumField label="Konum" unit="mm" value={sup.location_mm}
                    onChange={(v) => setSup({ location_mm: v })}
                    help="Kap ekseni boyunca konum. Etek için taban kotu." />
                  <NumField label="Genişlik" unit="mm" value={sup.width_mm}
                    onChange={(v) => setSup({ width_mm: v })}
                    help="Destek genişliği — eyerde temas genişliği." />
                  <NumField label="Yükseklik" unit="mm" value={sup.height_mm}
                    onChange={(v) => setSup({ height_mm: v })}
                    help="Desteğin kap eksenine dik yöndeki toplam yüksekliği." />
                  {sup.type === "skirt" && <>
                    <NumField label="Etek Çapı" unit="mm" value={sup.diameter_mm ?? 0}
                      onChange={(v) => setSup({ diameter_mm: v > 0 ? v : null })}
                      help="Etek ortalama/dış çapı; hesap için zorunludur." />
                    <NumField label="Etek Et Kalınlığı" unit="mm" value={sup.thickness_mm ?? 0}
                      onChange={(v) => setSup({ thickness_mm: v > 0 ? v : null })}
                      help="Etek nominal et kalınlığı; hesap için zorunludur." />
                  </>}
                  {sup.type === "saddle" && (
                    <NumField label="Sarma Açısı" unit="°" value={sup.contact_angle_deg ?? 0}
                      onChange={(v) => setSup({ contact_angle_deg: v })}
                      hint={saddleCount < 2 ? "Zick analizi iki eyer gerektirir; tek eyerle sonuç sınırlı olur." : undefined}
                      help="Eyer sarma açısı — Zick analizi için. Genelde 120°." />
                  )}
                  {sup.type === "leg" && (
                    <>
                      <NumField label="Ayak Sayısı" value={sup.leg_count ?? 0}
                        onChange={(v) => setSup({ leg_count: v > 0 ? v : null })}
                        help="Leg tipindeki desteğin taşıyıcı ayak adedi." />
                      <NumField label="Ayak Çapı" unit="mm" value={sup.leg_diameter_mm ?? 0}
                        onChange={(v) => setSup({ leg_diameter_mm: v > 0 ? v : null })}
                        help="Ayak dış çapı; hesap için zorunludur." />
                      <NumField label="Ayak Et Kalınlığı" unit="mm" value={sup.leg_thickness_mm ?? 0}
                        onChange={(v) => setSup({ leg_thickness_mm: v > 0 ? v : null })}
                        help="Ayak nominal et kalınlığı; hesap için zorunludur." />
                      <NumField label="Ayak Dağılım Yarıçapı" unit="mm" value={sup.support_radius_mm ?? 0}
                        onChange={(v) => setSup({ support_radius_mm: v > 0 ? v : null })}
                        help="Ayak eksenlerinin kap merkezinden gerçek uzaklığı; moment hesabı için zorunludur." />
                      <NumField label="Taban Plakası Alanı" unit="mm²" value={sup.base_plate_area_mm2 ?? 0}
                        onChange={(v) => setSup({ base_plate_area_mm2: v > 0 ? v : null })}
                        help="Boş bırakılırsa dairesel ayak kesiti kullanılır." />
                      <NumField label="Ankraj Cıvatası Adedi" value={sup.anchor_bolt_count ?? 0}
                        onChange={(v) => setSup({ anchor_bolt_count: v > 0 ? v : null })}
                        help="Uplift ve yatay yük aktarımında kullanılan ankraj adedi." />
                      <NumField label="Ankraj İzinli Çekme" unit="N" value={sup.anchor_tension_allowable_N ?? 0}
                        onChange={(v) => setSup({ anchor_tension_allowable_N: v > 0 ? v : null })}
                        help="Bir ankraj cıvatası için izin verilen çekme kuvveti." />
                      <NumField label="Ankraj İzinli Kesme" unit="N" value={sup.anchor_shear_allowable_N ?? 0}
                        onChange={(v) => setSup({ anchor_shear_allowable_N: v > 0 ? v : null })}
                        help="Bir ankraj cıvatası için izin verilen kesme kuvveti." />
                      <NumField label="Yatay Taban Yükü" unit="N" value={sup.lateral_load_N}
                        onChange={(v) => setSup({ lateral_load_N: v })}
                        help="Ankraj kesme kontrolüne aktarılan yatay kuvvet." />
                    </>
                  )}
                  {(sup.type === "skirt" || sup.type === "leg") && (
                    <NumField label="Devirme Momenti" unit="N·mm"
                      value={sup.overturning_moment_Nmm}
                      onChange={(v) => setSup({ overturning_moment_Nmm: v })}
                      hint="0 = moment yok (varsayım sonuçlara yazılır)"
                      help="Rüzgâr/deprem kaynaklı devirme momenti. 0 bırakılırsa bu yükler destek gerilmesine yansıtılmaz." />
                  )}
                </div>
              );
            })()}
          </AccordionSection>

          <AccordionSection {...sec("material")} title="Malzeme"
            meta={mat.material_id + " (manuel giriş — K4)"}
            desc="Gövde ve bombelerin malzeme özellikleri — standart tablosundan seçilir.">
            <div className="nozzle-list" style={{ marginBottom: 12 }}>
              {project.materials.map((m) => (
                <div key={m.material_id} className={`nozzle-card${m.material_id === mat.material_id ? " nozzle-card--active" : ""}`} onClick={() => setActiveMaterialId(m.material_id)}>
                  <div className="nozzle-card__head"><span className="nozzle-card__tag">{m.material_id}</span><span>{m.material_designation}</span>
                    {project.materials.length > 1 && <button className="nozzle-card__del" onClick={(e) => { e.stopPropagation(); removeMaterial(m.material_id); }}>✕</button>}
                  </div>
                </div>
              ))}
              <button className="btn btn--ghost btn--sm nozzle-add" onClick={() => { addMaterial(); setActiveMaterialId(`MAT-${String(project.materials.length + 1).padStart(2, "0")}`); }}>+ Malzeme Ekle</button>
            </div>
            <div className="grid">
              <TextField label="Malzeme Tanımı" value={mat.material_designation}
                help="Malzeme sertifikasında veya standart tablosunda geçen tam malzeme tanımı."
                onChange={(v) => setMat({ material_designation: v })} />
              <NumField label="İzin Verilen Gerilme (S)" unit="MPa" value={mat.allowable_stress}
                onChange={(v) => setMat({ allowable_stress: v })}
                help="Tasarım sıcaklığında malzemenin izin verilen gerilmesi (standart tablosundan). Et kalınlığını doğrudan belirler." />
              <NumField label="Akma Dayanımı" unit="MPa" value={mat.yield_strength}
                onChange={(v) => setMat({ yield_strength: v })}
                help="Malzemenin kalıcı şekil değiştirmeye başladığı gerilme değeri." />
              <NumField label="Çekme Dayanımı" unit="MPa" value={mat.tensile_strength}
                onChange={(v) => setMat({ tensile_strength: v })}
                help="Malzemenin kopmadan önce ulaşabildiği en yüksek çekme gerilmesi." />
              <NumField label="Yoğunluk" unit="kg/m³" value={mat.density}
                onChange={(v) => setMat({ density: v })} help="Ağırlık hesabı için kullanılır." />
              <SelectField
                label="UCS-66 Eğri Grubu"
                value={mat.ucs66_curve_group ?? ""}
                onChange={(v) => setMat({ ucs66_curve_group: v || null })}
                options={[
                  { value: "", label: "— girilmedi —" },
                  { value: "A", label: "A" },
                  { value: "B", label: "B" },
                  { value: "C", label: "C" },
                  { value: "D", label: "D" },
                ]}
                help="Malzeme belgesinden okunur (Şekil UCS-66). Girilmezse MDMT kontrolü yapılmaz — varsayılan atanmaz."
              />
            </div>
          </AccordionSection>

          <AccordionSection {...sec("weld")} title="Kaynak & NDT" meta={weld.joint_id}
            desc="Kaynak birleşim verimi ve tahribatsız muayene kapsamı.">
            <div className="nozzle-list" style={{ marginBottom: 12 }}>
              {project.welds.map((w) => (
                <div key={w.joint_id} className={`nozzle-card${w.joint_id === weld.joint_id ? " nozzle-card--active" : ""}`} onClick={() => setActiveWeldId(w.joint_id)}>
                  <div className="nozzle-card__head"><span className="nozzle-card__tag">{w.joint_id}</span><span>{w.joint_type}</span>
                    {project.welds.length > 1 && <button className="nozzle-card__del" onClick={(e) => { e.stopPropagation(); removeWeld(w.joint_id); }}>✕</button>}
                  </div>
                </div>
              ))}
              <button className="btn btn--ghost btn--sm nozzle-add" onClick={() => { addWeld(); setActiveWeldId(`WJ-${String(project.welds.length + 1).padStart(2, "0")}`); }}>+ Kaynak Ekle</button>
            </div>
            <div className="grid">
              <NumField label="Kaynak Verimi (E)" value={weld.joint_efficiency}
                onChange={(v) => setWeld({ joint_efficiency: v })} step={0.05}
                help="Kaynak birleşim katsayısı (0.70–1.00). NDT kapsamına bağlıdır; et kalınlığını etkiler." />
              <TextField label="NDE Yöntemi" value={weld.nde_method ?? ""}
                help="Kaynak için uygulanan tahribatsız muayene yöntemi; örneğin RT, UT veya PT."
                onChange={(v) => setWeld({ nde_method: v })} />
              <TextField label="NDE Kapsamı" value={weld.nde_extent ?? ""}
                help="Muayenenin kaynak üzerindeki kapsamı; örneğin 100% veya spot."
                onChange={(v) => setWeld({ nde_extent: v })} />
            </div>
          </AccordionSection>
        </div>

        {issues.length > 0 && (
          <div className={`alert ${issues.some((issue) => issue.blocking) ? "alert--error" : "alert--warn"}`} role="alert">
            <strong>Geometri kontrolü</strong>
            <ul>
              {issues.map((issue) => <li key={issue.code}>{issue.message}</li>)}
            </ul>
            {!issues.some((issue) => issue.blocking) && acceptedIssueSignature === issueSignature && (
              <span className="field__hint">Uyarı kabul edildi; sonuçlara geçebilirsiniz.</span>
            )}
          </div>
        )}

        <aside className="geo-preview">
          <div className="panel geo-preview__card">
            <div className="panel__head geo-preview__head">
              <SegmentTabs
                ariaLabel="Önizleme görünümü"
                value={previewTab}
                onChange={setPreviewTab}
                options={[
                  { value: "3d", label: "3D Önizleme" },
                  { value: "2d", label: "Ölçülü Kesit" },
                  { value: "exact", label: "Kesin Model" },
                ]}
              />
              <button className="btn btn--ghost btn--sm" onClick={loadExact}
                disabled={exactBusy}>
                {exactBusy ? "Üretiliyor…" : "↻ Kesin Modeli Yükle"}
              </button>
            </div>
            <div className="geo-preview__body">
              {previewTab === "3d" && (
                <LivePreview
                  shell={shell}
                  shells={project.shell_sections}
                  heads={project.heads}
                  cones={project.cones}
                  componentSequence={project.component_sequence}
                  nozzles={project.nozzles}
                  orientation={project.orientation}
                  active={active}
                  activeNozzle={activeNozzle}
                />
              )}

              {previewTab === "2d" && (
                <div className="geo-preview__scroll">
                  <VesselSchematic
                    di={shell.inside_diameter ?? 0}
                    leftDi={leftHead.inside_diameter}
                    rightDi={rightHead.inside_diameter}
                    L={shell.tangent_length}
                    t={shell.nominal_thickness}
                    straightFlange={rightHead.straight_flange_length}
                    leftStraightFlange={leftHead.straight_flange_length}
                    rightStraightFlange={rightHead.straight_flange_length}
                    leftHeadType={leftHead.type}
                    rightHeadType={rightHead.type}
                    leftHeadT={leftHead.nominal_thickness}
                    rightHeadT={rightHead.nominal_thickness}
                    nozzles={schematicNozzles}
                    activeNozzle={activeNozzle}
                    chain={{ sequence: project.component_sequence, shells: project.shell_sections,
                      heads: project.heads, cones: project.cones }}
                    active={active}
                    orientation={project.orientation as "horizontal" | "vertical"}
                  />
                  <p className="geo-hint">
                    Bir alana geldiğinde ilgili ölçü şemada <b>turuncu</b> vurgulanır.
                    Şema ölçekli ama semboliktir; kesin geometri CadQuery modelinde.
                  </p>
                </div>
              )}

              {previewTab === "exact" && (
                exactErr ? (
                  <div className="viewer-msg">
                    <div className="empty__mark">⚠</div>
                    <p>{exactErr}</p>
                  </div>
                ) : exactUrl ? (
                  <VesselViewer
                    url={exactUrl}
                    autoRotate={false}
                    section={false}
                    dims={computeDims(project)}
                  />
                ) : (
                  <div className="viewer-msg">
                    <p>
                      CadQuery ile üretilen <b>kesin</b> modeli görmek için
                      “Kesin Modeli Yükle”ye bas.
                    </p>
                  </div>
                )
              )}
            </div>
          </div>
        </aside>
      </div>

      <NextButtons onNext={proceedToResults}
        nextLabel={issues.length > 0 && acceptedIssueSignature !== issueSignature
          ? "Uyarıyı kabul et ve sonuçlara geç →"
          : "Sonuçlara Geç →"} />
    </div>
  );
}

// ============================================================ Ortak: kaydet
async function ensureSaved(): Promise<string> {
  const s = useStore.getState();
  let id = s.projectId;
  if (id == null) {
    const res = await api.createProject(s.project);
    id = res.id;
    s.setProjectId(res.id, res.input_file_hash);
  } else if (s.dirty) {
    const res = await api.updateProject(id, s.project);
    s.setProjectId(id, res.input_file_hash);
  }
  return id;
}

// ============================================================ Ortak: kaydet+hesapla
async function ensureCalculated(): Promise<void> {
  const s = useStore.getState();
  const id = await ensureSaved();
  const calc = await api.calculate(id);
  s.setCalc(calc);
}

// ============================================================ 4. Sonuçlar
// `emptyNote` verilirse, grup boşken sessizce gizlenmez — K4: eksiklik gizlenmez.
// Kullanıcı "bu kontrol yapıldı ve geçti" ile "bu kontrol hiç yapılmadı"yı ayırt
// edebilmeli. Boş bir bölümün görünmemesi ikincisini birincisi gibi gösterir.
function ResultGroup({
  title,
  rows,
  emptyNote,
}: {
  title: string;
  rows: CalcResult[];
  emptyNote: string;
}) {
  if (rows.length === 0) {
    return (
      <Panel title={title} meta="üretilmedi">
        <p className="muted" style={{ margin: 0 }}>{emptyNote}</p>
      </Panel>
    );
  }
  return (
    <Panel title={title} meta={`${rows.length} kayıt`}>
      <table className="table">
        <thead>
          <tr>
            <th>Bileşen</th>
            <th>Madde Ref.</th>
            <th style={{ textAlign: "right" }}>Sonuç</th>
            <th style={{ textAlign: "right" }}>Limit</th>
            <th style={{ textAlign: "right" }}>Kullanım</th>
            <th>Durum</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <ResultRow key={i} r={r} />
          ))}
        </tbody>
      </table>
    </Panel>
  );
}

export function ResultsPage() {
  const { calc, setCalc, setStep } = useStore();
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const run = async () => {
    setLoading(true);
    setErr(null);
    try {
      await ensureCalculated();
      setCalc(useStore.getState().calc);
    } catch (e: any) {
      setErr(e.message ?? "Hesap hatası");
    } finally {
      setLoading(false);
    }
  };

  const byType = (t: string) =>
    (calc?.results ?? []).filter((r) => r.calculation_type === t);

  return (
    <div className="page">
      <PageHead
        kicker="Adım 04 / 06"
        title="Hesap Sonuçları"
        desc="ASME VIII-1 hesap sırası: et kalınlığı, MAWP, hidrotest, nozul takviye, kaynak, çakışma."
      />
      {err && <div className="alert alert--warn">⚠ {err}</div>}

      {!calc && !loading && (
        <div className="empty">
          <div className="empty__mark">⚙</div>
          <p>Henüz hesap çalıştırılmadı.</p>
          <button className="btn btn--primary" onClick={run} style={{ marginTop: 16 }}>
            Hesapla
          </button>
        </div>
      )}

      {loading && (
        <div className="empty">
          <div className="spin" style={{ margin: "0 auto 12px" }} />
          <p>Hesaplanıyor…</p>
        </div>
      )}

      {calc && !loading && (
        <>
          {calc.errors.length > 0 && (
            <Panel
              title="Hesap Hataları"
              meta={`${calc.errors.length} hata`}
              desc="Aşağıdaki bölümler bu hatalar yüzünden üretilemedi. Boş görünen bölüm, kontrolün geçtiği anlamına gelmez."
            >
              <ul className="err-list">
                {calc.errors.map((e, i) => (
                  <li key={i} className="mono">{e}</li>
                ))}
              </ul>
            </Panel>
          )}
          <div className="kpi-row">
            <div className="kpi">
              <div className="kpi__label">Global MAWP</div>
              <div className="kpi__value">
                {calc.global_mawp_mpa?.toFixed(2) ?? "—"}
                <span className="kpi__unit"> MPa</span>
              </div>
              <div className="kpi__foot">en düşük bileşen limiti</div>
            </div>
            <div className="kpi">
              <div className="kpi__label">Hidrostatik Test</div>
              <div className="kpi__value">
                {byType("hydrotest")[0]?.final_result?.toFixed(2) ?? "—"}
                <span className="kpi__unit"> MPa</span>
              </div>
              <div className="kpi__foot">UG-99</div>
            </div>
            <div className="kpi">
              <div className="kpi__label">Pnömatik Test</div>
              <div className="kpi__value">
                {byType("pneumatic_test")[0]?.final_result?.toFixed(2) ?? "—"}
                <span className="kpi__unit"> MPa</span>
              </div>
              <div className="kpi__foot">UG-100</div>
            </div>
            <div className="kpi">
              <div className="kpi__label">İç Hacim</div>
              <div className="kpi__value">
                {calc.volume_mass.inner_volume_liters.toFixed(0)}
                <span className="kpi__unit"> L</span>
              </div>
              <div className="kpi__foot">
                {calc.volume_mass.inner_volume_m3.toFixed(2)} m³
              </div>
            </div>
            <div className="kpi">
              <div className="kpi__label">Metal Ağırlığı</div>
              <div className="kpi__value">
                {calc.volume_mass.metal_mass_kg.toFixed(0)}
                <span className="kpi__unit"> kg</span>
              </div>
              <div className="kpi__foot">tahmini</div>
            </div>
          </div>

          <div className="btn-row" style={{ justifyContent: "flex-start" }}>
            <button className="btn" onClick={run}>↻ Yeniden Hesapla</button>
          </div>

          <ResultGroup
            title="Ön Kontroller — Girdi Tutarlılığı"
            rows={[...byType("pressure_consistency"), ...byType("material_check")]}
            emptyNote="Girdi tutarlılık kontrolleri uyarı üretmedi: çalışma basıncı tasarım basıncını aşmıyor ve tüm bileşenlerin malzemesi listede bulundu."
          />

          <ResultGroup title="Et Kalınlığı — Gövde & Bombe" rows={byType("thickness")} emptyNote="Gövde/bombe kalınlık hesabı üretilmedi. Geometri adımında en az bir gövde kesiti ve bombe tanımlı olmalı; hata varsa yukarıdaki Hesap Hataları panelinde görünür." />
          <ResultGroup title="Nozul Takviyesi (UG-37/UG-40)" rows={byType("nozzle_reinforcement")} emptyNote="Nozul tanımlanmadığı için UG-37/UG-40 takviye kontrolü yapılmadı." />
          <ResultGroup title="Flanş Gerilmesi (Appendix 2)" rows={byType("flange_stress")} emptyNote="Flanş tanımlanmadığı için Appendix 2 kontrolü yapılmadı." />
          <ResultGroup title="Basınç Tahliye (UG-125–136)" rows={byType("pressure_relief")} emptyNote="Basınç tahliye sistemi tanımlanmadı." />
          <ResultGroup title="MAWP — Bileşen Bazında" rows={byType("mawp")} emptyNote="Bileşen MAWP değeri üretilmedi — kalınlık hesabı başarısızsa MAWP de üretilmez." />
          <ResultGroup title="Hidrostatik Test" rows={byType("hydrotest")} emptyNote="UG-99(b) test basıncı üretilmedi; MAWP hesaplanamadığında test basıncı da hesaplanamaz." />
          <ResultGroup title="Pnömatik Test — UG-100" rows={byType("pneumatic_test")} emptyNote="UG-100 pnömatik test basıncı üretilmedi." />
          {/* Dış basınç üç ayrı tip üretebiliyor: normal yolda `external_pressure`,
              vakum kontrolünde `vacuum_stability`, modül yüklenemezse
              `external_pressure_check`. Üçü de aynı bölümde gösterilmeli —
              yoksa vakum sonucu ve modül-yok durumu kullanıcıya hiç ulaşmaz. */}
          <ResultGroup
            title="Dış Basınç / Vakum — UG-28"
            rows={[
              ...byType("external_pressure"),
              ...byType("vacuum_stability"),
              ...byType("external_pressure_check"),
            ]}
            emptyNote="Dış basınç veya vakum koşulu girilmedi — UG-28/UG-33 stabilite kontrolü YAPILMADI. Tasarım Koşulları adımından dış basıncı veya vakum kutusunu işaretleyin."
          />
          <ResultGroup
            title="MDMT — UCS-66"
            rows={byType("mdmt_check")}
            emptyNote="Malzemeye UCS-66 eğri grubu (A/B/C/D) girilmediği için MDMT kontrolü yapılmadı. Eğri grubunu Malzeme adımından girin."
          />
          <ResultGroup
            title="Destekler — Zick / Skirt / Leg"
            rows={[
              ...byType("saddle_stress"),
              ...byType("skirt_stress"),
              ...byType("leg_stress"),
            ]}
            emptyNote="Destek tanımlanmadığı için Zick (eyer) / etek / ayak kontrolü YAPILMADI. Kap desteklenmiyor anlamına gelmez — kontrol hiç çalışmadı."
          />
          <ResultGroup title="Kaynak Doğrulama" rows={byType("weld_validation")} emptyNote="Kaynak birleşimi tanımlanmadığı için kaynak doğrulaması yapılmadı." />
          <ResultGroup title="Çakışma / Geometri" rows={byType("clash_check")} emptyNote="Çakışma kontrolü üretilmedi — en az iki nozul veya nozul+destek gerekir." />

          <ResultGroup title="Koni Uç Birleşimleri" rows={byType("junction_check")}
            emptyNote="Junction tanımı yok veya koni uç birleşimi kapsam dışı." />
          <NextButtons onNext={() => setStep(4)} nextLabel="3D Modele Geç →" />
        </>
      )}
    </div>
  );
}

// Project'ten 3D ölçü bilgisini türet (K2: mesh'ten değil, project data'dan).
// Bombe derinliği paylaşılan `vesselModel.headDepth`'ten gelir (tek kaynak).
function computeDims(project: ReturnType<typeof useStore.getState>["project"]): ModelDims {
  const shell = project.shell_sections[0];
  const leftHead = project.heads[0];
  const rightHead = project.heads[1] ?? project.heads[0];
  const di = shell.inside_diameter ?? 0;
  const t = shell.nominal_thickness;
  const outerR = di / 2 + t;
  const lhd = headDepth(leftHead.inside_diameter, leftHead.type, leftHead.straight_flange_length);
  const rhd = headDepth(rightHead.inside_diameter, rightHead.type, rightHead.straight_flange_length);

  const nozzles = project.nozzles.map((nz) => ({
    tag: nz.tag,
    z: nz.axial_position,
    thetaDeg: nz.circumferential_angle,
    tipR: outerR + nz.outside_projection,
    od: nz.outside_diameter,
    host: nz.host_component_id,
  }));

  return {
    L: shell.tangent_length,
    outerR,
    outerD: 2 * outerR,
    thickness: t,
    overallLen: shell.tangent_length + lhd + rhd,
    orientation: project.orientation as "horizontal" | "vertical",
    nozzle: nozzles[0] ?? { tag: "N1", z: 0, thetaDeg: 90, tipR: outerR + 150, od: 168.3, host: "SHELL-01" },
    nozzles,
  };
}

// ============================================================ 5. 3D Model
export function ViewerPage() {
  const { setStep, project } = useStore();
  const [url, setUrl] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [autoRotate, setAutoRotate] = useState(true);
  const [section, setSection] = useState(false);
  const dims = computeDims(project);

  const prepare = async () => {
    setBusy(true);
    setErr(null);
    try {
      const id = await ensureSaved();
      // Önbelleği kır: proje değişmiş olabilir
      setUrl(`${api.stlUrl(id)}?t=${Date.now()}`);
    } catch (e: any) {
      setErr(e.message ?? "Model hazırlanamadı");
    } finally {
      setBusy(false);
    }
  };

  const id = useStore.getState().projectId;

  return (
    <div className="page">
      <PageHead
        kicker="Adım 05 / 06"
        title="3D Model"
        desc="Kabın parametrik STL modeli — fare ile döndürün, tekerlekle yakınlaşın, sağ tıkla kaydırın."
      />
      {err && <div className="alert alert--warn">⚠ {err}</div>}

      {!url ? (
        <div className="empty">
          <div className="empty__mark">◈</div>
          <p>3D önizlemeyi oluşturmak için modeli hazırlayın.</p>
          <button className="btn btn--primary" onClick={prepare} disabled={busy}
            style={{ marginTop: 16 }}>
            {busy ? <><span className="spin" /> Hazırlanıyor…</> : "3D Modeli Oluştur"}
          </button>
        </div>
      ) : (
        <>
          <Panel
            title="Parametrik Kap Modeli"
            meta="STL · three.js"
            right={
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn btn--ghost" onClick={() => setSection((v) => !v)}
                  disabled={!url}>
                  {section ? "▣ Tam Görünüm" : "⧗ Kesit Görünümü"}
                </button>
                <button className="btn btn--ghost" onClick={() => setAutoRotate((v) => !v)}>
                  {autoRotate ? "⏸ Döndürmeyi Durdur" : "↻ Otomatik Döndür"}
                </button>
                <button className="btn" onClick={prepare} disabled={busy}>↻ Yenile</button>
                {id && <a className="btn" href={api.stepUrl(id)}>⬇ STEP</a>}
              </div>
            }
          >
            <div className="viewer-shell">
              <VesselViewer url={url} autoRotate={autoRotate} dims={dims} section={section}
                onManual={() => setAutoRotate(false)} />
              <div className="dim-panel">
                <div className="dim-panel__title">ANA ÖLÇÜLER</div>
                <DimRow k="Toplam boy" v={`${dims.overallLen.toFixed(0)} mm`} />
                <DimRow k="Teğet boyu" v={`${dims.L.toFixed(0)} mm`} />
                <DimRow k="Dış çap" v={`Ø ${dims.outerD.toFixed(0)} mm`} />
                <DimRow k="İç çap" v={`Ø ${(dims.outerD - 2 * dims.thickness).toFixed(0)} mm`} />
                <DimRow k="Et kalınlığı" v={`${dims.thickness} mm`} />
                <DimRow k="Yönelim" v={ORIENTATION_TR[dims.orientation ?? "horizontal"] ?? dims.orientation ?? "Yatay"} />
                {/* Nozul ölçüleri */}
                {(dims.nozzles ?? []).map((nz, i) => (
                  <DimRow key={i} k={`Nozul ${nz.tag}`}
                    v={`z=${nz.z} · θ=${nz.thetaDeg}° · Ø${nz.od}`} />
                ))}
              </div>
            </div>
          </Panel>
          <div className="alert alert--info">
            ℹ Ölçüler proje verisinden gelir (mesh'ten ölçülmez). Model tessellate edilmiş bir
            STL'dir; imalat için STEP dosyasını veya hesap raporunu kullanın.
          </div>
          <NextButtons onNext={() => setStep(5)} nextLabel="Rapora Geç →" />
        </>
      )}
    </div>
  );
}

// ============================================================ 6. Rapor
export function ReportPage() {
  const { projectId, setStep, calc, project } = useStore();
  const [ready, setReady] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const prepare = async () => {
    setBusy(true);
    setErr(null);
    try {
      await ensureCalculated();
      setReady(true);
    } catch (e: any) {
      setErr(e.message ?? "Rapor hazırlanamadı");
    } finally {
      setBusy(false);
    }
  };

  const id = useStore.getState().projectId ?? projectId;

  return (
    <div className="page">
      <PageHead
        kicker="Adım 06 / 06"
        title="Rapor ve Çıktılar"
        desc="23 bölümlük HTML hesap raporu (izlenebilirlik bloğuyla) ve STEP 3D modeli."
      />
      {err && <div className="alert alert--warn">⚠ {err}</div>}

      {!ready ? (
        <div className="empty">
          <div className="empty__mark">▤</div>
          <p>Raporu üretmek için projeyi kaydedip hesaplayın.</p>
          <button className="btn btn--primary" onClick={prepare} disabled={busy}
            style={{ marginTop: 16 }}>
            {busy ? <><span className="spin" /> Hazırlanıyor…</> : "Raporu Üret"}
          </button>
        </div>
      ) : (
        <>
          {calc && <Panel title="Rapor özeti" meta="yöneten ve kapsam sonuçları">
            <div className="kpi-row">
              <div className="kpi"><div className="kpi__label">Yöneten MAWP</div><div className="kpi__value">{calc.global_mawp_mpa?.toFixed(2) ?? "—"}<span className="kpi__unit"> MPa</span></div></div>
              <div className="kpi"><div className="kpi__label">Yöneten MDMT</div><div className="kpi__value">{(() => { const r = calc.results.find((x) => x.calculation_type === "mdmt_check" && x.component_id === "MDMT-GOVERNING"); return r && r.status !== "BLOCKED MISSING INPUT" && r.status !== "BLOCKED CODE DATA" && r.final_result != null ? r.final_result.toFixed(1) : "—"; })()}<span className="kpi__unit"> °C</span></div></div>
              <div className="kpi"><div className="kpi__label">Junction</div><div className="kpi__value">{project.welds.length}<span className="kpi__unit"> kaynak</span></div></div>
              <div className="kpi"><div className="kpi__label">Applicability</div><div className="kpi__value">{new Set(calc.results.map((r) => r.component_id || r.component_type)).size}<span className="kpi__unit"> bileşen</span></div></div>
            </div>
          </Panel>}
          <Panel
            title="Hesap Raporu"
            meta="HTML — izlenebilirlik bloğu dahil"
            right={
              <div style={{ display: "flex", gap: 8 }}>
                <a className="btn btn--ghost" href={api.reportUrl(id!)} target="_blank" rel="noreferrer">
                  ↗ Yeni Sekmede
                </a>
                <a className="btn" href={api.stepUrl(id!)}>⬇ STEP indir</a>
              </div>
            }
          >
            <iframe className="report-frame" src={api.reportUrl(id!)} title="Hesap Raporu" />
          </Panel>
          <div className="alert alert--info">
            ℹ PDF çıktısı, sunucuda WeasyPrint native kütüphaneleri kurulduğunda etkinleşir.
            STEP dosyası SolidWorks / FreeCAD ile açılabilir.
          </div>
          <div className="btn-row" style={{ justifyContent: "flex-start" }}>
            <button className="btn btn--ghost" onClick={() => setStep(4)}>← 3D Model</button>
          </div>
        </>
      )}
    </div>
  );
}
