import api from './axios';

const dashboardApi = {

    getOverview: () =>
        api.get('/api/dashboard/overview/'),

    getCrimesByCategory: (period = 'all') =>
        api.get('/api/dashboard/crimes-by-category/', { params: { period } }),

    getCrimesBySeverity: (period = 'all') =>
        api.get('/api/dashboard/crimes-by-severity/', { params: { period } }),

    getHotspots: (period = 'all', limit = 10) =>
        api.get('/api/dashboard/hotspots/', { params: { period, limit } }),

    getMonthlyTrends: () =>
        api.get('/api/dashboard/trends/monthly/'),

    getDailyTrends: () =>
        api.get('/api/dashboard/trends/daily/'),

    getRecentCrimes: (limit = 10) =>
        api.get('/api/dashboard/recent-crimes/', { params: { limit } }),

    getAlerts: () =>
        api.get('/api/dashboard/alerts/'),

    getMyStats: () =>
        api.get('/api/dashboard/my-stats/'),

    getCategoryDistrict: (params = {}) =>
        api.get('/api/dashboard/category-district/', { params }),
};

export default dashboardApi;