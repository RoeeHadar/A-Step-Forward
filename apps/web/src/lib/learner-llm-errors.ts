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
    not_configured:
      'שירות הבינה המלאכותית לא מוגדר בשרת כרגע, ולכן לא ניתן לעבד את הבקשה.',
    auth_failure:
      'יש בעיית אימות מול ספק המודל. הצוות הטכני צריך לבדוק את ההגדרות.',
    rate_limited:
      'הגענו למגבלת בקשות זמנית לשירות המודל — זה קורה לעיתים בשעות עומס.',
    timeout:
      'הבקשה ארכה יותר מדי לפני שהתקבלה תשובה. ייתכן שהשיחה ארוכה או שהשירות איטי כרגע.',
    context_too_large:
      'ההקשר של השיחה גדול מדי למודל. נסה שאלה קצרה יותר או התחל שיחה חדשה.',
    provider_error:
      'ספק המודל החזיר שגיאה זמנית ולא סיפק תשובה.',
    empty_response: 'המודל החזיר תשובה ריקה.',
    network_error: 'לא הצלחנו להתחבר לשירות המודל.',
    stream_interrupted: 'התשובה נקטעה באמצע בגלל תקלה בחיבור.',
    unknown: 'לא הצלחנו לקבל תשובה מהמודל.',
  },
  en: {
    not_configured:
      'The AI service is not configured on the server, so your request could not be processed.',
    auth_failure:
      'There is an authentication problem with the model provider. The technical team needs to check the configuration.',
    rate_limited:
      'We hit a temporary rate limit on the model service — this sometimes happens during busy periods.',
    timeout:
      'The request took too long before a response arrived. The conversation may be long or the service may be slow right now.',
    context_too_large:
      'The conversation context is too large for the model. Try a shorter question or start a new chat.',
    provider_error:
      'The model provider returned a temporary error and did not supply an answer.',
    empty_response: 'The model returned an empty response.',
    network_error: 'We could not connect to the model service.',
    stream_interrupted: 'The response was cut off mid-stream because of a connection issue.',
    unknown: 'We could not get a response from the model.',
  },
};

const ACTIONS: Record<LearnerLocale, Record<LLMFailureKind, string[]>> = {
  he: {
    not_configured: ['נסה שוב בעוד כמה דקות.', 'בינתיים אפשר ללמוד ב-**/learn**.'],
    auth_failure: ['נסה שוב מאוחר יותר.', 'אם הבעיה נמשכת, פנה לתמיכה.'],
    rate_limited: [
      'המתן דקה ושלח שוב — המגבלה בדרך כלל מתאפסת מהר.',
      'בינתיים אפשר ללמוד ב-**/learn**.',
    ],
    timeout: [
      'נסה שוב עם שאלה קצרה יותר.',
      'רענן את הדף ושלח מחדש.',
    ],
    context_too_large: [
      'שלח שאלה קצרה וממוקדת.',
      'או פתח שיחה חדשה עם אותו סוכן.',
    ],
    provider_error: [
      'נסה שוב בעוד רגע.',
      'בינתיים אפשר ללמוד ב-**/learn**.',
    ],
    empty_response: ['שלח שוב את השאלה.', 'נסח אותה מחדש בקצרה אם אפשר.'],
    network_error: [
      'בדוק את החיבור לאינטרנט.',
      'רענן את הדף ונסה שוב.',
    ],
    stream_interrupted: [
      'שלח שוב את השאלה.',
      'אם זה חוזר, נסה שאלה קצרה יותר.',
    ],
    unknown: [
      'נסה שוב בעוד רגע.',
      'בינתיים אפשר ללמוד ב-**/learn**.',
    ],
  },
  en: {
    not_configured: ['Try again in a few minutes.', 'Meanwhile, browse **/learn**.'],
    auth_failure: ['Try again later.', 'If this persists, contact support.'],
    rate_limited: [
      'Wait a minute and send again — the limit usually resets quickly.',
      'Meanwhile, browse **/learn**.',
    ],
    timeout: [
      'Try again with a shorter question.',
      'Refresh the page and resend.',
    ],
    context_too_large: [
      'Send a shorter, focused question.',
      'Or start a new chat with the same agent.',
    ],
    provider_error: [
      'Try again in a moment.',
      'Meanwhile, browse **/learn**.',
    ],
    empty_response: ['Send your question again.', 'Rephrase it briefly if you can.'],
    network_error: [
      'Check your internet connection.',
      'Refresh the page and try again.',
    ],
    stream_interrupted: [
      'Send your question again.',
      'If it keeps happening, try a shorter question.',
    ],
    unknown: [
      'Try again in a moment.',
      'Meanwhile, browse **/learn**.',
    ],
  },
};

const LABELS: Record<LearnerLocale, { whatHappened: string; yourQuestion: string; whatToDo: string; saved: string; detail: string }> = {
  he: {
    whatHappened: '**מה קרה:**',
    yourQuestion: '**השאלה שלך:**',
    whatToDo: '**מה לעשות:**',
    saved: 'ההודעה שלך נשמרה בהיסטוריית הצ\'אט, ואראה אותה בסיבוב הבא.',
    detail: '**פרטים טכניים:**',
  },
  en: {
    whatHappened: '**What happened:**',
    yourQuestion: '**Your question:**',
    whatToDo: '**What to do:**',
    saved: 'Your message is saved in your chat history, so I will see it on the next turn.',
    detail: '**Technical detail:**',
  },
};

function agentHead(agent: string, locale: LearnerLocale): string {
  return AGENT_HEADS[locale][agent] ?? (locale === 'he' ? 'אני העוזר שלך.' : "I'm your assistant.");
}

function technicalDetail(failure: LLMFailureInfo, locale: LearnerLocale): string | null {
  const parts: string[] = [];
  if (failure.provider) {
    parts.push(locale === 'he' ? `ספק: ${failure.provider}` : `Provider: ${failure.provider}`);
  }
  if (failure.status) {
    parts.push(locale === 'he' ? `קוד שגיאה: ${failure.status}` : `Error code: ${failure.status}`);
  }
  if (failure.model) {
    parts.push(locale === 'he' ? `מודל: ${failure.model}` : `Model: ${failure.model}`);
  }
  return parts.length ? parts.join(' · ') : null;
}

/** Learner-facing chat message when the LLM path fails. */
export function buildChatFailureMessage(params: {
  agent: string;
  locale: LearnerLocale;
  failure: LLMFailureInfo;
  messagePreview?: string;
}): string {
  const { agent, locale, failure, messagePreview } = params;
  const kind = failure.kind ?? 'unknown';
  const labels = LABELS[locale];
  const preview = messagePreview?.trim().slice(0, 120);
  const actions = ACTIONS[locale][kind] ?? ACTIONS[locale].unknown;
  const detail = technicalDetail(failure, locale);

  const lines = [
    agentHead(agent, locale),
    '',
    labels.whatHappened,
    REASON[locale][kind] ?? REASON[locale].unknown,
  ];

  if (detail) {
    lines.push('', labels.detail, detail);
  }

  if (preview) {
    lines.push('', labels.yourQuestion, `*"${preview}"*`);
  }

  lines.push('', labels.whatToDo);
  for (const action of actions) {
    lines.push(`- ${action}`);
  }

  lines.push('', labels.saved);
  return lines.join('\n');
}
