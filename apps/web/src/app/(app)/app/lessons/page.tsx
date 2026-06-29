/**
 * /app/lessons — legacy route; unified catalog lives at /learn.
 */
import { redirect } from 'next/navigation';

export default function LessonsIndexPage() {
  redirect('/learn');
}
