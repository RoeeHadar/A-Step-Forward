import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { BOOK_PRIVACY_NOTICE, LEGAL_DOCS } from './legal-content';
import { LegalBody, legalPlaceholders, parseLegalBlocks, renderLegalInline } from './legal-markup';

const html = (body: string) => renderToStaticMarkup(createElement(LegalBody, { body }));

describe('legal markup', () => {
  it('parses headings, paragraphs and bullet lists', () => {
    const blocks = parseLegalBlocks('**What is in place**\n- one\n- two\nAfter the list.\n\nNext *para*.');
    expect(blocks).toEqual([
      { kind: 'heading', text: 'What is in place' },
      { kind: 'list', items: ['one', 'two'] },
      { kind: 'paragraph', text: 'After the list.' },
      { kind: 'paragraph', text: 'Next *para*.' },
    ]);
  });

  it('renders blanks as visible highlighted placeholders', () => {
    const out = html('Write to [[email]] today.');
    expect(out).toContain('<mark data-placeholder=""');
    expect(out).toContain('>[email]</mark>');
    expect(out).not.toContain('[[');
  });

  it('renders bold, italic and internal links', () => {
    const out = html('**1. Who.** See the *policy* and [privacy policy](/privacy).');
    expect(out).toContain('<strong>1. Who.</strong>');
    expect(out).toContain('<em>policy</em>');
    expect(out).toMatch(/<a [^>]*href="\/privacy"[^>]*>privacy policy<\/a>/);
  });

  it('keeps blanks inside bold text', () => {
    expect(renderLegalInline('**[[x]]**')).toHaveLength(1);
    expect(html('**a [[x]] b**')).toContain('data-placeholder');
  });
});

describe('legal content (M5)', () => {
  const all = Object.entries(LEGAL_DOCS).flatMap(([id, byLocale]) =>
    Object.entries(byLocale).map(([locale, doc]) => ({ id, locale, doc })),
  );

  it('has all three pages in Hebrew and English', () => {
    expect(all.map((d) => `${d.id}:${d.locale}`).sort()).toEqual(
      ['accessibility:en', 'accessibility:he', 'privacy:en', 'privacy:he', 'terms:en', 'terms:he'],
    );
  });

  it.each(all)('$id/$locale carries no internal draft notes', ({ doc }) => {
    const text = `${doc.title}\n${doc.body}`;
    expect(text).not.toMatch(/⚠|Open points|Facts this draft|Evidence behind|internal, don't publish|ASF-/);
    expect(doc.body.trim().length).toBeGreaterThan(500);
  });

  it.each(all)('$id/$locale renders every blank as a placeholder', ({ doc }) => {
    const blanks = legalPlaceholders(doc.body);
    expect(blanks.length).toBeGreaterThan(0);
    const out = html(doc.body);
    expect(out.match(/data-placeholder/g)?.length).toBe(blanks.length);
    expect(out).not.toContain('[[');
    expect(out).not.toContain('**');
  });

  it('book notice links to /privacy in both languages', () => {
    for (const text of Object.values(BOOK_PRIVACY_NOTICE)) {
      expect(text).toMatch(/\]\(\/privacy\)/);
      expect(renderToStaticMarkup(createElement('p', null, renderLegalInline(text)))).toContain(
        'href="/privacy"',
      );
    }
  });
});
