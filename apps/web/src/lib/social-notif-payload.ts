/**
 * Pure helpers for notification payloads (safe for client + unit tests).
 */

/** Neon sometimes returns jsonb as a string; normalize to a plain object. */
export function normalizeNotifPayload(raw: unknown): Record<string, unknown> {
  if (raw == null) return {};
  if (typeof raw === 'string') {
    try {
      const parsed: unknown = JSON.parse(raw);
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        return parsed as Record<string, unknown>;
      }
      // Double-encoded JSON string
      if (typeof parsed === 'string') {
        const again: unknown = JSON.parse(parsed);
        if (again && typeof again === 'object' && !Array.isArray(again)) {
          return again as Record<string, unknown>;
        }
      }
    } catch {
      return {};
    }
    return {};
  }
  if (typeof raw === 'object' && !Array.isArray(raw)) {
    return raw as Record<string, unknown>;
  }
  return {};
}

export function payloadLinkId(payload: Record<string, unknown>): string | null {
  const v = payload.link_id ?? payload.linkId;
  if (typeof v === 'string' && v.trim()) return v.trim();
  if (typeof v === 'number' && Number.isFinite(v)) return String(v);
  return null;
}

export function payloadFriendshipId(payload: Record<string, unknown>): string | null {
  const v = payload.friendship_id ?? payload.friendshipId;
  if (typeof v === 'string' && v.trim()) return v.trim();
  return null;
}
