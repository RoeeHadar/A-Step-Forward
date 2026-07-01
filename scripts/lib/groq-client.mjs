/**
 * Shared Groq chat-completions helper for curriculum scripts.
 */
const GROQ_MODELS = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant'];

export function getGroqApiKey() {
  return process.env.GROQ_API_KEY || process.env.LLM_API_KEY || '';
}

export async function callGroq(messages, { maxTokens = 8192, temperature = 0.45, timeoutMs = 90_000 } = {}) {
  const apiKey = getGroqApiKey();
  if (!apiKey) return null;

  for (const model of GROQ_MODELS) {
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
      if (!resp.ok) {
        const errText = await resp.text().catch(() => '');
        console.warn(`[groq] ${model} → ${resp.status}: ${errText.slice(0, 200)}`);
        if (resp.status === 401 || resp.status === 403) return null;
        continue;
      }
      const body = await resp.json();
      const content = body?.choices?.[0]?.message?.content;
      if (!content) continue;
      return { content, model };
    } catch (err) {
      clearTimeout(timer);
      console.warn(`[groq] ${model} error: ${err.message}`);
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
