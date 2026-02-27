import { create } from 'zustand';
import { persist  } from 'zustand/middleware';

const useAuthStore = create(
    persist(
        (set, get) => ({
            // ── State ──────────────────────────────────────────
            officer:       null,
            accessToken:   null,
            refreshToken:  null,
            isAuthenticated: false,

            // ── Actions ────────────────────────────────────────
            setAuth: (officer, tokens) => {
                localStorage.setItem('access_token',  tokens.access);
                localStorage.setItem('refresh_token', tokens.refresh);
                set({
                    officer,
                    accessToken:     tokens.access,
                    refreshToken:    tokens.refresh,
                    isAuthenticated: true,
                });
            },

            updateOfficer: (officer) => set({ officer }),

            logout: () => {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                set({
                    officer:         null,
                    accessToken:     null,
                    refreshToken:    null,
                    isAuthenticated: false,
                });
            },
        }),
        {
            name: 'safepulse-auth',
        }
    )
);

export default useAuthStore;