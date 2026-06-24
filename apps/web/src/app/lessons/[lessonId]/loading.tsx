import { Card, CardContent } from '@asf/ui/card';
import { SiteHeader } from '@/components/site-header';

export default function LessonLoading() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-8">
        <div className="mb-6 h-4 w-24 animate-pulse rounded bg-muted" />
        <div className="mb-3 h-9 w-2/3 animate-pulse rounded bg-muted" />
        <div className="mb-6 flex gap-3">
          <div className="h-6 w-20 animate-pulse rounded bg-muted" />
          <div className="h-6 w-16 animate-pulse rounded bg-muted" />
        </div>
        <Card className="mb-8">
          <CardContent className="space-y-3 pt-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-4 animate-pulse rounded bg-muted" style={{ width: `${85 - i * 4}%` }} />
            ))}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
