/**
 * Shared Groq chat-completions helper for curriculum scripts.
 */
const GROQ_MODELS = ['llama-3.1-8b-instant', 'llama-3.3-70b-versatile'];

export function getGroqApiKey() {
  return process.env.GROQ_API_KEY || process.env.LLM_API_KEY || '';
}

function parseRetryAfterMs(resp) {
  const header = resp.headers.get('retry-after');
  if (header) {
    const sec = Number.parseFloat(header);
    if (!Number.isNaN(sec)) return Math.ceil(sec * 1000);
  }
  return 65_000;
}

export async function callGroq(messages, { maxTokens = 4096, temperature = 0.45, timeoutMs = 120_000, maxRetries = 6 } = {}) {
  const apiKey = getGroqApiKey();
  if (!apiKey) return null;

  for (const model of GROQ_MODELS) {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeoutMs);
      try {
        const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model,
            messages,
            response_format: { type: 'json_object' },
            max_tokens: maxTokens,
            temperature,
          }),
          signal: controller.signal,
        });
        clearTimeout(timer);
        if (resp.ok) {
          const body = await resp.json();
          const content = body?.choices?.[0]?.message?.content;
          if (content) return { content, model };
          continue;
        }
        const errText = await resp.text().catch(() => '');
        console.warn(`[groq] ${model} attempt ${attempt + 1} → ${resp.status}: ${errText.slice(0, 180)}`);
        if (resp.status === 401 || resp.status === 403) return null;
        if (resp.status === 429 || resp.status === 413) {
          const waitMs = parseRetryAfterMs(resp);
          console.warn(`[groq] rate limit — waiting ${Math.round(waitMs / 1000)}s…`);
          await new Promise((r) => setTimeout(r, waitMs));
          continue;
        }
        break;
      } catch (err) {
        clearTimeout(timer);
        console.warn(`[groq] ${model} error: ${err.message}`);
        if (attempt < maxRetries - 1) {
          await new Promise((r) => setTimeout(r, 10_000));
        }
      }
    }
  }
  return null;
}

export function parseJsonLoose(text) {
  const trimmed = text.trim();
  try {
    return JSON.parse(trimmed);
  } catch {
    const start = trimmed.indexOf('{');
    const end = trimmed.lastIndexOf('}');
    if (start >= 0 && end > start) {
      return JSON.parse(trimmed.slice(start, end + 1));
    }
    throw new Error('No JSON object in model response');
  }
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

export { sleep };
