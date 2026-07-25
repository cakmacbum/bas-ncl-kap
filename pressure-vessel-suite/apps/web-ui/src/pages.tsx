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
import { CALC_TYPE_TR, HEAD_TYPE_TR, NOZZLE_TYPE_TR, ORIENTATION_TR, tr } from "./i18n";
import type { CalcResult } from "./types";
import { VesselViewer, type ModelDims } from "./viewer";
import { VesselSchematic, type DimKey } from "./schematic";
import { LivePreview } from "./livePreview";
import {
  CUSTOM, catalog, dimsFor, matchDims, sizeOptions, wallOptions,
} from "./nozzleCatalog";
import { headDepth } from "./vesselModel";

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
  const { project, setProject, setStep } = useStore();
  const p = project;
  return (
    <div className="page">
      <PageHead
        kicker="Adım 01 / 06"
        title="Yeni Proje"
        desc="Proje kimliği ve hesap rotasını tanımlayın. V1 rotası ASME VIII-1 (iç basınç)."
      />
      <Panel title="Proje Kimliği" meta="genel bilgiler"
        desc="Proje kimliği ve hesap standardı (ASME VIII-1).">
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
            options={[{ value: "ASME VIII-1", label: "ASME VIII Division 1" }]}
            onChange={(v) => setProject((x) => ({ ...x, calculation_code: v }))} />
          <TextField label="Standart Sürümü" value={p.code_edition}
            onChange={(v) => setProject((x) => ({ ...x, code_edition: v }))} />
          <SelectField label="Kap Yönelimi" value={p.orientation}
            options={[
              { value: "horizontal", label: "Yatay" },
              { value: "vertical", label: "Dikey" },
            ]}
            onChange={(v) => setProject((x) => ({ ...x, orientation: v }))} />
        </div>
      </Panel>
      <NextButtons onNext={() => setStep(1)} />
    </div>
  );
}

// ============================================================ 2. Tasarım Koşulları
export function ConditionsPage() {
  const { project, patchConditions, setStep } = useStore();
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
  const shell = project.shell_sections[0];
  const mat = project.materials[0];
  const weld = project.welds[0];

  const setShell = (patch: Partial<typeof shell>) =>
    setProject((x) => ({ ...x, shell_sections: [{ ...x.shell_sections[0], ...patch }] }));
  const setHead = (i: number, patch: Partial<(typeof project.heads)[0]>) =>
    setProject((x) => ({
      ...x,
      heads: x.heads.map((h, idx) => (idx === i ? { ...h, ...patch } : h)),
    }));
  const setMat = (patch: Partial<typeof mat>) =>
    setProject((x) => ({ ...x, materials: [{ ...x.materials[0], ...patch }] }));
  const setWeld = (patch: Partial<typeof weld>) =>
    setProject((x) => ({ ...x, welds: [{ ...x.welds[0], ...patch }] }));

  const headOpts = Object.entries(HEAD_TYPE_TR).map(([value, label]) => ({ value, label }));
  const nozzleTypeOpts = Object.entries(NOZZLE_TYPE_TR).map(([value, label]) => ({ value, label }));
  const hostOpts = [
    { value: "SHELL-01", label: "Gövde (SHELL-01)" },
    { value: "HEAD-L", label: "Sol Bombe (HEAD-L)" },
    { value: "HEAD-R", label: "Sağ Bombe (HEAD-R)" },
  ];

  const [active, setActive] = useState<DimKey>("");
  const [activeNozzle, setActiveNozzle] = useState<number>(0);
  const dim = (k: DimKey) => ({ onFocus: () => setActive(k), onBlur: () => setActive("") });
  const leftHead = project.heads[0];
  const rightHead = project.heads[1] ?? project.heads[0];

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
          <AccordionSection {...sec("shell")} title="Silindirik Gövde" meta="SHELL-01"
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

                {/* Düz kapak için UG-34 C katsayısı */}
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

          <AccordionSection {...sec("material")} title="Malzeme"
            meta={mat.material_id + " (manuel giriş — K4)"}
            desc="Gövde ve bombelerin malzeme özellikleri — standart tablosundan seçilir.">
            <div className="grid">
              <TextField label="Malzeme Tanımı" value={mat.material_designation}
                onChange={(v) => setMat({ material_designation: v })} />
              <NumField label="İzin Verilen Gerilme (S)" unit="MPa" value={mat.allowable_stress}
                onChange={(v) => setMat({ allowable_stress: v })}
                help="Tasarım sıcaklığında malzemenin izin verilen gerilmesi (standart tablosundan). Et kalınlığını doğrudan belirler." />
              <NumField label="Akma Dayanımı" unit="MPa" value={mat.yield_strength}
                onChange={(v) => setMat({ yield_strength: v })} />
              <NumField label="Çekme Dayanımı" unit="MPa" value={mat.tensile_strength}
                onChange={(v) => setMat({ tensile_strength: v })} />
              <NumField label="Yoğunluk" unit="kg/m³" value={mat.density}
                onChange={(v) => setMat({ density: v })} help="Ağırlık hesabı için kullanılır." />
            </div>
          </AccordionSection>

          <AccordionSection {...sec("weld")} title="Kaynak & NDT" meta={weld.joint_id}
            desc="Kaynak birleşim verimi ve tahribatsız muayene kapsamı.">
            <div className="grid">
              <NumField label="Kaynak Verimi (E)" value={weld.joint_efficiency}
                onChange={(v) => setWeld({ joint_efficiency: v })} step={0.05}
                help="Kaynak birleşim katsayısı (0.70–1.00). NDT kapsamına bağlıdır; et kalınlığını etkiler." />
              <TextField label="NDE Yöntemi" value={weld.nde_method ?? ""}
                onChange={(v) => setWeld({ nde_method: v })} />
              <TextField label="NDE Kapsamı" value={weld.nde_extent ?? ""}
                onChange={(v) => setWeld({ nde_extent: v })} />
            </div>
          </AccordionSection>
        </div>

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
                  heads={project.heads}
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
                    L={shell.tangent_length}
                    t={shell.nominal_thickness}
                    straightFlange={rightHead.straight_flange_length}
                    leftHeadType={leftHead.type}
                    rightHeadType={rightHead.type}
                    leftHeadT={leftHead.nominal_thickness}
                    rightHeadT={rightHead.nominal_thickness}
                    nozzles={schematicNozzles}
                    activeNozzle={activeNozzle}
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

      <NextButtons onNext={() => setStep(3)} nextLabel="Sonuçlara Geç →" />
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
function ResultGroup({ title, rows }: { title: string; rows: CalcResult[] }) {
  if (rows.length === 0) return null;
  return (
    <Panel title={title} meta={`${rows.length} kayıt`}>
      <table className="table">
        <thead>
          <tr>
            <th>Bileşen</th>
            <th>Madde Ref.</th>
            <th style={{ textAlign: "right" }}>Sonuç</th>
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

          <ResultGroup title="Et Kalınlığı — Gövde & Bombe" rows={byType("thickness")} />
          <ResultGroup title="Nozul Takviyesi (UG-37/UG-40)" rows={byType("nozzle_reinforcement")} />
          <ResultGroup title="MAWP — Bileşen Bazında" rows={byType("mawp")} />
          <ResultGroup title="Hidrostatik Test" rows={byType("hydrotest")} />
          <ResultGroup title="Pnömatik Test — UG-100" rows={byType("pneumatic_test")} />
          <ResultGroup title="Dış Basınç / Vakum — UG-28" rows={byType("external_pressure")} />
          <ResultGroup title="MDMT — UCS-66" rows={byType("mdmt")} />
          <ResultGroup title="Kaynak Doğrulama" rows={byType("weld_validation")} />
          <ResultGroup title="Çakışma / Geometri" rows={byType("clash_check")} />

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
  const lhd = headDepth(di, leftHead.type, leftHead.straight_flange_length);
  const rhd = headDepth(di, rightHead.type, rightHead.straight_flange_length);

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
              <VesselViewer url={url} autoRotate={autoRotate} dims={dims} section={section} />
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
  const { projectId, setStep } = useStore();
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
