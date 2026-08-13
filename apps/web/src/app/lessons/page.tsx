import { redirect } from 'next/navigation';

/** Legacy English OpenStax catalog — unified content lives at /learn. */
export default function LessonsIndexRedirect() {
  redirect('/learn');
}
