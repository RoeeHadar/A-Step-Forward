'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { CURRICULUM_CATEGORIES } from '@/lib/curriculum-categories';

export default function LessonsPage() {
  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-2">שיעורים</h1>
      <p className="text-muted-foreground mb-8">בחר קטגוריה להתחלה</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {CURRICULUM_CATEGORIES.map((cat) => (
          <Link key={cat.id} href={`/app/lessons/${cat.id}`}>
            <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader className="pb-2">
                <div className="text-3xl mb-2">{cat.emoji}</div>
                <CardTitle className="text-base leading-tight">{cat.heLabel}</CardTitle>
                <p className="text-xs text-muted-foreground">{cat.enLabel}</p>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{cat.sections.length} נושאים</p>
                <span className="text-xs text-primary font-medium mt-1 inline-block">עיין ›</span>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
