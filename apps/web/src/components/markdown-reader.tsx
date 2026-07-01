'use client';

import { MarkdownMath } from '@/components/markdown-math';

export function MarkdownReader({ content }: { content: string }) {
  return <MarkdownMath>{content}</MarkdownMath>;
}
