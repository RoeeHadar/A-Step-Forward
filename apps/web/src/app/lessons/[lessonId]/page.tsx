import { redirect } from 'next/navigation';

export default function LegacyLessonRedirect() {
  redirect('/learn');
}
