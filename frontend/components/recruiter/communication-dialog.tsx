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
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { Recommendation, RecommendationEvent } from '@/lib/mock/recommendations';
import { MessageSquare, User } from 'lucide-react';

interface CommunicationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  recommendation: Recommendation | null;
  onSendMessage: (message: string) => void;
}

export function CommunicationDialog({
  open,
  onOpenChange,
  recommendation,
  onSendMessage,
}: CommunicationDialogProps) {
  const t = useTranslations();
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);

  const handleSend = async () => {
    if (!message.trim()) {
      return;
    }

    setIsSending(true);
    try {
      await onSendMessage(message);
      setMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setMessage('');
    }
    onOpenChange(newOpen);
  };

  const getActorLabel = (actorRole: string) => {
    switch (actorRole) {
      case 'recruiter':
        return t('headhunter.you');
      case 'hr':
        return t('headhunter.hr');
      case 'interviewer':
        return t('headhunter.interviewer');
      case 'candidate':
        return t('headhunter.candidate');
      default:
        return actorRole;
    }
  };

  const getEventTypeLabel = (type: string) => {
    switch (type) {
      case 'submitted':
        return '提交推荐';
      case 'hr_reviewed':
        return 'HR已查看';
      case 'interview_scheduled':
        return '已安排面试';
      case 'interview_completed':
        return '面试完成';
      case 'offer_sent':
        return '已发送Offer';
      case 'accepted':
        return '候选人接受';
      case 'rejected':
        return '已拒绝';
      case 'withdrawn':
        return '已撤回';
      default:
        return type;
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>{t('headhunter.communicationDialogTitle')}</DialogTitle>
          <DialogDescription>
            {recommendation && (
              <span className="text-sm text-muted-foreground">
                {t('headhunter.candidateName')}: {recommendation.candidateId}
              </span>
            )}
          </DialogDescription>
        </DialogHeader>

        {/* Communication History */}
        <div className="flex-1 min-h-0">
          <Label className="text-sm font-semibold mb-2 block">
            {t('headhunter.communicationHistory')}
          </Label>
          <ScrollArea className="h-[300px] rounded-md border p-4">
            {recommendation?.timeline && recommendation.timeline.length > 0 ? (
              <div className="space-y-4">
                {recommendation.timeline.map((event) => (
                  <div key={event.id} className="flex gap-3">
                    <div className="flex-shrink-0 mt-1">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100">
                        <User className="h-4 w-4 text-gray-600" />
                      </div>
                    </div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold">{event.actor}</span>
                        <span className="text-xs text-muted-foreground">
                          {getActorLabel(event.actorRole)}
                        </span>
                        <span className="text-xs text-muted-foreground">·</span>
                        <span className="text-xs text-muted-foreground">
                          {new Date(event.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <div className="text-sm text-gray-700">
                        <span className="font-medium">{getEventTypeLabel(event.type)}</span>
                        {event.notes && (
                          <>
                            <span className="mx-1">-</span>
                            <span>{event.notes}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <MessageSquare className="h-12 w-12 text-gray-400 mb-2" />
                <p className="text-sm text-muted-foreground">
                  {t('headhunter.noCommunicationHistory')}
                </p>
              </div>
            )}
          </ScrollArea>
        </div>

        {/* Write Message */}
        <div className="space-y-2 pt-4">
          <Label htmlFor="message">{t('headhunter.writeMessage')}</Label>
          <Textarea
            id="message"
            placeholder={t('headhunter.messagePlaceholder')}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={4}
            className="resize-none"
          />
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={isSending}
          >
            {t('common.cancel')}
          </Button>
          <Button onClick={handleSend} disabled={!message.trim() || isSending}>
            {isSending ? t('common.loading') : t('headhunter.sendMessage')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
