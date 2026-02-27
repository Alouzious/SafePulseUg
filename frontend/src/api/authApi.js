import api from './axios';

const authApi = {

    register: (data) =>
        api.post('/api/auth/register/', data),

    login: (data) =>
        api.post('/api/auth/login/', data),

    logout: (refreshToken) =>
        api.post('/api/auth/logout/', { refresh: refreshToken }),

    getProfile: () =>
        api.get('/api/auth/profile/'),

    updateProfile: (data) =>
        api.put('/api/auth/profile/', data),

    changePassword: (data) =>
        api.post('/api/auth/change-password/', data),

    getOfficers: () =>
        api.get('/api/auth/officers/'),
};

export default authApi;