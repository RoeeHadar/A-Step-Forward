import { redirect } from 'next/navigation';

/**
 * Book-a-Lesson is retired for now (will return later).
 * Keep the route so old links don't 404 — send visitors home.
 */
export default function BookPageRetired() {
  redirect('/');
}
