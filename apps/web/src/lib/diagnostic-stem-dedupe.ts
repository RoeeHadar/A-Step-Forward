/** Stable fingerprint so Neon UUID rows and lesson-bank hashes dedupe the same MCQ. */
export function diagnosticStemKey(stem: string): string {
  return (stem ?? '')
    .trim()
    .replace(/\s+/g, ' ')
    .toLowerCase()
    .slice(0, 240);
}

export function stemAlreadyAsked(stem: string, askedStemKeys: string[] | undefined): boolean {
  const key = diagnosticStemKey(stem);
  return (askedStemKeys ?? []).includes(key);
}
