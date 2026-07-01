'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { cn } from '@/lib/utils';
import { normalizeLatexInMarkdown } from '@/lib/normalize-latex';

type MarkdownMathProps = {
  children: string;
  className?: string;
  dir?: 'ltr' | 'rtl';
};

/** Markdown + GFM + LaTeX (KaTeX), with seed-data escape normalization. */
export function MarkdownMath({ children, className, dir }: MarkdownMathProps) {
  const content = normalizeLatexInMarkdown(children);
  return (
    <div
      className={cn(
        'prose prose-sm dark:prose-invert max-w-none prose-headings:font-display prose-pre:bg-muted/40',
        className,
      )}
      dir={dir}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
