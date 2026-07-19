/**
 * Locale-aware display (and optional migration) for the shared learner persona
 * shown on /app/memory "About me".
 *
 * Historical diagnostics were appended in English under "## Diagnostic calibration"
 * even for Hebrew UI learners. Newer writes use Hebrew; this helper normalizes
 * both shapes for the active UI locale.
 */

const DIAG_SECTION_RE =
  /##\s*(?:Diagnostic calibration|כיול אבחון)\s*\n[\s\S]*?(?=\n##\s|\s*$)/gi;

const DIAG_BULLET_RE =
  /^[-*]\s*(?:Diagnostic calibration|כיול אבחון)\b.*$/gim;

const DIAG_BARE_LINE_RE = /^(?:Diagnostic calibration|כיול אבחון)\b.*$/gim;

/** Strip every diagnostic section + orphan diagnostic bullets. */
export function stripDiagnosticPersonaContent(text: string): string {
  let out = text.replace(DIAG_SECTION_RE, '\n');
  out = out.replace(DIAG_BULLET_RE, '');
  out = out.replace(DIAG_BARE_LINE_RE, '');
  return out.replace(/\n{3,}/g, '\n\n').trim();
}

/**
 * Best-effort translation of a single English diagnostic calibration bullet
 * (the shape produced by diagnostic-plan.ts / persistDiagnosticSummary).
 */
export function translateDiagnosticBulletEnToHe(line: string): string | null {
  const raw = line.replace(/^[-*]\s*/, '').trim();
  if (!/^Diagnostic calibration\b/i.test(raw)) return null;

  const countMatch = raw.match(/\((\d+)\s+validation questions\)/i);
  const qCount = countMatch?.[1] ?? '?';

  const towardMatch = raw.match(/toward\s+\*?\*?(.+?)\*?\*?\./i);
  const toward = towardMatch?.[1]?.trim() ?? 'יעד הלמידה שלך';

  const gapsMatch = raw.match(/Confirmed gaps\s*[—\-]\s*prioritize:\s*(.+?)\./i);
  const noGaps = /No major gaps surfaced/i.test(raw);
  const strengthsMatch = raw.match(/Validated strengths:\s*(.+?)\./i);
  const focusMatch = raw.match(/Week-1 focus:\s*(.+?)\./i);
  const weakStrongMatch = raw.match(
    /\(Weak:\s*(.+?);\s*Strong:\s*(.+?)\)\s*$/i,
  );

  const parts: string[] = [
    `כיול אבחון (${qCount} שאלות אימות) לכיוון **${toward}**.`,
    'כל נושא נבדק ברמת קושי שמתאימה לדירוג העצמי שלך.',
  ];
  if (gapsMatch?.[1]) {
    parts.push(`פערים לאימות — להתמקד ב: ${gapsMatch[1].trim()}.`);
  } else if (noGaps) {
    parts.push('לא עלו פערים גדולים — אפשר להתקדם בנתיב.');
  }
  if (strengthsMatch?.[1]) {
    parts.push(`חוזקות מאומתות: ${strengthsMatch[1].trim()}.`);
  }
  if (focusMatch?.[1]) {
    parts.push(`מיקוד שבוע 1: ${focusMatch[1].trim()}.`);
  }
  const weak = weakStrongMatch?.[1]?.trim();
  const strong = weakStrongMatch?.[2]?.trim();
  if (weak || strong) {
    parts.push(
      `(חלש: ${weak && weak !== 'none' ? weak : 'אין'}; חזק: ${strong && strong !== 'none' ? strong : 'אין'})`,
    );
  }
  return parts.join(' ');
}

const HEADER_MAP_HE: Array<[RegExp, string]> = [
  [/^##\s*How they talk\s*$/gim, '## איך הם מדברים'],
  [/^##\s*How I talk\s*$/gim, '## איך אני מדבר/ת'],
  [/^##\s*How they like explanations\s*$/gim, '## איך הם אוהבים הסברים'],
  [/^##\s*How I like explanations\s*$/gim, '## איך אני אוהב/ת הסברים'],
  [/^##\s*Triggers(?:\s*\/\s*|\s+and\s+)preferences\s*$/gim, '## טריגרים והעדפות'],
  [/^##\s*Recent durable observations.*$/gim, '## תצפיות יציבות אחרונות'],
  [/^##\s*Recent observations.*$/gim, '## תצפיות אחרונות'],
  [/^##\s*About me\s*$/gim, '## עליי'],
  [/^##\s*Diagnostic calibration\s*$/gim, '## כיול אבחון'],
];

const HEADER_MAP_EN: Array<[RegExp, string]> = [
  [/^##\s*איך הם מדברים\s*$/gim, '## How they talk'],
  [/^##\s*איך אני מדבר\/ת\s*$/gim, '## How I talk'],
  [/^##\s*איך הם אוהבים הסברים\s*$/gim, '## How they like explanations'],
  [/^##\s*איך אני אוהב\/ת הסברים\s*$/gim, '## How I like explanations'],
  [/^##\s*טריגרים והעדפות\s*$/gim, '## Triggers and preferences'],
  [/^##\s*תצפיות יציבות אחרונות.*$/gim, '## Recent durable observations'],
  [/^##\s*תצפיות אחרונות.*$/gim, '## Recent observations'],
  [/^##\s*עליי\s*$/gim, '## About me'],
  [/^##\s*כיול אבחון\s*$/gim, '## Diagnostic calibration'],
];

function applyHeaderMap(text: string, map: Array<[RegExp, string]>): string {
  let out = text;
  for (const [re, replacement] of map) out = out.replace(re, replacement);
  return out;
}

/**
 * Localize persona markdown for the Memory "About me" panel.
 * When a locale-matched diagnostic brief is available, it replaces ALL historical
 * diagnostic dumps (often 4+ English repeats) with a single clean section.
 */
export function localizePersonaMarkdown(
  text: string,
  locale: 'he' | 'en',
  diagnosticBriefHe?: string | null,
  diagnosticBriefEn?: string | null,
): string {
  if (!text.trim()) return text;

  const hadDiagnostic =
    /Diagnostic calibration/i.test(text) || /כיול אבחון/.test(text);

  let body = stripDiagnosticPersonaContent(text);

  if (locale === 'he') {
    let brief = diagnosticBriefHe?.trim() || null;
    if (!brief && hadDiagnostic) {
      // Fall back: translate the first English diagnostic bullet we can parse.
      const enLine = text
        .split('\n')
        .map((l) => l.trim())
        .find((l) => /Diagnostic calibration/i.test(l));
      brief = enLine ? translateDiagnosticBulletEnToHe(enLine) : null;
    }
    if (brief) {
      body = `## כיול אבחון\n- ${brief}\n\n${body}`.trim();
    }
    return applyHeaderMap(body, HEADER_MAP_HE);
  }

  // English UI
  const briefEn = diagnosticBriefEn?.trim();
  if (briefEn) {
    body = `## Diagnostic calibration\n- ${briefEn}\n\n${body}`.trim();
  } else if (hadDiagnostic && diagnosticBriefHe?.trim()) {
    // Prefer not to show Hebrew brief on EN UI; keep stripped body only.
  }
  return applyHeaderMap(body, HEADER_MAP_EN);
}

/** True when stored persona still contains English diagnostic dumps. */
export function personaNeedsDiagnosticMigration(text: string | null | undefined): boolean {
  return Boolean(text && /Diagnostic calibration/i.test(text));
}
