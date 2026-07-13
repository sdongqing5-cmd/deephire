'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { mockCandidates } from '@/lib/mock/candidates';
import type { ClientJob } from '@/lib/mock/client-jobs';

interface RecommendDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  job: ClientJob | null;
  onSubmit: (candidateId: string, notes: string) => void;
}

export function RecommendDialog({
  open,
  onOpenChange,
  job,
  onSubmit,
}: RecommendDialogProps) {
  const t = useTranslations();
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>('');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!selectedCandidateId || !notes.trim()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(selectedCandidateId, notes);
      // Reset form
      setSelectedCandidateId('');
      setNotes('');
      onOpenChange(false);
    } catch (error) {
      console.error('Failed to submit recommendation:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      // Reset form when closing
      setSelectedCandidateId('');
      setNotes('');
    }
    onOpenChange(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{t('headhunter.recommendDialogTitle')}</DialogTitle>
          <DialogDescription>
            {job?.title && (
              <span className="text-sm text-muted-foreground">
                {t('headhunter.position')}: {job.titleKey ? t(`jobs.${job.titleKey}`) : job.title}
              </span>
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Candidate Selection */}
          <div className="space-y-2">
            <Label htmlFor="candidate">{t('headhunter.selectCandidate')}</Label>
            <Select value={selectedCandidateId} onValueChange={setSelectedCandidateId}>
              <SelectTrigger id="candidate">
                <SelectValue placeholder={t('headhunter.selectCandidatePlaceholder')} />
              </SelectTrigger>
              <SelectContent>
                {mockCandidates.map((candidate) => (
                  <SelectItem key={candidate.id} value={candidate.id}>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{candidate.name}</span>
                      <span className="text-xs text-muted-foreground">
                        {candidate.currentTitle} @ {candidate.currentCompany}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Recommendation Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">{t('headhunter.recommendationNotes')}</Label>
            <Textarea
              id="notes"
              placeholder={t('headhunter.recommendationNotesPlaceholder')}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={6}
              className="resize-none"
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={isSubmitting}
          >
            {t('common.cancel')}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!selectedCandidateId || !notes.trim() || isSubmitting}
          >
            {isSubmitting ? t('common.loading') : t('headhunter.submitRecommendation')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
