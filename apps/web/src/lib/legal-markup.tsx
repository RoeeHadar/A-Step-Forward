/**
 * Tiny renderer for the legal page text in legal-content.ts. Supports only
 * what the drafts use: paragraphs, "- " bullet lists, a line that is all
 * **bold** (rendered as a section heading), inline **bold**, *italic*,
 * [label](/path) links, and [[...]] blanks that Roee still has to fill in.
 */
import Link from 'next/link';
import type { ReactNode } from 'react';

export type LegalBlock =
  | { kind: 'heading'; text: string }
  | { kind: 'paragraph'; text: string }
  | { kind: 'list'; items: string[] };

const BOLD_LINE = /^\*\*([^*]+)\*\*$/;

export function parseLegalBlocks(body: string): LegalBlock[] {
  const blocks: LegalBlock[] = [];
  let list: string[] | null = null;
  for (const raw of body.split('\n')) {
    const line = raw.trim();
    if (line.startsWith('- ')) {
      if (!list) {
        list = [];
        blocks.push({ kind: 'list', items: list });
      }
      list.push(line.slice(2).trim());
      continue;
    }
    list = null;
    if (!line) continue;
    const heading = BOLD_LINE.exec(line);
    blocks.push(heading ? { kind: 'heading', text: heading[1] ?? '' } : { kind: 'paragraph', text: line });
  }
  return blocks;
}

const PLACEHOLDER = /\[\[([\s\S]+?)\]\]/g;

/** The [[...]] blanks in a text, in order (for tests and the handoff list). */
export function legalPlaceholders(text: string): string[] {
  return [...text.matchAll(PLACEHOLDER)].map((m) => (m[1] ?? '').trim());
}

const INLINE = /\[\[([\s\S]+?)\]\]|\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)\s]+)\)|\*([^*]+)\*/g;

export function renderLegalInline(text: string, keyPrefix = 'i'): ReactNode[] {
  const out: ReactNode[] = [];
  let last = 0;
  let n = 0;
  for (const m of text.matchAll(INLINE)) {
    const at = m.index ?? 0;
    if (at > last) out.push(text.slice(last, at));
    const key = `${keyPrefix}-${n++}`;
    if (m[1] != null) {
      out.push(
        <mark
          key={key}
          data-placeholder=""
          className="rounded bg-amber-200 px-1 font-medium text-amber-950 ring-1 ring-amber-500"
        >
          [{m[1].trim()}]
        </mark>,
      );
    } else if (m[2] != null) {
      out.push(<strong key={key}>{renderLegalInline(m[2], key)}</strong>);
    } else if (m[3] != null && m[4] != null) {
      const href = m[4];
      out.push(
        href.startsWith('/') ? (
          <Link key={key} href={href} className="underline underline-offset-2 hover:text-primary">
            {m[3]}
          </Link>
        ) : (
          <a key={key} href={href} className="underline underline-offset-2 hover:text-primary">
            {m[3]}
          </a>
        ),
      );
    } else if (m[5] != null) {
      out.push(<em key={key}>{renderLegalInline(m[5], key)}</em>);
    }
    last = at + m[0].length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

export function LegalBody({ body }: { body: string }) {
  return (
    <>
      {parseLegalBlocks(body).map((b, i) => {
        if (b.kind === 'heading') {
          return (
            <h2 key={i} className="mt-8 text-lg font-semibold">
              {renderLegalInline(b.text, `h${i}`)}
            </h2>
          );
        }
        if (b.kind === 'list') {
          return (
            <ul key={i} className="my-3 list-disc space-y-1.5 ps-6">
              {b.items.map((item, j) => (
                <li key={j}>{renderLegalInline(item, `l${i}-${j}`)}</li>
              ))}
            </ul>
          );
        }
        return (
          <p key={i} className="my-3 leading-relaxed">
            {renderLegalInline(b.text, `p${i}`)}
          </p>
        );
      })}
    </>
  );
}
