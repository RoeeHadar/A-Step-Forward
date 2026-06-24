'use client';

import { useState, useTransition } from 'react';
import { Pencil, Trash2, Search } from 'lucide-react';
import type { MemoryRecord } from '@asf/schemas/memory';
import { Badge } from '@asf/ui/badge';
import { Button } from '@asf/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
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

export function MemoryInspector({ memories }: { memories: MemoryRecord[] }) {
  const [items, setItems] = useState(memories);
  const [query, setQuery] = useState('');
  const [pending, startTransition] = useTransition();

  const filtered = items.filter(
    (m) =>
      m.content.toLowerCase().includes(query.toLowerCase()) ||
      m.tags.some((t) => t.toLowerCase().includes(query.toLowerCase())),
  );

  return (
    <div className="space-y-6">
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search memories…"
          className="pl-9"
          aria-label="Search memories"
        />
      </div>

      <div className="space-y-4">
        {filtered.map((memory) => (
          <Card key={memory.id}>
            <CardHeader className="flex flex-row items-start justify-between gap-4 pb-2">
              <div className="space-y-1">
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">{memory.type}</Badge>
                  {memory.tags.map((tag) => (
                    <Badge key={tag} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
                <CardTitle className="text-base font-normal">{memory.summary ?? 'Memory'}</CardTitle>
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
            </CardHeader>
            <CardContent>
              <p className="text-sm">{memory.content}</p>
              <p className="mt-2 text-xs text-muted-foreground">
                Salience {Math.round(memory.salience * 100)}% · Confidence{' '}
                {Math.round(memory.confidence * 100)}%
              </p>
            </CardContent>
          </Card>
        ))}
        {filtered.length === 0 ? (
          <p className="text-center text-muted-foreground">
            {items.length === 0
              ? 'No memories yet — start chatting with an agent and we\u2019ll build a picture of how you learn.'
              : 'No memories match your search.'}
          </p>
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
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label={`Edit memory ${memory.id}`}>
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
            <DialogTitle>Edit memory</DialogTitle>
            <DialogDescription>Corrections are logged for audit.</DialogDescription>
          </DialogHeader>
          <input type="hidden" name="memoryId" value={memory.id} />
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor={`content-${memory.id}`}>Content</Label>
              <Textarea id={`content-${memory.id}`} name="content" defaultValue={memory.content} rows={4} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor={`reason-${memory.id}`}>Reason for edit</Label>
              <Input id={`reason-${memory.id}`} name="reason" defaultValue="Learner correction" required />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={disabled}>
              Save
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
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label={`Delete memory ${memory.id}`}>
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
            <DialogTitle>Delete memory</DialogTitle>
            <DialogDescription>
              This soft-deletes the memory and records an audit event. This cannot be undone from the UI.
            </DialogDescription>
          </DialogHeader>
          <input type="hidden" name="memoryId" value={memory.id} />
          <div className="grid gap-2 py-4">
            <Label htmlFor={`delete-reason-${memory.id}`}>Reason</Label>
            <Input id={`delete-reason-${memory.id}`} name="reason" defaultValue="Learner requested deletion" required />
          </div>
          <DialogFooter>
            <Button type="submit" variant="destructive" disabled={disabled}>
              Delete
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
