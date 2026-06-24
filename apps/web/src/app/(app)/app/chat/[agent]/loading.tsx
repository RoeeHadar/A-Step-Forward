import { Skeleton } from '@asf/ui/skeleton';

export default function ChatLoading() {
  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <header className="mb-4 flex items-center gap-3">
        <Skeleton className="h-3 w-3 rounded-full" aria-hidden />
        <Skeleton className="h-8 w-48" />
      </header>

      <div className="flex flex-1 flex-col overflow-hidden rounded-xl border border-border">
        <div className="flex-1 space-y-4 p-4">
          <Skeleton className="mx-auto h-4 w-2/3 max-w-sm" />
          <Skeleton className="ml-auto h-16 w-[60%] max-w-xs rounded-lg" />
          <Skeleton className="mr-auto h-24 w-[70%] max-w-md rounded-lg" />
        </div>
        <div className="flex gap-2 border-t border-border p-4">
          <Skeleton className="h-[44px] flex-1 rounded-md" />
          <Skeleton className="h-10 w-10 shrink-0 rounded-md" />
        </div>
      </div>
    </div>
  );
}
