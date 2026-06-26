/**
 * TEMPORARY public diagnostic. Returns which env vars are configured (booleans
 * only — no values) and tries a 1-token Groq call to verify the key actually
 * works. Remove once chat is verified live.
 */
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

async function probeGroq(apiKey: string | undefined): Promise<{ ok: boolean; status?: number; body?: string }> {
  if (!apiKey) return { ok: false, status: 0, body: 'no key' };
  try {
    const controller = new AbortController();
    const t = setTimeout(() => controller.abort(), 8000);
    const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'llama-3.1-8b-instant',
        messages: [{ role: 'user', content: 'ping' }],
        max_tokens: 5,
        stream: false,
      }),
      signal: controller.signal,
    });
    clearTimeout(t);
    const text = await resp.text();
    return { ok: resp.ok, status: resp.status, body: text.slice(0, 300) };
  } catch (err) {
    return { ok: false, status: 0, body: String(err) };
  }
}

export async function GET() {
  const env = {
    DATABASE_URL: Boolean(process.env.DATABASE_URL),
    POSTGRES_URL: Boolean(process.env.POSTGRES_URL),
    GROQ_API_KEY: Boolean(process.env.GROQ_API_KEY),
    CLERK_SECRET_KEY: Boolean(process.env.CLERK_SECRET_KEY),
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY),
    NEXT_PUBLIC_API_BASE_URL: Boolean(process.env.NEXT_PUBLIC_API_BASE_URL),
    NODE_ENV: process.env.NODE_ENV,
    VERCEL_ENV: process.env.VERCEL_ENV,
    VERCEL_REGION: process.env.VERCEL_REGION,
  };

  const groqProbe = await probeGroq(process.env.GROQ_API_KEY);

  return Response.json({ env, groqProbe });
}
