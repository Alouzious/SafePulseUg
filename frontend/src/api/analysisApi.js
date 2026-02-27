import api from './axios';

const analysisApi = {

    analyzeReport: (caseNumber) =>
        api.post('/api/analysis/analyze-report/', { case_number: caseNumber }),

    generalAnalysis: (prompt = '') =>
        api.post('/api/analysis/general/', prompt ? { prompt } : {}),

    chat: (message, sessionId = null) =>
        api.post('/api/analysis/chat/', {
            message,
            ...(sessionId && { session_id: sessionId }),
        }),

    getChatHistory: (sessionId) =>
        api.get(`/api/analysis/chat/${sessionId}/`),

    getResults: () =>
        api.get('/api/analysis/results/'),

    getResultById: (id) =>
        api.get(`/api/analysis/results/${id}/`),
};

export default analysisApi;