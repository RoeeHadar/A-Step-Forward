import { redirect } from 'next/navigation';

// Legacy route — unified catalog lives at /learn.
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export default async function SectionPage() {
  redirect('/learn');
}
