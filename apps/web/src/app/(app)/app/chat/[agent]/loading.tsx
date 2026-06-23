import { Skeleton } from '@asf/ui/skeleton';

export default function ChatLoading() {
  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col gap-4">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="flex-1 w-full rounded-xl" />
    </div>
  );
}
