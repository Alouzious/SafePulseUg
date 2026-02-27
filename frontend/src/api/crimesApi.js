import api from './axios';

const crimesApi = {

    getAll: (params = {}) =>
        api.get('/api/crimes/', { params }),

    getById: (id) =>
        api.get(`/api/crimes/${id}/`),

    create: (data) =>
        api.post('/api/crimes/', data),

    update: (id, data) =>
        api.put(`/api/crimes/${id}/`, data),

    delete: (id) =>
        api.delete(`/api/crimes/${id}/`),

    getMyReports: () =>
        api.get('/api/crimes/my-reports/'),

    getStats: () =>
        api.get('/api/crimes/stats/'),

    addSuspect: (crimeId, data) =>
        api.post(`/api/crimes/${crimeId}/suspects/`, data),

    removeSuspect: (crimeId, suspectId) =>
        api.delete(`/api/crimes/${crimeId}/suspects/${suspectId}/`),

    addWitness: (crimeId, data) =>
        api.post(`/api/crimes/${crimeId}/witnesses/`, data),

    removeWitness: (crimeId, witnessId) =>
        api.delete(`/api/crimes/${crimeId}/witnesses/${witnessId}/`),
};

export default crimesApi;