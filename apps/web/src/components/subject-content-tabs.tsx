'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { Badge } from '@asf/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@asf/ui/tabs';
import { MarkdownReader } from '@/components/markdown-reader';
import type { BagrutExam, ContentSection } from '@/lib/content-api';
import { fetchSectionsPage } from '@/lib/content-api';

type SubjectContentTabsProps = {
  subject: string;
  initialSections: ContentSection[];
  initialTotal: number;
  initialGrades: string[];
  bagrutExams: BagrutExam[];
  defaultTab?: 'textbook' | 'bagrut';
};

export function SubjectContentTabs({
  subject,
  initialSections,
  initialTotal,
  initialGrades,
  bagrutExams,
  defaultTab = 'textbook',
}: SubjectContentTabsProps) {
  const [tab, setTab] = useState(defaultTab);
  const [sections, setSections] = useState(initialSections);
  const [total, setTotal] = useState(initialTotal);
  const [page, setPage] = useState(1);
  const [gradeFilter, setGradeFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedExam, setSelectedExam] = useState<BagrutExam | null>(bagrutExams[0] ?? null);

  const grades = initialGrades;

  const pageSize = 20;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const loadPage = useCallback(
    async (nextPage: number, grade: string) => {
      setLoading(true);
      try {
        const result = await fetchSectionsPage(
          subject,
          {
            page: nextPage,
            page_size: pageSize,
            grade: grade || undefined,
          },
          true,
        );
        setSections(result.items);
        setTotal(result.total);
        setPage(nextPage);
      } catch {
        // Keep current sections visible; pagination controls stay usable for retry.
      } finally {
        setLoading(false);
      }
    },
    [subject],
  );

  useEffect(() => {
    loadPage(1, gradeFilter);
  }, [gradeFilter, loadPage]);

  return (
    <Tabs
      value={tab}
      onValueChange={(value) => setTab(value as 'textbook' | 'bagrut')}
      className="w-full"
    >
      <TabsList className="mb-6">
        <TabsTrigger value="textbook">Textbook</TabsTrigger>
        <TabsTrigger value="bagrut" disabled={bagrutExams.length === 0}>
          Bagrut Exams
          {bagrutExams.length > 0 ? (
            <Badge variant="secondary" className="ml-2">
              {bagrutExams.length}
            </Badge>
          ) : null}
        </TabsTrigger>
      </TabsList>

      <TabsContent value="textbook" className="space-y-4">
        {grades.length > 0 ? (
          <div className="flex flex-wrap items-center gap-3">
            <label htmlFor="grade-filter" className="text-sm text-muted-foreground">Grade</label>
            <select
              id="grade-filter"
              value={gradeFilter}
              onChange={(e) => setGradeFilter(e.target.value)}
              className="glass-surface rounded-lg border border-border bg-surface-1/50 px-3 py-2 text-sm"
            >
              <option value="">All grades</option>
              {grades.map((g) => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
          </div>
        ) : null}

        {sections.length === 0 ? (
          <p className="text-muted-foreground">
            No parsed sections yet for this subject. Bagrut exams may still be available in the other tab.
          </p>
        ) : (
          <div className="space-y-4">
            {sections.map((section) => (
              <Card key={`${section.title}-${section.chunk_index ?? 0}`} className="glass-surface border-border/60">
                <CardHeader className="pb-2">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <CardTitle className="text-lg" dir="auto">{section.title}</CardTitle>
                    <div className="flex flex-wrap gap-2">
                      {section.grade ? <Badge variant="outline">{section.grade}</Badge> : null}
                      {section.page_start != null ? (
                        <Badge variant="secondary">
                          p. {section.page_start}
                          {section.page_end != null && section.page_end !== section.page_start
                            ? `–${section.page_end}`
                            : ''}
                        </Badge>
                      ) : null}
                    </div>
                  </div>
                  {section.chunk_index != null ? (
                    <Link
                      href={`/learn/${subject}/${section.chunk_index}`}
                      className="text-xs text-primary hover:underline"
                    >
                      Open full page
                    </Link>
                  ) : null}
                </CardHeader>
                <CardContent dir="rtl" className="prose-container">
                  <MarkdownReader content={section.body_md} />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {totalPages > 1 ? (
          <div className="flex items-center justify-between gap-4 pt-2">
            <p className="text-sm text-muted-foreground">
              Page {page} of {totalPages} · {total} sections
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={page <= 1 || loading}
                onClick={() => loadPage(page - 1, gradeFilter)}
                className="rounded-lg border border-border px-3 py-1.5 text-sm disabled:opacity-50"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={page >= totalPages || loading}
                onClick={() => loadPage(page + 1, gradeFilter)}
                className="rounded-lg border border-border px-3 py-1.5 text-sm disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        ) : null}
      </TabsContent>

      <TabsContent value="bagrut">
        {bagrutExams.length === 0 ? (
          <p className="text-muted-foreground">No Bagrut exams available for this subject yet.</p>
        ) : (
          <div className="flex flex-col gap-6 lg:flex-row">
            <ul className="space-y-2 lg:w-72 shrink-0">
              {bagrutExams.map((exam) => (
                <li key={`${exam.display_name}-${exam.year ?? 'na'}`}>
                  <button
                    type="button"
                    onClick={() => setSelectedExam(exam)}
                    className={`w-full rounded-lg border px-3 py-2 text-start text-sm transition-colors ${
                      selectedExam?.display_name === exam.display_name &&
                      selectedExam?.year === exam.year
                        ? 'border-primary bg-primary/10 text-foreground'
                        : 'border-border bg-surface-1/40 text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    <span className="font-medium">{exam.display_name}</span>
                    <span className="mt-1 flex flex-wrap gap-1">
                      {exam.year != null ? (
                        <Badge variant="secondary" className="text-xs">{exam.year}</Badge>
                      ) : null}
                      <Badge variant="outline" className="text-xs">{exam.exam_type}</Badge>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
            <Card className="glass-surface min-h-[70vh] flex-1 overflow-hidden">
              {selectedExam ? (
                <iframe
                  src={selectedExam.file_url}
                  title={selectedExam.display_name}
                  className="h-[70vh] w-full border-0"
                />
              ) : (
                <CardContent className="p-8 text-muted-foreground">
                  Select an exam to view the PDF.
                </CardContent>
              )}
            </Card>
          </div>
        )}
      </TabsContent>
    </Tabs>
  );
}
