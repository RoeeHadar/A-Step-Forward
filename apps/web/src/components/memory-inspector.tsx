'use client';

import { useState, useTransition } from 'react';
import Link from 'next/link';
import { Pencil, Trash2, Search } from 'lucide-react';
import type { MemoryRecord } from '@asf/schemas/memory';
import { Badge } from '@asf/ui/badge';
import { Button } from '@asf/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@asf/ui/dialog';
import { Input } from '@asf/ui/input';
import { Label } from '@asf/ui/label';
import { Textarea } from '@asf/ui/textarea';
import { deleteMemoryAction, updateMemoryAction } from '@/app/(app)/app/memory/actions';
import { useI18n } from '@/providers/i18n-provider';

export function MemoryInspector({ memories }: { memories: MemoryRecord[] }) {
  const { messages } = useI18n();
  const t = messages.memory;
  const [items, setItems] = useState(memories);
  const [query, setQuery] = useState('');
  const [pending, startTransition] = useTransition();

  const filtered = items.filter(
    (m) =>
      m.content.toLowerCase().includes(query.toLowerCase()) ||
      m.tags.some((tag) => tag.toLowerCase().includes(query.toLowerCase())),
  );

  return (
    <div className="space-y-6">
      <div className="relative max-w-md">
        <Search
          className="absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          aria-hidden
        />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t.searchPlaceholder}
          className="ps-9"
          aria-label={t.searchAriaLabel}
        />
      </div>

      <div className="space-y-4">
        {filtered.map((memory) => (
          <div key={memory.id} className="card-punch rounded-2xl p-5">
            <div className="flex flex-row items-start justify-between gap-4 pb-2">
              <div className="space-y-1">
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">{memory.type}</Badge>
                  {memory.tags.map((tag) => (
                    <Badge key={tag} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
                <h3 className="font-display text-base font-semibold">
                  {memory.summary ?? t.memoryDefault}
                </h3>
              </div>
              <div className="flex gap-1">
                <EditDialog memory={memory} disabled={pending} startTransition={startTransition} />
                <DeleteDialog
                  memory={memory}
                  disabled={pending}
                  startTransition={startTransition}
                  onDeleted={() => setItems((prev) => prev.filter((m) => m.id !== memory.id))}
                />
              </div>
            </div>
            <p className="text-sm">{memory.content}</p>
            <p className="mt-2 text-xs text-muted-foreground">
              <span className="bg-gradient-to-r from-primary to-accent-cyan bg-clip-text text-transparent">
                {t.salience} {Math.round(memory.salience * 100)}%
              </span>
              {' · '}
              <span className="bg-gradient-to-r from-primary to-accent-cyan bg-clip-text text-transparent">
                {t.confidence} {Math.round(memory.confidence * 100)}%
              </span>
            </p>
          </div>
        ))}
        {filtered.length === 0 ? (
          items.length === 0 ? (
            <div className="card-punch rounded-2xl p-8 text-center">
              <p className="text-muted-foreground">{t.noMemoriesYet}</p>
              <p className="mt-2 text-sm text-muted-foreground">{t.noMemoriesCta}</p>
              <Button asChild className="mt-4">
                <Link href="/app/chat/tutor">{t.noMemoriesCtaLink}</Link>
              </Button>
            </div>
          ) : (
            <p className="text-center text-muted-foreground">{t.noSearchResults}</p>
          )
        ) : null}
      </div>
    </div>
  );
}

function EditDialog({
  memory,
  disabled,
  startTransition,
}: {
  memory: MemoryRecord;
  disabled: boolean;
  startTransition: (fn: () => void) => void;
}) {
  const { messages } = useI18n();
  const t = messages.memory;

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label={`${t.editAriaLabel} ${memory.id}`}>
          <Pencil className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form
          action={(formData) => {
            startTransition(() => {
              void updateMemoryAction(formData);
            });
          }}
        >
          <DialogHeader>
            <DialogTitle className="font-display">{t.editTitle}</DialogTitle>
            <DialogDescription>{t.editDescription}</DialogDescription>
          </DialogHeader>
          <input type="hidden" name="memoryId" value={memory.id} />
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor={`content-${memory.id}`}>{t.content}</Label>
              <Textarea id={`content-${memory.id}`} name="content" defaultValue={memory.content} rows={4} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor={`reason-${memory.id}`}>{t.reasonForEdit}</Label>
              <Input
                id={`reason-${memory.id}`}
                name="reason"
                defaultValue={t.defaultEditReason}
                required
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={disabled}>
              {t.save}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function DeleteDialog({
  memory,
  disabled,
  startTransition,
  onDeleted,
}: {
  memory: MemoryRecord;
  disabled: boolean;
  startTransition: (fn: () => void) => void;
  onDeleted: () => void;
}) {
  const { messages } = useI18n();
  const t = messages.memory;

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label={`${t.deleteAriaLabel} ${memory.id}`}>
          <Trash2 className="h-4 w-4 text-destructive" />
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form
          action={(formData) => {
            startTransition(async () => {
              await deleteMemoryAction(formData);
              onDeleted();
            });
          }}
        >
          <DialogHeader>
            <DialogTitle className="font-display">{t.deleteTitle}</DialogTitle>
            <DialogDescription>{t.deleteDescription}</DialogDescription>
          </DialogHeader>
          <input type="hidden" name="memoryId" value={memory.id} />
          <div className="grid gap-2 py-4">
            <Label htmlFor={`delete-reason-${memory.id}`}>{t.reason}</Label>
            <Input
              id={`delete-reason-${memory.id}`}
              name="reason"
              defaultValue={t.defaultDeleteReason}
              required
            />
          </div>
          <DialogFooter>
            <Button type="submit" variant="destructive" disabled={disabled}>
              {t.delete}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
