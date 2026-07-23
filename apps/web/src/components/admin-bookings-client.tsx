'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { Input } from '@asf/ui/input';
import { Label } from '@asf/ui/label';
import { Textarea } from '@asf/ui/textarea';
import { cn } from '@asf/ui';
import { PageHeader } from '@/components/page-header';
import { useI18n } from '@/providers/i18n-provider';

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

type TabId = 'requests' | 'calendar' | 'contacts';

const REDIRECT_URI = 'https://a-step-forward-waij.vercel.app/api/book/gcal/oauth/callback';

export function AdminBookingsClient({ gcalQuery }: { gcalQuery: string | null }) {
  const { messages, locale } = useI18n();
  const t = messages.admin;
  const dateLocale = locale === 'he' ? 'he-IL' : 'en-GB';

  const [tab, setTab] = useState<TabId>('requests');
  const [data, setData] = useState<SettingsPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [meetingLink, setMeetingLink] = useState('');
  const [calendarId, setCalendarId] = useState('primary');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [showTestingHelp, setShowTestingHelp] = useState(false);

  const statusLabel = useMemo(() => {
    const map: Record<string, string> = {
      submitted: t.statusSubmitted,
      proposal_sent: t.statusProposalSent,
      pick_pending: t.statusPickPending,
      confirmed: t.statusConfirmed,
      rejected: t.statusRejected,
      cancelled: t.statusCancelled,
      expired: t.statusExpired,
    };
    return (status: string) => map[status] ?? status;
  }, [t]);

  async function load() {
    setError(null);
    const res = await fetch('/api/admin/bookings/settings');
    if (!res.ok) {
      setError(t.loadFailed);
      return;
    }
    const json = (await res.json()) as SettingsPayload;
    setData(json);
    setCalendarId(json.settings?.calendarId ?? 'primary');
    setMeetingLink(json.settings?.meetingLink ?? '');
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- load once on mount
  }, []);

  useEffect(() => {
    if (!gcalQuery) return;
    const params = new URLSearchParams(
      gcalQuery.includes('=') ? gcalQuery : `gcal=${gcalQuery}`,
    );
    const gcal = params.get('gcal') ?? '';
    const watchErr = params.get('watch');
    const map: Record<string, string> = {
      connected: t.msgConnected,
      denied: t.msgDenied,
      exchange_failed: t.msgExchangeFailed,
      save_failed: t.msgSaveFailed,
      state_mismatch: t.msgStateMismatch,
      not_configured: t.msgNotConfigured,
      unauthorized: t.msgUnauthorized,
      forbidden: t.msgForbidden,
    };
    if (gcal === 'denied') {
      setShowTestingHelp(true);
      setTab('calendar');
    }
    if (gcal === 'connected') {
      setShowTestingHelp(false);
      setTab('calendar');
    }
    setMessage(
      `${map[gcal] ?? (gcal ? `Google Calendar: ${gcal}` : '')}${
        watchErr ? ` (watch: ${watchErr})` : ''
      }`.trim() || null,
    );
  }, [gcalQuery, t]);

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
        setMessage(json.error ?? t.saveFailed);
        return;
      }
      setMessage(t.saved);
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
        id?: string | null;
      };
      if (!res.ok) {
        setMessage(
          [json.error ?? t.msgActionFailed, json.detail ? `— ${json.detail}` : '']
            .filter(Boolean)
            .join(' '),
        );
        return;
      }
      if (actionName === 'refresh_busy') {
        setMessage(t.msgBusyRefreshed.replace('{count}', String(json.busyCount ?? 0)));
      } else if (actionName === 'test_email') {
        setMessage(t.msgTestEmail.replace('{email}', json.notifyEmail ?? '—'));
      } else {
        setMessage(t.msgWatchRenewed);
      }
      await load();
    } finally {
      setSaving(false);
    }
  }

  const connected = Boolean(data?.settings?.hasRefreshToken);
  const pendingCount =
    data?.bookings?.filter((b) =>
      ['submitted', 'proposal_sent', 'pick_pending'].includes(b.status),
    ).length ?? 0;

  const tabs: { id: TabId; label: string; badge?: number }[] = [
    { id: 'requests', label: t.tabRequests, badge: pendingCount || undefined },
    { id: 'calendar', label: t.tabCalendar },
    { id: 'contacts', label: t.tabContacts },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title={t.bookingsTitle} description={t.bookingsSubtitle} backHref="/admin" />

      {message ? (
        <p
          className={cn(
            'rounded-xl border px-4 py-3 text-sm',
            showTestingHelp
              ? 'border-accent-amber/40 bg-accent-amber/10'
              : 'border-border bg-surface-2',
          )}
          role="status"
        >
          {message}
        </p>
      ) : null}
      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}

      <div
        className="flex flex-wrap gap-1 rounded-xl border border-border bg-surface-1 p-1"
        role="tablist"
        aria-label={t.bookingsTitle}
      >
        {tabs.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={tab === item.id}
            className={cn(
              'inline-flex flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors sm:flex-none',
              tab === item.id
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-surface-2 hover:text-foreground',
            )}
            onClick={() => setTab(item.id)}
          >
            {item.label}
            {item.badge ? (
              <span
                className={cn(
                  'rounded-md px-1.5 py-0.5 text-[11px] tabular-nums',
                  tab === item.id ? 'bg-primary-foreground/20' : 'bg-surface-2',
                )}
              >
                {item.badge}
              </span>
            ) : null}
          </button>
        ))}
      </div>

      {tab === 'requests' ? (
        <section className="space-y-4 rounded-2xl border border-border bg-surface-1 p-6">
          <h2 className="font-display text-lg font-semibold">{t.incomingTitle}</h2>

          <div
            className={cn(
              'rounded-xl border px-4 py-3 text-sm',
              data?.resendConfigured
                ? 'border-border bg-surface-2'
                : 'border-destructive/40 bg-destructive/10',
            )}
          >
            <p className="font-medium text-foreground">
              {data?.resendConfigured ? t.resendOk : t.resendMissing}
            </p>
            <ul className="mt-2 space-y-1 font-mono text-xs text-muted-foreground">
              <li>RESEND_API_KEY: {data?.emailEnv?.RESEND_API_KEY ? 'yes' : 'NO'}</li>
              <li>Notify → {data?.notifyEmail ?? '—'}</li>
              <li>From → {data?.fromAddress ?? '—'}</li>
            </ul>
            <Button
              type="button"
              variant="secondary"
              className="mt-3"
              disabled={saving || !data?.resendConfigured}
              onClick={() => void action('test_email')}
            >
              {t.sendTestEmail}
            </Button>
          </div>

          {!data?.bookings?.length ? (
            <p className="text-sm text-muted-foreground">{t.incomingEmpty}</p>
          ) : (
            <ul className="space-y-3">
              {data.bookings.map((b) => (
                <li
                  key={b.token}
                  className="rounded-xl border border-border bg-surface-2 px-4 py-3 text-sm"
                >
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <span className="font-medium">
                      {b.learnerName}{' '}
                      <span className="text-muted-foreground">· {statusLabel(b.status)}</span>
                    </span>
                    <span className="text-muted-foreground">
                      {new Date(b.createdAt).toLocaleString(dateLocale, {
                        timeZone: 'Asia/Jerusalem',
                      })}
                    </span>
                  </div>
                  <p className="mt-1 text-muted-foreground">
                    {b.requesterName} &lt;{b.requesterEmail}&gt; · {b.requesterPhone}
                  </p>
                  <p className="mt-1">
                    {b.modality === 'haifa' ? t.modalityHaifa : t.modalityOnline} · {b.durationH}
                    h · ₪{b.priceIls}
                  </p>
                  <p className="mt-1 text-muted-foreground">
                    {t.preferred}:{' '}
                    {new Date(b.preferredStart).toLocaleString(dateLocale, {
                      timeZone: 'Asia/Jerusalem',
                    })}
                  </p>
                  {b.goalText ? (
                    <p className="mt-1">
                      {t.goal}: {b.goalText}
                    </p>
                  ) : null}
                  <Link
                    href={`/book/r/${b.token}`}
                    className="mt-2 inline-flex text-primary underline-offset-4 hover:underline"
                  >
                    {t.openStatus}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>
      ) : null}

      {tab === 'calendar' ? (
        <section className="space-y-4 rounded-2xl border border-border bg-surface-1 p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="font-display text-lg font-semibold">{t.calendarTitle}</h2>
            <span
              className={cn(
                'rounded-md px-2 py-1 text-xs font-semibold uppercase tracking-wide',
                connected ? 'bg-primary/15 text-primary' : 'bg-accent-amber/15 text-foreground',
              )}
            >
              {connected ? t.calendarConnected : t.calendarNotConnected}
            </span>
          </div>

          {(!connected || showTestingHelp) && (
            <div className="space-y-3 rounded-xl border border-accent-amber/40 bg-accent-amber/10 px-4 py-3 text-sm">
              <p className="font-medium text-foreground">{t.testingTitle}</p>
              <p className="text-muted-foreground">{t.testingBody}</p>
              <p className="font-medium text-foreground">{t.testingStepsTitle}</p>
              <ol className="list-decimal space-y-1 ps-5 text-foreground">
                <li>{t.testingStep1}</li>
                <li>{t.testingStep2}</li>
                <li>{t.testingStep3}</li>
                <li>
                  {t.testingStep4.replace('{uri}', REDIRECT_URI)}
                  <code className="mt-1 block break-all rounded-md bg-surface-2 px-2 py-1 text-xs" dir="ltr">
                    {REDIRECT_URI}
                  </code>
                </li>
                <li>{t.testingStep5}</li>
              </ol>
              <p className="text-xs text-muted-foreground">{t.testingPublish}</p>
            </div>
          )}

          <ul className="space-y-1 text-sm text-muted-foreground">
            <li>{data?.oauthConfigured ? t.oauthOk : t.oauthMissing}</li>
            <li>{data?.secretsKeyConfigured ? t.secretsOk : t.secretsMissing}</li>
            <li>{connected ? t.refreshTokenYes : t.refreshTokenNo}</li>
            <li>
              {data?.settings?.googleChannelId
                ? t.watchActive.replace(
                    '{when}',
                    data.settings.googleChannelExpiration
                      ? new Date(data.settings.googleChannelExpiration).toLocaleString(dateLocale, {
                          timeZone: 'Asia/Jerusalem',
                        })
                      : '—',
                  )
                : t.watchInactive}
            </li>
            <li>
              {data?.busyPreview
                ? t.busyCache
                    .replace('{count}', String(data.busyPreview.count))
                    .replace(
                      '{synced}',
                      data.busyPreview.syncedAt
                        ? new Date(data.busyPreview.syncedAt).toLocaleString(dateLocale, {
                            timeZone: 'Asia/Jerusalem',
                          })
                        : '—',
                    )
                : '—'}
            </li>
          </ul>

          <div className="flex flex-wrap gap-2 pt-1">
            <Button asChild disabled={!data?.oauthConfigured}>
              <Link href={data?.connectUrl ?? '#'}>
                {connected ? t.reconnectGoogle : t.connectGoogle}
              </Link>
            </Button>
            <Button
              type="button"
              variant="secondary"
              disabled={saving || !connected}
              onClick={() => void action('refresh_busy')}
            >
              {t.refreshBusy}
            </Button>
            <Button
              type="button"
              variant="secondary"
              disabled={saving || !connected}
              onClick={() => void action('renew_watch')}
            >
              {t.renewWatch}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">{t.calendarHint}</p>
        </section>
      ) : null}

      {tab === 'contacts' ? (
        <form
          onSubmit={saveContacts}
          className="space-y-4 rounded-2xl border border-border bg-surface-1 p-6"
        >
          <h2 className="font-display text-lg font-semibold">{t.contactsTitle}</h2>
          <p className="text-sm text-muted-foreground">{t.contactsBody}</p>
          <div className="space-y-1.5">
            <Label htmlFor="cal-id">{t.calendarId}</Label>
            <Input
              id="cal-id"
              value={calendarId}
              onChange={(e) => setCalendarId(e.target.value)}
              placeholder="primary"
              dir="ltr"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="meet">{t.meetingLink}</Label>
            <Input
              id="meet"
              value={meetingLink}
              onChange={(e) => setMeetingLink(e.target.value)}
              placeholder="https://meet.google.com/..."
              dir="ltr"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="phone">
              {t.phone} {data?.settings?.hasPhone ? t.phoneSet : ''}
            </Label>
            <Input
              id="phone"
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              autoComplete="off"
              dir="ltr"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="address">
              {t.address} {data?.settings?.hasAddress ? t.addressSet : ''}
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
            {saving ? t.saving : t.save}
          </Button>
        </form>
      ) : null}
    </div>
  );
}
