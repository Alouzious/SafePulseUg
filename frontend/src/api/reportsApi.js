import api from './axios';

const reportsApi = {

    downloadCrimeListPdf: (filters = {}) =>
        api.post('/api/reports/crime-list/pdf/', filters, {
            responseType: 'blob'
        }),

    downloadCrimeListExcel: (filters = {}) =>
        api.post('/api/reports/crime-list/excel/', filters, {
            responseType: 'blob'
        }),

    downloadCrimePdf: (caseNumber) =>
        api.get(`/api/reports/crime/${caseNumber}/pdf/`, {
            responseType: 'blob'
        }),

    downloadAnalysisPdf: (id) =>
        api.get(`/api/reports/analysis/${id}/pdf/`, {
            responseType: 'blob'
        }),

    getHistory: () =>
        api.get('/api/reports/history/'),
};

export default reportsApi;