export type ActivityType =
  | 'candidate_added'
  | 'candidate_updated'
  | 'status_changed'
  | 'interview_scheduled'
  | 'interview_completed'
  | 'interview_cancelled'
  | 'offer_sent'
  | 'offer_accepted'
  | 'offer_rejected'
  | 'job_created'
  | 'job_updated'
  | 'job_closed'
  | 'note_added'
  | 'resume_uploaded';

export interface Activity {
  id: string;
  type: ActivityType;
  userId: string;
  candidateId?: string;
  jobId?: string;
  interviewId?: string;
  title: string;
  description: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}
