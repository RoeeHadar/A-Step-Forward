import { BookStatusClient } from '@/components/book-status-client';

export const dynamic = 'force-dynamic';

type Props = { params: Promise<{ token: string }> };

export default async function BookStatusPage({ params }: Props) {
  const { token } = await params;
  return <BookStatusClient token={token} />;
}
