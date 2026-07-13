import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types/user';
import { mockUsers } from '@/lib/mock/users';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  hasHydrated: boolean;
  setHasHydrated: (hasHydrated: boolean) => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      hasHydrated: false,

      setHasHydrated: (hasHydrated: boolean) => {
        set({ hasHydrated });
      },

      login: async (email: string) => {
        // Simulate API delay
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Find user in mock data
        const user = mockUsers.find((u) => u.email === email);

        if (!user) {
          throw new Error('Invalid email or password');
        }

        // In a real app, we would verify the password
        // For now, any password works with the correct email
        set({ user, isAuthenticated: true });
      },

      logout: () => {
        set({ user: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
