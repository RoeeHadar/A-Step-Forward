import { notFound } from 'next/navigation';
import { SectionPageContent } from '@/components/section-page-content';
import { CURRICULUM_CATEGORIES } from '@/lib/curriculum-categories';

interface Props {
  params: Promise<{ category: string; section: string }>;
}

export default async function SectionPage({ params }: Props) {
  const { category: categoryId, section: sectionId } = await params;
  const category = CURRICULUM_CATEGORIES.find((c) => c.id === categoryId);
  if (!category) notFound();
  const section = category.sections.find((s) => s.id === sectionId);
  if (!section) notFound();

  return <SectionPageContent category={category} section={section} />;
}
