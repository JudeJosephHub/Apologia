import { create } from "zustand";
import type { Sermon } from "@/lib/api";

interface AppState {
  // Auth
  user: { id: string; email: string } | null;
  accessToken: string | null;
  setUser: (user: { id: string; email: string } | null, token: string | null) => void;
  logout: () => void;

  // Sermons
  sermons: Sermon[];
  setSermons: (sermons: Sermon[]) => void;

  // Search
  searchQuery: string;
  setSearchQuery: (query: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Dev mode: auto-login (no Supabase configured)
  user: { id: "dev-user-001", email: "judejosephsimon@gmail.com" },
  accessToken: "dev-token",
  setUser: (user, token) => set({ user, accessToken: token }),
  logout: () => set({ user: null, accessToken: null }),

  sermons: [],
  setSermons: (sermons) => set({ sermons }),

  searchQuery: "",
  setSearchQuery: (searchQuery) => set({ searchQuery }),
}));
