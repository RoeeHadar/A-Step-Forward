import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export type ClassValue = string | number | boolean | null | undefined;

export function cn(...values: ClassValue[]): string {
  return twMerge(clsx(values));
}
