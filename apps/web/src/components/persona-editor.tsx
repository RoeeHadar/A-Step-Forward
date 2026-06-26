'use client';

import { useState, useTransition } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { Button } from '@asf/ui/button';
import { Badge } from '@asf/ui/badge';
import { useLanguagePreference } from '@/hooks/use-language-preference';

/**
 * Persona editor — pure client. Talks to:
 *   - GET  /api/agent-memory/persona     (initial load is server-side)
 *   - POST /api/agent-memory/persona     (full replace on Save)
 *   - POST /api/agent-memory/consolidate (Rebuild from notes — calls Groq)
 *
 * The persona body is stored as free-form markdown with H2 section
 * headers + bullet list lines. The editor exposes:
 *   - a single textarea (markdown source) so we don't lock the user into
 *     our recommended section names if they want their own,
 *   - a Save button that replaces the body,
 *   - a Rebuild button that triggers an LLM consolidation pass over the
 *     learner's per-agent private notes.
 */
const STR = {
  he: {
    title: 'הפרסונה שלך',
    blurb: 'זהו מסמך CLAUDE.md אישי שכל הסוכנים קוראים בכל פניה. הוא מתאר איך אתה לומד — לא מה אתה יודע. אפשר לערוך, לשמור, או לבקש מהמערכת לבנות אותו מחדש מההערות שהסוכנים אספו עליך.',
    updated: 'עודכן לאחרונה',
    never_updated: 'טרם נכתב',
    empty_hint: 'הפרסונה ריקה. הוסף סעיפים כמו "## איך אני מדבר", "## איך אני אוהב הסברים", "## טריגרים והעדפות" כדי להתחיל.',
    save: 'שמור',
    saving: 'שומר…',
    saved: 'נשמר',
    save_error: 'השמירה נכשלה. נסה שוב.',
    rebuild: 'בנה מחדש מההערות',
    rebuilding: 'בונה…',
    rebuild_done: (a: number, c: number) =>
      `נבנה מחדש: ${c} הערות סוכנים נשקלו, ${a} מוזגו לפרסונה ונארכבו.`,
    rebuild_skipped: (reason: string) => `לא הופעל: ${reason}`,
    rebuild_error: 'הבנייה מחדש נכשלה.',
    chars: 'תווים',
    notes_title: 'הערות פרטיות לפי סוכן',
    notes_blurb: 'לכל סוכן יש פנקס משלו עליך — סוכנים אחרים לא רואים אותו. בנייה מחדש לוקחת את ההערות החשובות ומקודדת אותן לפרסונה.',
    no_notes: 'אין הערות',
    notes_for: (n: number) => `${n} הערות`,
    delete_section: 'מחק',
  },
  en: {
    title: 'Your persona',
    blurb: 'This is your personal CLAUDE.md — every AI agent reads it on every turn. It describes HOW you learn, not WHAT you know. You can edit it, save, or ask the system to rebuild it from the notes the agents have collected.',
    updated: 'Last updated',
    never_updated: 'Never written',
    empty_hint: 'Persona is empty. Add sections like "## How I talk", "## How I like explanations", "## Triggers and preferences" to get started.',
    save: 'Save',
    saving: 'Saving…',
    saved: 'Saved',
    save_error: 'Save failed. Try again.',
    rebuild: 'Rebuild from notes',
    rebuilding: 'Rebuilding…',
    rebuild_done: (a: number, c: number) =>
      `Rebuilt: ${c} agent notes considered, ${a} merged into persona and archived.`,
    rebuild_skipped: (reason: string) => `Skipped: ${reason}`,
    rebuild_error: 'Rebuild failed.',
    chars: 'chars',
    notes_title: 'Per-agent private notes',
    notes_blurb: 'Each agent has its own private notes about you — other agents don\u2019t see them. Rebuilding promotes important notes into your persona.',
    no_notes: 'No notes',
    notes_for: (n: number) => `${n} notes`,
    delete_section: 'Delete',
  },
} as const;

interface RebuildResult {
  ran: boolean;
  reason?: string;
  notes_considered: number;
  notes_archived: number;
}

function formatDate(iso: string | null, isHe: boolean): string {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleString(isHe ? 'he-IL' : 'en-GB', {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  } catch {
    return iso;
  }
}

export function PersonaEditor({
  initialText,
  updatedAt,
  noteCountsByAgent,
}: {
  initialText: string | null;
  updatedAt: string | null;
  noteCountsByAgent: Record<string, number>;
}) {
  const [lang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';

  const [text, setText] = useState(initialText ?? '');
  const [updated, setUpdated] = useState(updatedAt);
  const [status, setStatus] = useState<
    | { kind: 'idle' }
    | { kind: 'saved' }
    | { kind: 'rebuilt'; result: RebuildResult }
    | { kind: 'error'; msg: string }
  >({ kind: 'idle' });
  const [savePending, startSave] = useTransition();
  const [rebuildPending, startRebuild] = useTransition();

  function save() {
    startSave(async () => {
      setStatus({ kind: 'idle' });
      try {
        const res = await fetch('/api/agent-memory/persona', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text }),
        });
        if (!res.ok) throw new Error(await res.text());
        setUpdated(new Date().toISOString());
        setStatus({ kind: 'saved' });
      } catch (err) {
        setStatus({
          kind: 'error',
          msg: err instanceof Error ? err.message : t.save_error,
        });
      }
    });
  }

  function rebuild() {
    startRebuild(async () => {
      setStatus({ kind: 'idle' });
      try {
        const res = await fetch('/api/agent-memory/consolidate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ force: false }),
        });
        if (!res.ok) throw new Error(await res.text());
        const data = (await res.json()) as RebuildResult & {
          persona_chars_after?: number;
        };
        // Pull the fresh persona back so the textarea reflects the LLM-merged body.
        const next = await fetch('/api/agent-memory/persona');
        if (next.ok) {
          const body = (await next.json()) as {
            text: string | null;
            updated_at: string | null;
          };
          setText(body.text ?? '');
          setUpdated(body.updated_at);
        }
        setStatus({ kind: 'rebuilt', result: data });
      } catch (err) {
        setStatus({
          kind: 'error',
          msg: err instanceof Error ? err.message : t.rebuild_error,
        });
      }
    });
  }

  return (
    <div className="space-y-6" dir={isHe ? 'rtl' : 'ltr'} lang={lang}>
      <Card className="glass-surface border-border/60">
        <CardHeader>
          <CardTitle>{t.title}</CardTitle>
          <p className="text-sm text-muted-foreground">{t.blurb}</p>
          <p className="text-xs text-muted-foreground">
            {t.updated}: {updated ? formatDate(updated, isHe) : t.never_updated}
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {text.length === 0 && (
            <p className="text-sm text-muted-foreground italic">{t.empty_hint}</p>
          )}
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value.slice(0, 4000))}
            className="w-full min-h-[260px] rounded-lg border border-border/60 bg-card/50 p-3 font-mono text-sm leading-relaxed focus:border-primary focus:outline-none"
            placeholder={'## How I talk\n- ...\n\n## How I like explanations\n- ...'}
            spellCheck={false}
            dir="ltr" // markdown source is always LTR even when UI is RTL
            aria-label={t.title}
          />
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs text-muted-foreground">
              {text.length}/4000 {t.chars}
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                disabled={rebuildPending}
                onClick={rebuild}
              >
                {rebuildPending ? t.rebuilding : t.rebuild}
              </Button>
              <Button disabled={savePending} onClick={save}>
                {savePending ? t.saving : t.save}
              </Button>
            </div>
          </div>

          {status.kind === 'saved' && (
            <p className="text-sm text-green-500">{t.saved}</p>
          )}
          {status.kind === 'rebuilt' && (
            <p className="text-sm text-green-500">
              {status.result.ran
                ? t.rebuild_done(
                    status.result.notes_archived,
                    status.result.notes_considered,
                  )
                : t.rebuild_skipped(status.result.reason ?? 'unknown')}
            </p>
          )}
          {status.kind === 'error' && (
            <p className="text-sm text-red-400">{status.msg}</p>
          )}
        </CardContent>
      </Card>

      <Card className="glass-surface border-border/60">
        <CardHeader>
          <CardTitle className="text-base">{t.notes_title}</CardTitle>
          <p className="text-sm text-muted-foreground">{t.notes_blurb}</p>
        </CardHeader>
        <CardContent>
          <ul className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {Object.entries(noteCountsByAgent).map(([agent, n]) => (
              <li
                key={agent}
                className="flex items-center justify-between rounded-lg border border-border/60 bg-card/50 px-3 py-2"
              >
                <span className="font-mono text-sm">{agent}</span>
                <Badge variant={n > 0 ? 'default' : 'secondary'}>
                  {n > 0 ? t.notes_for(n) : t.no_notes}
                </Badge>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
