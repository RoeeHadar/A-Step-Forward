import 'server-only';

import { cookies } from 'next/headers';
import { LOCALE_COOKIE, resolveLocale } from './locale-storage';

export async function getServerLocale() {
  const cookieStore = await cookies();
  return resolveLocale(cookieStore.get(LOCALE_COOKIE)?.value);
}
