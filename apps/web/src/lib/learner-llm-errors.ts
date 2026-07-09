import type { LLMFailureInfo, LLMFailureKind } from '@/lib/llm-provider';

export type LearnerLocale = 'he' | 'en';

const AGENT_HEADS: Record<LearnerLocale, Record<string, string>> = {
  he: {
    tutor: 'אני המורה שלך.',
    mentor: 'אני המנטור שלך.',
    coach: 'אני המאמן שלך.',
    reviewer: 'אני הבודק שלך.',
  },
  en: {
    tutor: "I'm your Tutor.",
    mentor: "I'm your Mentor.",
    coach: "I'm your Coach.",
    reviewer: "I'm your Reviewer.",
  },
};

const REASON: Record<LearnerLocale, Record<LLMFailureKind, string>> = {
  he: {
    not_configured: 'שירות הבינה המלאכותית לא זמין כרגע.',
    auth_failure: 'יש בעיית הגדרה בשרת — הצוות בודק.',
    rate_limited: 'יותר מדי בקשות זמניות לשירות המודל.',
    timeout: 'התשובה לקחה יותר מדי זמן.',
    context_too_large:
      'הבקשה הייתה גדולה מדי לספק המודל. זה בדרך כלל בגלל רקע שהמערכת שולחת, לא בגלל השאלה שלך.',
    provider_error: 'ספק המודל החזיר שגיאה זמנית.',
    empty_response: 'המודל לא החזיר תשובה.',
    network_error: 'לא הצלחנו להתחבר לשירות המודל.',
    stream_interrupted: 'התשובה נקטעה באמצע.',
    unknown: 'לא הצלחנו לקבל תשובה כרגע.',
  },
  en: {
    not_configured: 'The AI service is unavailable right now.',
    auth_failure: 'There is a server configuration issue — our team is checking.',
    rate_limited: 'Too many temporary requests to the model service.',
    timeout: 'The response took too long.',
    context_too_large:
      'The request was too large for the model provider — usually platform background, not your question.',
    provider_error: 'The model provider returned a temporary error.',
    empty_response: 'The model returned no answer.',
    network_error: 'We could not reach the model service.',
    stream_interrupted: 'The response was cut off mid-stream.',
    unknown: 'We could not get a response right now.',
  },
};

const ACTION: Record<LearnerLocale, Record<LLMFailureKind, string>> = {
  he: {
    not_configured: 'נסה שוב בעוד דקה, או עיין ב-**/learn**.',
    auth_failure: 'נסה שוב מאוחר יותר.',
    rate_limited: 'המתן דקה ושלח שוב.',
    timeout: 'רענן ושלח שוב — שאלה קצרה עוזרת.',
    context_too_large: 'שלח שוב — שאלה קצרה או שיחה חדשה.',
    provider_error: 'נסה שוב בעוד רגע, או עיין ב-**/learn**.',
    empty_response: 'שלח את השאלה שוב.',
    network_error: 'בדוק חיבור לאינטרנט ורענן.',
    stream_interrupted: 'שלח את השאלה שוב.',
    unknown: 'נסה שוב בעוד רגע.',
  },
  en: {
    not_configured: 'Try again in a minute, or browse **/learn**.',
    auth_failure: 'Try again later.',
    rate_limited: 'Wait a minute and send again.',
    timeout: 'Refresh and resend — a shorter question helps.',
    context_too_large: 'Try again — a shorter question or new chat helps.',
    provider_error: 'Try again shortly, or browse **/learn**.',
    empty_response: 'Send your question again.',
    network_error: 'Check your connection and refresh.',
    stream_interrupted: 'Send your question again.',
    unknown: 'Try again in a moment.',
  },
};

function agentHead(agent: string, locale: LearnerLocale): string {
  return AGENT_HEADS[locale][agent] ?? (locale === 'he' ? 'אני העוזר שלך.' : "I'm your assistant.");
}

/** Learner-facing chat message when the LLM path fails. */
export function buildChatFailureMessage(params: {
  agent: string;
  locale: LearnerLocale;
  failure: LLMFailureInfo;
  messagePreview?: string;
  showTechnicalDetail?: boolean;
}): string {
  const { agent, locale, failure, messagePreview, showTechnicalDetail = false } = params;
  const kind = failure.kind ?? 'unknown';
  const preview = messagePreview?.trim().slice(0, 100);
  const lines = [
    agentHead(agent, locale),
    '',
    locale === 'he' ? `**מה קרה:** ${REASON.he[kind]}` : `**What happened:** ${REASON.en[kind]}`,
    '',
    locale === 'he' ? `**מה לעשות:** ${ACTION.he[kind]}` : `**What to do:** ${ACTION.en[kind]}`,
  ];

  if (showTechnicalDetail && (failure.status || failure.provider)) {
    const parts: string[] = [];
    if (failure.provider) parts.push(failure.provider);
    if (failure.status) parts.push(String(failure.status));
    lines.push('', locale === 'he' ? `(${parts.join(' · ')})` : `(${parts.join(' · ')})`);
  }

  if (preview) {
    lines.push(
      '',
      locale === 'he' ? `שאלת: *"${preview}"*` : `You asked: *"${preview}"*`,
    );
  }

  lines.push(
    '',
    locale === 'he'
      ? 'אם השאלה לא נשלחה, נסה שוב. אפשר גם לעיין ב-**/learn**.'
      : 'If your message did not go through, try again. You can also browse **/learn**.',
  );
  return lines.join('\n');
}
