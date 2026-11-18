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
import { computeIssues } from "./geometrySteps/IssuesPanel";
import { AUTH_ENABLED } from "./features";
import { AccountMenu } from "./auth/AccountMenu";
import { StepErrorBoundary } from "./StepErrorBoundary";

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

  React.useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  React.useEffect(() => {
    document.querySelector(".main")?.scrollTo(0, 0);
  }, [step]);

  const pages = [
    <NewProjectPage />,
    <ConditionsPage />,
    <GeometryPage />,
    <ResultsPage />,
    <ViewerPage />,
    <ReportPage />,
  ];
  const navigate = (target: number) => {
    if (target > 2) {
      const issues = computeIssues(project);
      const blocking = issues.filter((issue) => issue.blocking);
      const warnings = issues.filter((issue) => issue.level !== "info");
      if (blocking.length > 0) {
        window.alert(`Geometri tamamlanmadan ilerlenemez:\n\n${blocking.map((issue) => issue.message).join("\n")}`);
        setStep(2);
        return;
      }
      if (issues.length > 0 && !window.confirm(`Geometri uyarıları var:\n\n${issues.map((issue) => issue.message).join("\n")}\n\nYine de devam edilsin mi?`)) {
        setStep(2);
        return;
      }
    }
    setStep(target);
  };

  return (
    <div className="app">
      <a className="skip-link" href="#workspace">İçeriğe geç</a>
      <div className="brand">
        <svg
          className="brand__mark"
          aria-hidden="true"
          viewBox="0 0 48 48"
          width="36"
          height="36"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M 14 17 H 34 A 7 8 0 0 1 34 33 H 14 A 7 8 0 0 1 14 17 Z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinejoin="round"
          />
          <line
            x1="14"
            y1="18"
            x2="14"
            y2="32"
            stroke="currentColor"
            strokeWidth="1"
            strokeDasharray="2 2"
            opacity="0.35"
          />
          <line
            x1="34"
            y1="18"
            x2="34"
            y2="32"
            stroke="currentColor"
            strokeWidth="1"
            strokeDasharray="2 2"
            opacity="0.35"
          />
          <path
            d="M 21 17 V 10 H 27 V 17"
            stroke="var(--accent)"
            strokeWidth="2"
            strokeLinejoin="round"
          />
          <line
            x1="18"
            y1="9"
            x2="30"
            y2="9"
            stroke="var(--accent)"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <line
            x1="10"
            y1="25"
            x2="38"
            y2="25"
            stroke="var(--accent)"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeDasharray="4 2.5"
            opacity="0.85"
          />
          <path
            d="M 14 33 L 13 41 M 18 33 L 19 41 M 11 41 H 21"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <path
            d="M 30 33 L 29 41 M 34 33 L 35 41 M 27 41 H 37"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
        <div>
          <div className="brand__name">Basınçlı Kap Suite</div>
          <div className="brand__sub">MÜHENDİSLİK ÇALIŞMA ALANI</div>
        </div>
      </div>

      <div className="topbar">
        <div className="topbar__title">
          <span className="topbar__breadcrumb">Projeler <span>/</span> {project.project_number}</span>
          <strong>{project.project_name}</strong>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <span className="workspace-status">{calc ? "Hesap üretildi · sonuçları inceleyin" : "Henüz hesaplanmadı"}</span>
          {calc?.global_mawp_mpa != null && (
            <span className="topbar__meta">
              MAWP {calc.global_mawp_mpa.toFixed(2)} MPa
            </span>
          )}
          <button className="icon-btn" onClick={toggleTheme} title="Tema değiştir" aria-label={theme === "dark" ? "Açık temaya geç" : "Koyu temaya geç"}>
            {theme === "dark" ? "☀" : "☾"}
          </button>
          {AUTH_ENABLED && <AccountMenu />}
        </div>
      </div>

      <nav className="nav" aria-label="Proje adımları">
        <div className="nav__project"><span>AKTİF PROJE</span><strong>{project.project_number || "Proje numarası yok"}</strong><small>Revizyon {project.revision} · SI birim sistemi</small></div>
        <div className="nav__label">TASARIM İŞ AKIŞI</div>
        {STEPS.map((s, i) => (
          <button
            key={i}
            className={
              "step" +
              (i === step ? " step--active" : "")
            }
            aria-current={i === step ? "step" : undefined}
            title={s.note}
            onClick={() => navigate(i)}
          >
            <span className="step__num">{String(i + 1).padStart(2, "0")}</span>
            <span className="step__title">
              {s.title}
              <small>{s.sub}</small>
            </span>
            <span className="step__note">{s.note}</span>
          </button>
        ))}
        <div className="nav__footer"><span className="nav__standard">{project.calculation_code}</span><p>{project.code_edition} sürümü</p><small>Geometriden hesap raporuna,<br />tek bir çalışma alanı.</small></div>
      </nav>

      <main className="main" id="workspace" tabIndex={-1}>
        <div className="workspace-path"><span>ÇALIŞMA ALANI / {STEPS[step].title.toLocaleUpperCase("tr-TR")}</span><span>ADIM {String(step + 1).padStart(2, "0")} <span className="dim">/ 06</span></span></div>
        <StepErrorBoundary
          key={step}
          stepLabel={`${String(step + 1).padStart(2, "0")} · ${STEPS[step].title}`}
          onGoToFirstStep={() => setStep(0)}
        >
          {pages[step]}
        </StepErrorBoundary>
        <footer className="workspace-footer"><span>Basınçlı Kap Suite</span><span>Hesap çıktıları mühendislik incelemesi gerektirir.</span><span>SI · mm / MPa / °C</span></footer>
      </main>
    </div>
  );
}
