import { User } from '@/types/user';

export const mockUsers: User[] = [
  {
    id: '1',
    email: 'hr@deephire.com',
    name: 'Sarah Chen',
    role: 'hr',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
  {
    id: '2',
    email: 'recruiter@deephire.com',
    name: 'Mike Johnson',
    role: 'recruiter',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Mike',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
  {
    id: '3',
    email: 'interviewer@deephire.com',
    name: 'Emily Wang',
    role: 'interviewer',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Emily',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
];
