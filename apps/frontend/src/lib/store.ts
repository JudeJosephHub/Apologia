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
  user: null,
  accessToken: null,
  setUser: (user, token) => set({ user, accessToken: token }),
  logout: () => set({ user: null, accessToken: null }),

  sermons: [],
  setSermons: (sermons) => set({ sermons }),

  searchQuery: "",
  setSearchQuery: (searchQuery) => set({ searchQuery }),
}));
