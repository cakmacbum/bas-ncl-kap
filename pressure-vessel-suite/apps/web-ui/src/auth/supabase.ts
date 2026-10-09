import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

export const authConfigured = Boolean(url && anonKey);

// Yapılandırılmamışsa null — uygulama yerel geliştirme modunda çalışır.
export const supabase: SupabaseClient | null = authConfigured
  ? createClient(url!, anonKey!)
  : null;
