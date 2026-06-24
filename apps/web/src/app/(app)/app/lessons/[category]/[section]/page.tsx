import Link from 'next/link';
import { notFound } from 'next/navigation';
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

  return (
    <div className="container mx-auto py-8 px-4">
      <Link
        href={`/app/lessons/${category.id}`}
        className="text-sm text-muted-foreground hover:text-primary mb-4 inline-block"
      >
        ← חזרה ל{category.heLabel}
      </Link>
      <h1 className="text-3xl font-bold mb-2">{section.heLabel}</h1>
      <p className="text-muted-foreground mb-8">{section.enLabel}</p>
      <div className="rounded-xl border border-dashed border-muted-foreground/30 p-12 text-center">
        <p className="text-2xl mb-2">🚧</p>
        <p className="text-lg font-semibold">בקרוב — שיעורים בדרך!</p>
        <p className="text-muted-foreground text-sm mt-1">Coming soon — lessons are on the way!</p>
      </div>
    </div>
  );
}
