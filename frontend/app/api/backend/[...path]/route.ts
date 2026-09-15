import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL || "https://smarthire-genai-api.onrender.com";

const HOP_BY_HOP_HEADERS = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
  "host",
  "content-length",
]);

function forwardHeaders(request: NextRequest) {
  const headers = new Headers();
  request.headers.forEach((value, key) => {
    if (!HOP_BY_HOP_HEADERS.has(key.toLowerCase())) {
      headers.set(key, value);
    }
  });
  return headers;
}

export async function handler(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  const target = `${BACKEND_URL.replace(/\/$/, "")}/${path
    .map((segment) => encodeURIComponent(segment))
    .join("/")}${request.nextUrl.search}`;

  try {
    const body = ["GET", "HEAD"].includes(request.method)
      ? undefined
      : await request.arrayBuffer();

    const response = await fetch(target, {
      method: request.method,
      headers: forwardHeaders(request),
      body,
      redirect: "manual",
      cache: "no-store",
    });

    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => {
      if (!HOP_BY_HOP_HEADERS.has(key.toLowerCase())) {
        responseHeaders.set(key, value);
      }
    });

    return new NextResponse(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error("Backend proxy request failed", {
      target,
      method: request.method,
      error: error instanceof Error ? error.message : String(error),
    });

    return NextResponse.json(
      {
        detail:
          "The AI backend could not be reached. Please try again in a moment.",
      },
      { status: 502 },
    );
  }
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
export const HEAD = handler;
