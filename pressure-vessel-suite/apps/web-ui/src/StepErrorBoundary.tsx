import React from "react";

/** Fırlatılan değer Error olmayabilir (string, nesne…); kullanıcıya gösterilecek kısa mesajı üretir. */
export function describeStepError(error: unknown): string {
  if (error instanceof Error && error.message) return error.message;
  if (typeof error === "string" && error.trim()) return error;
  return "Beklenmeyen bir görüntüleme hatası oluştu.";
}

interface StepErrorFallbackProps {
  stepLabel: string;
  error: unknown;
  onRetry: () => void;
  onGoToFirstStep: () => void;
}

/** Hata sınırının yedek görünümü. Saf bileşen: sınıftan bağımsız render edilip sınanabilir. */
export function StepErrorFallback({ stepLabel, error, onRetry, onGoToFirstStep }: StepErrorFallbackProps) {
  return (
    <section className="alert alert--error step-error" role="alert">
      <div className="step-error__head">
        <svg className="step-error__icon" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false">
          <path d="M12 3 2.5 20h19L12 3Z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
          <path d="M12 10v5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          <circle cx="12" cy="17.6" r="1.1" fill="currentColor" />
        </svg>
        <strong className="step-error__title">Hata: Bu adım görüntülenirken bir sorun oluştu</strong>
      </div>
      <p className="step-error__text">
        Etkilenen adım: <b>{stepLabel}</b>
      </p>
      <p className="step-error__text">
        Girdiğiniz proje verileri silinmedi. Diğer adımlar çalışmaya devam ediyor; soldaki adım listesinden
        başka bir adıma geçebilir veya bu adımı yeniden deneyebilirsiniz.
      </p>
      <details className="step-error__details">
        <summary>Teknik ayrıntı</summary>
        <code>{describeStepError(error)}</code>
      </details>
      <div className="btn-row">
        <button type="button" className="btn btn--primary" onClick={onRetry}>
          Yeniden dene
        </button>
        <button type="button" className="btn btn--ghost" onClick={onGoToFirstStep}>
          İlk adıma dön
        </button>
      </div>
    </section>
  );
}

interface StepErrorBoundaryProps {
  stepLabel: string;
  onGoToFirstStep: () => void;
  children?: React.ReactNode;
}

interface StepErrorBoundaryState {
  /** `failed` ayrı tutulur: `throw null` / `throw undefined` de yakalanmış sayılmalı. */
  failed: boolean;
  error: unknown;
}

/**
 * Adım bazlı hata sınırı. Bir adım bileşeni render sırasında fırlatırsa yalnız o adımın
 * içeriği yedek görünüme düşer; üst çubuk ve adım gezinmesi sınırın dışında çalışmaya devam eder.
 * Adım değişiminde sıfırlanması için çağıran taraf `key={step}` vermelidir.
 */
export class StepErrorBoundary extends React.Component<StepErrorBoundaryProps, StepErrorBoundaryState> {
  state: StepErrorBoundaryState = { failed: false, error: null };

  static getDerivedStateFromError(error: unknown): StepErrorBoundaryState {
    return { failed: true, error };
  }

  componentDidCatch(error: unknown, info: React.ErrorInfo) {
    console.error(`[StepErrorBoundary] "${this.props.stepLabel}" adımı render edilemedi:`, error, info.componentStack);
  }

  private reset = () => {
    this.setState({ failed: false, error: null });
  };

  private goToFirstStep = () => {
    // Hata zaten ilk adımdaysa key değişmez; bu yüzden sınırı burada da sıfırla.
    this.reset();
    this.props.onGoToFirstStep();
  };

  render() {
    if (this.state.failed) {
      return (
        <StepErrorFallback
          stepLabel={this.props.stepLabel}
          error={this.state.error}
          onRetry={this.reset}
          onGoToFirstStep={this.goToFirstStep}
        />
      );
    }
    return this.props.children;
  }
}
