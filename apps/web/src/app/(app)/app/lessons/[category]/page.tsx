import { redirect } from 'next/navigation';

// Legacy route — unified catalog lives at /learn.
export default async function CategoryPage() {
  redirect('/learn');
}
