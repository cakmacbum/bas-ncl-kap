import React from "react";
import { authConfigured, supabase } from "./supabase";
import { useSession } from "./useSession";
import "./auth.css";
import { AUTH_ENABLED } from "../features";

const LANDING_URL = import.meta.env.VITE_LANDING_URL as string | undefined;

function SignIn() {
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const go = async () => {
    setBusy(true);
    setError(null);
    const { error: err } = await supabase!.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: window.location.origin },
    });
    if (err) {
      setError(err.message);
      setBusy(false);
    }
  };

  return (
    <main className="auth-screen">
      <div className="auth-card">
        <div className="auth-card__mark" aria-hidden="true" />
        <h1>Pressure Vessel Suite</h1>
        <p>ASME VIII-1 pressure vessel calculations, 3D model and report in one workspace.</p>
        <button className="btn btn--primary auth-card__btn" type="button" onClick={go} disabled={busy}>
          {busy ? "Redirecting…" : "Continue with Google"}
        </button>
        {error && <div className="alert alert--info" role="alert">{error}</div>}
        <small>Free. No credit card.</small>
        {LANDING_URL && <a href={LANDING_URL}>&larr; Back to website</a>}
      </div>
    </main>
  );
}

export function AuthGate({ children }: { children: React.ReactNode }) {
  if (!AUTH_ENABLED) return <>{children}</>;
  return <Gate>{children}</Gate>;
}

function Gate({ children }: { children: React.ReactNode }) {
  const { session, loading } = useSession();

  if (!authConfigured) {
    return (
      <>
        <div className="auth-banner" role="status">
          Auth not configured — local dev mode
        </div>
        {children}
      </>
    );
  }
  if (loading) return <div className="auth-screen" aria-busy="true" />;
  // ?signup=1 de aynı Google ekranını gösterir (Google kayıt/girişi aynı işler).
  if (!session) return <SignIn />;
  return <>{children}</>;
}
