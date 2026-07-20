import { describe, expect, it } from 'vitest';
import {
  normalizeNotifPayload,
  payloadFriendshipId,
  payloadLinkId,
} from './social-notif-payload';

describe('normalizeNotifPayload', () => {
  it('returns empty object for nullish', () => {
    expect(normalizeNotifPayload(null)).toEqual({});
    expect(normalizeNotifPayload(undefined)).toEqual({});
  });

  it('parses JSON strings and double-encoded strings', () => {
    expect(normalizeNotifPayload('{"link_id":"abc"}')).toEqual({ link_id: 'abc' });
    expect(normalizeNotifPayload(JSON.stringify(JSON.stringify({ link_id: 'x' })))).toEqual({
      link_id: 'x',
    });
  });

  it('passes through plain objects', () => {
    expect(normalizeNotifPayload({ teacher_id: 't1' })).toEqual({ teacher_id: 't1' });
  });
});

describe('payloadLinkId / payloadFriendshipId', () => {
  it('reads snake and camel keys', () => {
    expect(payloadLinkId({ link_id: ' L1 ' })).toBe('L1');
    expect(payloadLinkId({ linkId: 'L2' })).toBe('L2');
    expect(payloadLinkId({ link_id: 42 })).toBe('42');
    expect(payloadLinkId({})).toBeNull();
    expect(payloadFriendshipId({ friendship_id: ' F1 ' })).toBe('F1');
    expect(payloadFriendshipId({ friendshipId: 'F2' })).toBe('F2');
  });
});
