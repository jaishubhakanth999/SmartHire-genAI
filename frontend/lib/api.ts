import { createClient } from "./supabase/client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://smarthire-genai-api.onrender.com";

async function authHeaders(): Promise<Record<string, string>> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
}

function friendlyError(status: number, detail: string) {
  if (status === 401) return "Your session has expired. Please sign in again.";
  if (status === 403) return "You do not have permission to perform this action.";
  if (status === 404) return detail || "The requested resource was not found.";
  if (status === 413) return detail || "The uploaded file is too large.";
  if (status === 422) return detail || "The submitted data could not be validated.";
  if (status >= 500) return detail || "The server could not complete that request. Please try again.";
  return detail || `Request failed (${status}).`;
}

async function handle(res: Response) {
  if (res.status === 204) return null;
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // response wasn't JSON
    }
    throw new Error(friendlyError(res.status, detail));
  }
  if (res.status === 200 || res.status === 201) {
    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("application/json")) return res.json();
  }
  return null;
}

async function request(path: string, init: RequestInit = {}) {
  const headers = { ...(await authHeaders()), ...(init.headers || {}) };
  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  return handle(res);
}

export function apiGet(path: string) {
  return request(path, { method: "GET" });
}

export function apiPostJson(path: string, body: unknown) {
  return request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function apiPostForm(path: string, form: FormData) {
  return request(path, { method: "POST", body: form });
}

export function apiDelete(path: string) {
  return request(path, { method: "DELETE" });
}
