import React from "react";
import { useStore } from "./store";
import {
  NewProjectPage,
  ConditionsPage,
  GeometryPage,
  ResultsPage,
  ViewerPage,
  ReportPage,
} from "./pages";

const STEPS = [
  { title: "Yeni Proje", sub: "Kimlik & rota", note: "Proje kimliği ve hesap standardı (ASME VIII-1)." },
  { title: "Tasarım Koşulları", sub: "Basınç & sıcaklık", note: "Basınç, sıcaklık ve korozyon payları." },
  { title: "Kap Geometrisi", sub: "Gövde, bombe, nozul", note: "Gövde, bombeler, malzeme, kaynak ve nozullar." },
  { title: "Hesap Sonuçları", sub: "ASME VIII-1", note: "Et kalınlığı, MAWP, hidrotest, nozul takviye…" },
  { title: "3D Model", sub: "STL görüntüleyici", note: "STL modeli döndürerek incele; ana ölçüler." },
  { title: "Rapor & Çıktı", sub: "HTML & STEP", note: "HTML hesap raporu ve STEP indirme." },
];

export function App() {
  const { step, setStep, theme, toggleTheme, project, calc } = useStore();

  const pages = [
    <NewProjectPage />,
    <ConditionsPage />,
    <GeometryPage />,
    <ResultsPage />,
    <ViewerPage />,
    <ReportPage />,
  ];

  return (
    <div className="app">
      <div className="brand">
        <div className="brand__mark" />
        <div>
          <div className="brand__name">Basınçlı Kap Suite</div>
          <div className="brand__sub">ASME VIII-1</div>
        </div>
      </div>

      <div className="topbar">
        <div className="topbar__title">
          <strong>{project.project_name}</strong> · {project.project_number} · Rev {project.revision}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          {calc?.global_mawp_mpa != null && (
            <span className="topbar__meta">
              MAWP {calc.global_mawp_mpa.toFixed(2)} MPa
            </span>
          )}
          <button className="icon-btn" onClick={toggleTheme} title="Tema değiştir">
            {theme === "dark" ? "☀" : "☾"}
          </button>
        </div>
      </div>

      <nav className="nav">
        <div className="nav__label">Sihirbaz</div>
        {STEPS.map((s, i) => (
          <button
            key={i}
            className={
              "step" +
              (i === step ? " step--active" : "") +
              (i < step ? " step--done" : "")
            }
            onClick={() => setStep(i)}
          >
            <span className="step__num">{i < step ? "✓" : String(i + 1).padStart(2, "0")}</span>
            <span className="step__title">
              {s.title}
              <small>{s.sub}</small>
            </span>
            <span className="step__note">{s.note}</span>
          </button>
        ))}
      </nav>

      <main className="main">{pages[step]}</main>
    </div>
  );
}
