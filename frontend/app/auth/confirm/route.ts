import { type EmailOtpType } from "@supabase/supabase-js";
import { type NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET(request: NextRequest) {
  const tokenHash = request.nextUrl.searchParams.get("token_hash");
  const type = request.nextUrl.searchParams.get("type") as EmailOtpType | null;
  const code = request.nextUrl.searchParams.get("code");
  const nextParam = request.nextUrl.searchParams.get("next");
  const next = nextParam?.startsWith("/") && !nextParam.startsWith("//") ? nextParam : "/dashboard";

  const redirectUrl = request.nextUrl.clone();
  redirectUrl.pathname = next;
  redirectUrl.search = "";

  const supabase = await createClient();
  let error = null;

  if (code) {
    const result = await supabase.auth.exchangeCodeForSession(code);
    error = result.error;
  } else if (tokenHash && type) {
    const result = await supabase.auth.verifyOtp({
      token_hash: tokenHash,
      type,
    });
    error = result.error;
  } else {
    redirectUrl.pathname = "/auth/error";
    redirectUrl.searchParams.set("reason", "missing-token");
    return NextResponse.redirect(redirectUrl);
  }

  if (error) {
    redirectUrl.pathname = "/auth/error";
    redirectUrl.searchParams.set("reason", "invalid-or-expired-token");
    return NextResponse.redirect(redirectUrl);
  }

  return NextResponse.redirect(redirectUrl);
}
