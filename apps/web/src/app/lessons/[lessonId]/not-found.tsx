import { redirect } from 'next/navigation';

export default function LegacyLessonNotFound() {
  redirect('/learn');
}
