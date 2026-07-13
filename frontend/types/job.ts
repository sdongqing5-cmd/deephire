export type JobStatus = 'draft' | 'open' | 'closed' | 'filled';

export interface Job {
  id: string;
  title: string;
  titleKey?: string;
  department: string;
  location: string;
  type: 'full-time' | 'part-time' | 'contract' | 'internship';
  status: JobStatus;
  description: string;
  requirements: string[];
  responsibilities: string[];
  salaryRange?: {
    min: number;
    max: number;
    currency: string;
  };
  hiringManagerId: string;
  recruiterId?: string;
  openings: number;
  createdAt: string;
  updatedAt: string;
}

export interface CandidateJob {
  id: string;
  candidateId: string;
  jobId: string;
  status: 'applied' | 'screening' | 'interviewing' | 'offered' | 'hired' | 'rejected';
  appliedAt: string;
  updatedAt: string;
}
