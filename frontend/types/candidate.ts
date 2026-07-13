export type CandidateStatus = 'new' | 'screening' | 'interviewing' | 'offered' | 'hired' | 'rejected';

export interface Candidate {
  id: string;
  name: string;
  email: string;
  phone: string;
  status: CandidateStatus;
  currentCompany?: string;
  currentTitle?: string;
  yearsOfExperience?: number;
  location?: string;
  avatar?: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface Resume {
  id: string;
  candidateId: string;
  fileName: string;
  fileUrl: string;
  parsedData?: {
    skills: string[];
    education: Array<{
      school: string;
      degree: string;
      major: string;
      startDate: string;
      endDate: string;
    }>;
    experience: Array<{
      company: string;
      title: string;
      startDate: string;
      endDate: string;
      description: string;
    }>;
  };
  uploadedAt: string;
}

export interface Timeline {
  id: string;
  candidateId: string;
  type: 'note' | 'interview' | 'status_change' | 'email' | 'call';
  title: string;
  content: string;
  createdBy: string;
  createdAt: string;
}
