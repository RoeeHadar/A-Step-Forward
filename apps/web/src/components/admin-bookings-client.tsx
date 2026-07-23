'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { Input } from '@asf/ui/input';
import { Label } from '@asf/ui/label';
import { Textarea } from '@asf/ui/textarea';

type AdminBooking = {
  token: string;
  status: string;
  learnerName: string;
  requesterName: string;
  requesterEmail: string;
  requesterPhone: string;
  modality: string;
  durationH: number;
  priceIls: number;
  preferredStart: string;
  preferredEnd: string;
  goalText: string;
  createdAt: string;
};

type SettingsPayload = {
  oauthConfigured: boolean;
  secretsKeyConfigured: boolean;
  resendConfigured?: boolean;
  notifyEmail?: string;
  fromAddress?: string;
  usesTestFrom?: boolean;
  emailEnv?: {
    RESEND_API_KEY: boolean;
    RESEND_FROM: boolean;
    BOOKING_NOTIFY_EMAIL: boolean;
    TUTOR_EMAIL: boolean;
    notifyEmail: string;
    fromAddress: string;
    usesTestFrom: boolean;
  };
  connectUrl: string;
  settings: {
    calendarId: string;
    hasRefreshToken: boolean;
    googleChannelId: string | null;
    googleChannelExpiration: string | null;
    meetingLink: string | null;
    hasPhone: boolean;
    hasAddress: boolean;
    busyCacheUpdatedAt: string | null;
  } | null;
  busyPreview: { count: number; syncedAt: string | null; source: string } | null;
  bookings?: AdminBooking[];
};

export function AdminBookingsClient({ gcalQuery }: { gcalQuery: string | null }) {
  const [data, setData] = useState<SettingsPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [meetingLink, setMeetingLink] = useState('');
  const [calendarId, setCalendarId] = useState('primary');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function load() {
    setError(null);
    const res = await fetch('/api/admin/bookings/settings');
    if (!res.ok) {
      setError('Failed to load settings');
      return;
    }
    const json = (await res.json()) as SettingsPayload;
    setData(json);
    setCalendarId(json.settings?.calendarId ?? 'primary');
    setMeetingLink(json.settings?.meetingLink ?? '');
  }

  useEffect(() => {
    void load();
  }, []);

  useEffect(() => {
    if (!gcalQuery) return;
    const params = new URLSearchParams(
      gcalQuery.includes('=') ? gcalQuery : `gcal=${gcalQuery}`,
    );
    const gcal = params.get('gcal') ?? '';
    const watchErr = params.get('watch');
    const map: Record<string, string> = {
      connected: 'Google Calendar connected.',
      denied: 'Google consent was denied.',
      exchange_failed: 'OAuth token exchange failed.',
      save_failed: 'Could not save refresh token (check BOOKING_SECRETS_KEY).',
      state_mismatch: 'OAuth state mismatch — try again.',
      not_configured: 'Google OAuth env vars are missing.',
      unauthorized: 'Sign in as admin first.',
      forbidden: 'Admin role required.',
    };
    setMessage(
      `${map[gcal] ?? (gcal ? `Google Calendar: ${gcal}` : '')}${
        watchErr ? ` (watch: ${watchErr} — renew later from this page)` : ''
      }`.trim() || null,
    );
  }, [gcalQuery]);

  async function saveContacts(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const res = await fetch('/api/admin/bookings/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: phone || undefined,
          address: address || undefined,
          meetingLink,
          calendarId,
        }),
      });
      const json = (await res.json()) as { error?: string };
      if (!res.ok) {
        setMessage(json.error ?? 'Save failed');
        return;
      }
      setMessage('Saved.');
      setPhone('');
      setAddress('');
      await load();
    } finally {
      setSaving(false);
    }
  }

  async function action(actionName: 'renew_watch' | 'refresh_busy' | 'test_email') {
    setSaving(true);
    setMessage(null);
    try {
      const res = await fetch('/api/admin/bookings/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionName }),
      });
      const json = (await res.json()) as {
        error?: string;
        detail?: string | null;
        busyCount?: number;
        notifyEmail?: string;
        fromAddress?: string;
        usesTestFrom?: boolean;
        id?: string | null;
      };
      if (!res.ok) {
        setMessage(
          [
            json.error ?? 'Action failed',
            json.detail ? `— ${json.detail}` : '',
            json.fromAddress ? `(from ${json.fromAddress}` : '',
            json.notifyEmail ? ` → ${json.notifyEmail})` : json.fromAddress ? ')' : '',
          ]
            .filter(Boolean)
            .join(' '),
        );
        return;
      }
      if (actionName === 'refresh_busy') {
        setMessage(`Busy refreshed (${json.busyCount ?? 0} blocks).`);
      } else if (actionName === 'test_email') {
        setMessage(
          `Test email sent to ${json.notifyEmail ?? 'notify address'} (Resend id: ${json.id ?? 'ok'}). Check inbox + spam.`,
        );
      } else {
        setMessage('Watch channel renewed.');
      }
      await load();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-8">
      {message ? (
        <p className="rounded-lg border border-border bg-surface-2 px-4 py-3 text-sm" role="status">
          {message}
        </p>
      ) : null}
      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}

      <section className="space-y-3 rounded-2xl border border-border bg-surface-1 p-6">
        <h2 className="font-display text-lg font-semibold">Incoming requests</h2>

        <div
          className={
            data?.resendConfigured
              ? 'rounded-lg border border-border bg-surface-2 px-3 py-3 text-sm'
              : 'rounded-lg border border-destructive/40 bg-destructive/10 px-3 py-3 text-sm'
          }
        >
          <p className="font-medium text-foreground">
            {data?.resendConfigured
              ? 'Resend key present on this deployment'
              : 'RESEND_API_KEY is NOT visible to production'}
          </p>
          <ul className="mt-2 space-y-1 font-mono text-xs text-muted-foreground">
            <li>RESEND_API_KEY: {data?.emailEnv?.RESEND_API_KEY ? 'yes' : 'NO'}</li>
            <li>RESEND_FROM: {data?.emailEnv?.RESEND_FROM ? 'yes' : 'no (using onboarding@resend.dev)'}</li>
            <li>
              BOOKING_NOTIFY_EMAIL:{' '}
              {data?.emailEnv?.BOOKING_NOTIFY_EMAIL ? 'yes' : 'no (default roeehadar@gmail.com)'}
            </li>
            <li>Notify → {data?.notifyEmail ?? '—'}</li>
            <li>From → {data?.fromAddress ?? '—'}</li>
          </ul>
          {!data?.resendConfigured ? (
            <ol className="mt-3 list-decimal space-y-1 ps-5 text-sm text-foreground">
              <li>
                Open Vercel → project <strong>a-step-forward-waij</strong> (the live web app)
              </li>
              <li>Settings → Environment Variables</li>
              <li>
                Add <code>RESEND_API_KEY</code> exactly (no quotes), Environment ={' '}
                <strong>Production</strong> (and Preview if you want)
              </li>
              <li>
                Optional: <code>BOOKING_NOTIFY_EMAIL</code>=roeehadar@gmail.com,{' '}
                <code>RESEND_FROM</code> after you verify a domain
              </li>
              <li>
                Deployments → … on latest Production → <strong>Redeploy</strong> (env vars apply only
                after redeploy)
              </li>
              <li>Hard-refresh this page — RESEND_API_KEY must show yes</li>
            </ol>
          ) : null}
        </div>

        {data?.usesTestFrom && data?.resendConfigured ? (
          <p className="rounded-lg border border-accent-magenta/40 bg-accent-magenta/10 px-3 py-2 text-sm">
            You are using Resend&apos;s <strong>test</strong> sender (<code>onboarding@resend.dev</code>).
            It can only deliver to the email address on your Resend account — not arbitrary Gmail
            addresses. Fix: verify a domain in Resend → Domains, then set{' '}
            <code>RESEND_FROM</code> to e.g. <code>A Step Forward &lt;bookings@yourdomain.com&gt;</code>{' '}
            and redeploy. Or set <code>BOOKING_NOTIFY_EMAIL</code> to the exact email you used to sign
            up for Resend (for testing only).
          </p>
        ) : null}
        <Button
          type="button"
          variant="secondary"
          disabled={saving || !data?.resendConfigured}
          onClick={() => void action('test_email')}
        >
          Send test email now
        </Button>
        {!data?.bookings?.length ? (
          <p className="text-sm text-muted-foreground">No booking requests yet.</p>
        ) : (
          <ul className="space-y-3">
            {data.bookings.map((b) => (
              <li
                key={b.token}
                className="rounded-xl border border-border bg-surface-2 px-4 py-3 text-sm"
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <span className="font-medium">
                    {b.learnerName} · {b.status}
                  </span>
                  <span className="text-muted-foreground">
                    {new Date(b.createdAt).toLocaleString('he-IL', { timeZone: 'Asia/Jerusalem' })}
                  </span>
                </div>
                <p className="mt-1 text-muted-foreground">
                  {b.requesterName} &lt;{b.requesterEmail}&gt; · {b.requesterPhone}
                </p>
                <p className="mt-1">
                  {b.modality === 'haifa' ? 'Haifa' : 'Online'} · {b.durationH}h · ₪{b.priceIls}
                </p>
                <p className="mt-1 text-muted-foreground">
                  Preferred:{' '}
                  {new Date(b.preferredStart).toLocaleString('he-IL', {
                    timeZone: 'Asia/Jerusalem',
                  })}
                </p>
                {b.goalText ? <p className="mt-1">Goal: {b.goalText}</p> : null}
                <Link
                  href={`/book/r/${b.token}`}
                  className="mt-2 inline-flex text-primary underline-offset-4 hover:underline"
                >
                  Open status page
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="space-y-3 rounded-2xl border border-border bg-surface-1 p-6">
        <h2 className="font-display text-lg font-semibold">Google Calendar</h2>
        <ul className="space-y-1 text-sm text-muted-foreground">
          <li>OAuth client: {data?.oauthConfigured ? 'configured' : 'missing env'}</li>
          <li>Secrets key: {data?.secretsKeyConfigured ? 'configured' : 'missing BOOKING_SECRETS_KEY'}</li>
          <li>Refresh token: {data?.settings?.hasRefreshToken ? 'yes' : 'not connected'}</li>
          <li>Calendar id: {data?.settings?.calendarId ?? '—'}</li>
          <li>
            Watch:{' '}
            {data?.settings?.googleChannelId
              ? `active until ${data.settings.googleChannelExpiration ?? '?'}`
              : 'not registered'}
          </li>
          <li>
            Busy cache:{' '}
            {data?.busyPreview
              ? `${data.busyPreview.count} blocks (${data.busyPreview.source}) · ${data.busyPreview.syncedAt ?? 'n/a'}`
              : '—'}
          </li>
        </ul>
        <div className="flex flex-wrap gap-2 pt-2">
          <Button asChild disabled={!data?.oauthConfigured}>
            <Link href={data?.connectUrl ?? '#'}>Connect / reconnect Google</Link>
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={saving || !data?.settings?.hasRefreshToken}
            onClick={() => void action('refresh_busy')}
          >
            Refresh busy now
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={saving || !data?.settings?.hasRefreshToken}
            onClick={() => void action('renew_watch')}
          >
            Renew push watch
          </Button>
        </div>
        <p className="text-xs text-muted-foreground">
          Sync the same Google account on your iPhone so events appear in Apple Calendar.
          Push webhooks invalidate busy cache immediately; we also refresh at most every ~45s.
        </p>
      </section>

      <form
        onSubmit={saveContacts}
        className="space-y-4 rounded-2xl border border-border bg-surface-1 p-6"
      >
        <h2 className="font-display text-lg font-semibold">Contact details (private)</h2>
        <p className="text-sm text-muted-foreground">
          Sent to learners only after you accept an in-person (Haifa) or online booking. Never shown
          on the public /book page.
        </p>
        <div className="space-y-1.5">
          <Label htmlFor="cal-id">Google calendar id</Label>
          <Input
            id="cal-id"
            value={calendarId}
            onChange={(e) => setCalendarId(e.target.value)}
            placeholder="primary"
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="meet">Default meeting link (online)</Label>
          <Input
            id="meet"
            value={meetingLink}
            onChange={(e) => setMeetingLink(e.target.value)}
            placeholder="https://meet.google.com/..."
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="phone">
            Phone {data?.settings?.hasPhone ? '(set — leave blank to keep)' : ''}
          </Label>
          <Input
            id="phone"
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            autoComplete="off"
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="address">
            Full Haifa address {data?.settings?.hasAddress ? '(set — leave blank to keep)' : ''}
          </Label>
          <Textarea
            id="address"
            rows={2}
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            autoComplete="off"
          />
        </div>
        <Button type="submit" disabled={saving}>
          {saving ? 'Saving…' : 'Save'}
        </Button>
      </form>
    </div>
  );
}
