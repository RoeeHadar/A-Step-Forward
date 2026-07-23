/**
 * Encrypt/decrypt booking secrets (Google refresh token, phone, address).
 * AES-256-GCM; key from BOOKING_SECRETS_KEY (or CRON_SECRET fallback).
 */
import 'server-only';
import { createCipheriv, createDecipheriv, randomBytes, scryptSync } from 'node:crypto';

const PREFIX = 'v1:';

function getKey(): Buffer | null {
  const secret = process.env.BOOKING_SECRETS_KEY || process.env.CRON_SECRET || '';
  if (!secret || secret.length < 8) return null;
  return scryptSync(secret, 'asf-lesson-booking-v1', 32);
}

export function bookingSecretsConfigured(): boolean {
  return getKey() != null;
}

/** Returns ciphertext as `v1:<iv_b64>:<tag_b64>:<data_b64>` or null if no key. */
export function sealBookingSecret(plaintext: string): string | null {
  const key = getKey();
  if (!key) return null;
  const iv = randomBytes(12);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  const enc = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
  const tag = cipher.getAuthTag();
  return `${PREFIX}${iv.toString('base64url')}:${tag.toString('base64url')}:${enc.toString('base64url')}`;
}

export function openBookingSecret(sealed: string): string | null {
  const key = getKey();
  if (!key || !sealed.startsWith(PREFIX)) return null;
  try {
    const rest = sealed.slice(PREFIX.length);
    const [ivB64, tagB64, dataB64] = rest.split(':');
    if (!ivB64 || !tagB64 || !dataB64) return null;
    const iv = Buffer.from(ivB64, 'base64url');
    const tag = Buffer.from(tagB64, 'base64url');
    const data = Buffer.from(dataB64, 'base64url');
    const decipher = createDecipheriv('aes-256-gcm', key, iv);
    decipher.setAuthTag(tag);
    return Buffer.concat([decipher.update(data), decipher.final()]).toString('utf8');
  } catch {
    return null;
  }
}
