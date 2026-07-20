/**
 * Bookings API retired with the Book-a-Lesson UI.
 * Returns 410 so stale clients fail clearly.
 */
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST() {
  return Response.json(
    { error: 'gone', message: 'Book a Lesson is temporarily unavailable.' },
    { status: 410 },
  );
}

export async function GET() {
  return Response.json(
    { error: 'gone', message: 'Book a Lesson is temporarily unavailable.' },
    { status: 410 },
  );
}
