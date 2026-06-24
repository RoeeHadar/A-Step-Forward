import { notFound } from 'next/navigation';
import { CategoryPageContent } from '@/components/category-page-content';
import { CURRICULUM_CATEGORIES } from '@/lib/curriculum-categories';

interface Props {
  params: Promise<{ category: string }>;
}

export default async function CategoryPage({ params }: Props) {
  const { category: categoryId } = await params;
  const category = CURRICULUM_CATEGORIES.find((c) => c.id === categoryId);
  if (!category) notFound();

  return <CategoryPageContent category={category} />;
}
