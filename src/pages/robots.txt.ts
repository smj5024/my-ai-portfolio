import type { APIRoute } from 'astro';

export const GET: APIRoute = ({ site }) => {
  const origin = site?.origin ?? 'https://smj5024.github.io';
  return new Response(`User-agent: *\nAllow: /\nSitemap: ${origin}/my-ai-portfolio/sitemap-index.xml\n`, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
