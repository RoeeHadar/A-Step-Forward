import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Card, CardHeader, CardTitle } from '@asf/ui/card';
import { CURRICULUM_CATEGORIES } from '@/lib/curriculum-categories';

interface Props {
  params: Promise<{ category: string }>;
}

export default async function CategoryPage({ params }: Props) {
  const { category: categoryId } = await params;
  const category = CURRICULUM_CATEGORIES.find((c) => c.id === categoryId);
  if (!category) notFound();

  return (
    <div className="container mx-auto py-8 px-4">
      <Link
        href="/app/lessons"
        className="text-sm text-muted-foreground hover:text-primary mb-4 inline-block"
      >
        ← חזרה לקטגוריות
      </Link>
      <div className="flex items-center gap-3 mb-2">
        <span className="text-4xl">{category.emoji}</span>
        <h1 className="text-3xl font-bold">{category.heLabel}</h1>
      </div>
      <p className="text-muted-foreground mb-8">{category.enLabel}</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {category.sections.map((section) => (
          <Link key={section.id} href={`/app/lessons/${category.id}/${section.id}`}>
            <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="text-base">{section.heLabel}</CardTitle>
                <p className="text-xs text-muted-foreground">{section.enLabel}</p>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
