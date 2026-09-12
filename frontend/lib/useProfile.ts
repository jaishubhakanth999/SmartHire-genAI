"use client";

import { useEffect, useState } from "react";
import { createClient } from "./supabase/client";
import type { Profile } from "@/types";

/**
 * Fetches the signed-in user's profile row (id, email, role) directly from
 * Supabase using the anon key + the user's own session -- protected by the
 * `profiles_select_own` RLS policy, so this never needs the backend.
 */
export function useProfile() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const supabase = createClient();

    async function load() {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) {
        if (active) {
          setProfile(null);
          setLoading(false);
        }
        return;
      }
      const { data } = await supabase
        .from("profiles")
        .select("id, email, full_name, role")
        .eq("id", user.id)
        .single();
      if (active) {
        setProfile((data as Profile) ?? null);
        setLoading(false);
      }
    }

    load();
    const { data: listener } = supabase.auth.onAuthStateChange(() => load());
    return () => {
      active = false;
      listener.subscription.unsubscribe();
    };
  }, []);

  return { profile, loading };
}
