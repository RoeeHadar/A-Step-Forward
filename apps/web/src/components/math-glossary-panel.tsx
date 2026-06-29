import { MATH_GLOSSARY_TERMS } from '@/lib/math-glossary';

export function MathGlossaryPanel({ locale }: { locale: 'en' | 'he' }) {
  const isHe = locale === 'he';
  const title = isHe ? '\u05de\u05d9\u05dc\u05d5\u05df \u05de\u05d5\u05e0\u05d7\u05d9\u05dd' : 'Math Glossary';

  return (
    <details className="glass-surface mt-10 rounded-2xl border border-border/60 p-5">
      <summary className="cursor-pointer list-none font-semibold text-foreground marker:content-none [&::-webkit-details-marker]:hidden">
        <span className="inline-flex items-center gap-2">
          <span aria-hidden>{'\u{1F524}'}</span>
          {title}
        </span>
      </summary>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[28rem] border-collapse text-sm">
          <thead>
            <tr className="border-b border-border text-start text-xs uppercase tracking-wide text-muted-foreground">
              <th className="px-3 py-2 font-medium">{isHe ? '\u05e2\u05d1\u05e8\u05d9\u05ea' : 'Hebrew'}</th>
              <th className="px-3 py-2 font-medium">{isHe ? '\u05d0\u05e0\u05d2\u05dc\u05d9\u05ea' : 'English'}</th>
              <th className="px-3 py-2 font-medium" dir="rtl">
                {isHe ? '\u05e2\u05e8\u05d1\u05d9\u05ea' : 'Arabic'}
              </th>
            </tr>
          </thead>
          <tbody>
            {MATH_GLOSSARY_TERMS.map((row) => (
              <tr key={row.he} className="border-b border-border/40 last:border-0">
                <td className="px-3 py-2 font-medium text-foreground" dir="rtl">
                  {row.he}
                </td>
                <td className="px-3 py-2 text-muted-foreground">{row.en}</td>
                <td className="px-3 py-2 text-foreground" dir="rtl">
                  {row.ar}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}