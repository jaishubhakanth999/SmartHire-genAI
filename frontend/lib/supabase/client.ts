import { createBrowserClient } from "@supabase/ssr";

const SUPABASE_URL =
  process.env.NEXT_PUBLIC_SUPABASE_URL ||
  "https://lfovbkekbjtadqaatank.supabase.co";

const SUPABASE_KEY =
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  "sb_publishable_YnLQpoKR2bq6pKaBdnFbbQ_z7FWOeMm";

export function createClient() {
  return createBrowserClient(SUPABASE_URL, SUPABASE_KEY);
}
