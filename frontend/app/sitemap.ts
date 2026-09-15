import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL || "https://smart-hire-gen-ai-swart.vercel.app";
  return [
    { url: base, changeFrequency: "weekly", priority: 1 },
    { url: `${base}/login`, changeFrequency: "monthly", priority: 0.4 },
    { url: `${base}/signup`, changeFrequency: "monthly", priority: 0.5 },
  ];
}
