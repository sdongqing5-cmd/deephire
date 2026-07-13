export type InterviewType = 'phone-screen' | 'technical' | 'behavioral' | 'final';
export type InterviewStatus = 'scheduled' | 'completed' | 'cancelled' | 'no-show';
export type InterviewRecommendation = 'strong-proceed' | 'proceed' | 'hold' | 'reject';

export interface InterviewFeedback {
  rating: number; // 1-5
  strengths: string[];
  weaknesses: string[];
  recommendation: InterviewRecommendation;
  comments: string;
}

export interface Interview {
  id: string;
  candidateId: string;
  jobId: string;
  interviewerId: string;
  type: InterviewType;
  status: InterviewStatus;
  scheduledAt: string;
  duration: number; // minutes
  location?: string;
  meetingLink?: string;
  notes?: string;
  feedback?: InterviewFeedback;
  createdAt: string;
  updatedAt: string;
}
