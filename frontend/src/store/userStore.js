import { create } from 'zustand';

const useUserStore = create((set) => ({
  isAuthenticated: false,
  user: null,
  
  setUser: (user) => set((state) => ({ ...state, user })),
  logout: () => set(() => ({ isAuthenticated: false, user: null })),
}));

export default useUserStore;
