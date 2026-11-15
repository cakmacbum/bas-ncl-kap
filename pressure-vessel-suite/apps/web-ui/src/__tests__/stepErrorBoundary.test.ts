import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { StepErrorBoundary, StepErrorFallback, describeStepError } from "../StepErrorBoundary";

const noop = () => {};

describe("StepErrorBoundary", () => {
  it("getDerivedStateFromError hatayı state'e taşır", () => {
    const error = new Error("patladı");
    expect(StepErrorBoundary.getDerivedStateFromError(error)).toEqual({ failed: true, error });
  });

  it("throw undefined de yakalanmış sayılır", () => {
    expect(StepErrorBoundary.getDerivedStateFromError(undefined).failed).toBe(true);
  });

  it("hata yokken çocukları olduğu gibi render eder", () => {
    const html = renderToStaticMarkup(
      React.createElement(
        StepErrorBoundary,
        { stepLabel: "03 · Kap Geometrisi", onGoToFirstStep: noop },
        React.createElement("p", null, "adım içeriği"),
      ),
    );
    expect(html).toBe("<p>adım içeriği</p>");
  });
});

describe("StepErrorFallback", () => {
  const html = renderToStaticMarkup(
    React.createElement(StepErrorFallback, {
      stepLabel: "04 · Hesap Sonuçları",
      error: new Error("calc.results tanımsız"),
      onRetry: noop,
      onGoToFirstStep: noop,
    }),
  );

  it("role=alert ile adımı, hata mesajını ve veri güvencesini gösterir", () => {
    expect(html).toContain('role="alert"');
    expect(html).toContain("04 · Hesap Sonuçları");
    expect(html).toContain("calc.results tanımsız");
    expect(html).toContain("silinmedi");
  });

  it("iki eylem düğmesi içerir ve yığın izini dökmez", () => {
    expect(html.match(/<button/g)).toHaveLength(2);
    expect(html).toContain("Yeniden dene");
    expect(html).toContain("İlk adıma dön");
    expect(html).not.toMatch(/\bat \S+ \(/);
  });
});

describe("describeStepError", () => {
  it("Error dışı değerler için güvenli mesaj üretir", () => {
    expect(describeStepError(new Error("x"))).toBe("x");
    expect(describeStepError("düz metin")).toBe("düz metin");
    expect(describeStepError(undefined)).toBe("Beklenmeyen bir görüntüleme hatası oluştu.");
    expect(describeStepError({})).toBe("Beklenmeyen bir görüntüleme hatası oluştu.");
  });
});
