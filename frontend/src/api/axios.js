import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ─────────────────────────────────────────────────────────────
// AXIOS INSTANCE
// ─────────────────────────────────────────────────────────────
const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// ─────────────────────────────────────────────────────────────
// REQUEST INTERCEPTOR — Attach JWT token to every request
// ─────────────────────────────────────────────────────────────
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// ─────────────────────────────────────────────────────────────
// RESPONSE INTERCEPTOR — Auto refresh token on 401
// ─────────────────────────────────────────────────────────────
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                const response     = await axios.post(
                    `${BASE_URL}/api/auth/token/refresh/`,
                    { refresh: refreshToken }
                );

                const newAccessToken = response.data.access;
                localStorage.setItem('access_token', newAccessToken);
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

                return api(originalRequest);
            } catch (refreshError) {
                // Refresh failed — clear storage and redirect to login
                localStorage.clear();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;






















// import axios from 'axios';

// const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// // ─────────────────────────────────────────────────────────────
// // AXIOS INSTANCE
// // ─────────────────────────────────────────────────────────────
// const api = axios.create({
//     baseURL: BASE_URL,
//     headers: {
//         'Content-Type': 'application/json',
//     },
// });

// // ─────────────────────────────────────────────────────────────
// // REQUEST INTERCEPTOR — Attach JWT token to every request
// // ─────────────────────────────────────────────────────────────
// api.interceptors.request.use(
//     (config) => {
//         const token = localStorage.getItem('access_token');
//         if (token) {
//             config.headers.Authorization = `Bearer ${token}`;
//         }
//         return config;
//     },
//     (error) => Promise.reject(error)
// );

// // ─────────────────────────────────────────────────────────────
// // RESPONSE INTERCEPTOR — Auto refresh token on 401
// // ─────────────────────────────────────────────────────────────
// api.interceptors.response.use(
//     (response) => response,
//     async (error) => {
//         const originalRequest = error.config;

//         if (error.response?.status === 401 && !originalRequest._retry) {
//             originalRequest._retry = true;

//             try {
//                 const refreshToken = localStorage.getItem('refresh_token');
//                 const response     = await axios.post(
//                     `${BASE_URL}/api/auth/token/refresh/`,
//                     { refresh: refreshToken }
//                 );

//                 const newAccessToken = response.data.access;
//                 localStorage.setItem('access_token', newAccessToken);
//                 originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

//                 return api(originalRequest);
//             } catch (refreshError) {
//                 // Refresh failed — clear storage and redirect to login
//                 localStorage.clear();
//                 window.location.href = '/login';
//                 return Promise.reject(refreshError);
//             }
//         }

//         return Promise.reject(error);
//     }
// );

// export default api;