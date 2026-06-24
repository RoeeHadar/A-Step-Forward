import { Skeleton } from '@asf/ui/skeleton';

export default function LessonLoading() {
  return (
    <div className="max-w-3xl space-y-6">
      <Skeleton className="h-9 w-2/3" />
      <div className="flex gap-3">
        <Skeleton className="h-5 w-20" />
        <Skeleton className="h-5 w-16" />
      </div>
      <Skeleton className="h-64 w-full" />
      <Skeleton className="h-32 w-full" />
    </div>
  );
}
