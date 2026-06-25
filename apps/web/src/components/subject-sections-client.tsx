'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import type { SectionSummary } from '@/lib/content-api';

export function SubjectSectionsClient({
  subject,
  sections,
}: {
  subject: string;
  sections: SectionSummary[];
}) {
  const [query, setQuery] = useState('');
  const [gradeFilter, setGradeFilter] = useState('');

  const grades = useMemo(
    () => [...new Set(sections.map((s) => s.grade).filter(Boolean))] as string[],
    [sections],
  );

  const filtered = useMemo(() => {
    return sections.filter((s) => {
      const q = query.trim().toLowerCase();
      const matchesQuery =
        !q ||
        s.title.toLowerCase().includes(q) ||
        (s.title_en?.toLowerCase().includes(q) ?? false) ||
        s.source_file.toLowerCase().includes(q);
      const matchesGrade = !gradeFilter || s.grade === gradeFilter;
      return matchesQuery && matchesGrade;
    });
  }, [sections, query, gradeFilter]);

  if (sections.length === 0) {
    return (
      <p className="text-muted-foreground">
        No parsed sections yet for this subject. Bagrut exams may still be available above.
      </p>
    );
  }

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-3">
        <input
          type="search"
          placeholder="Search sections…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="glass-surface min-w-[200px] flex-1 rounded-lg border border-border bg-surface-1/50 px-3 py-2 text-sm"
          aria-label="Search sections"
        />
        {grades.length > 0 ? (
          <select
            value={gradeFilter}
            onChange={(e) => setGradeFilter(e.target.value)}
            className="glass-surface rounded-lg border border-border bg-surface-1/50 px-3 py-2 text-sm"
            aria-label="Filter by grade"
          >
            <option value="">All grades</option>
            {grades.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        ) : null}
      </div>

      <ol className="space-y-2">
        {filtered.map((s) => (
          <li key={s.id}>
            <Link
              href={`/learn/${subject}/${s.chunk_index}`}
              className="glass-surface flex items-center justify-between gap-3 rounded-xl px-4 py-3 transition-colors hover:border-primary/30"
            >
              <span className="font-medium text-foreground" dir="auto">
                {s.title}
              </span>
              <span className="shrink-0 text-xs text-muted-foreground">
                Ch. {s.chunk_index + 1}
                {s.grade ? ` · ${s.grade}` : ''}
              </span>
            </Link>
          </li>
        ))}
      </ol>
    </div>
  );
}
