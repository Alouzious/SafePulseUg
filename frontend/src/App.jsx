import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster }          from 'react-hot-toast';
import ProtectedRoute       from './components/common/ProtectedRoute';
import Layout               from './components/layout/Layout';
import LoginPage            from './pages/auth/LoginPage';
import RegisterPage         from './pages/auth/RegisterPage';
import DashboardPage        from './pages/dashboard/DashboardPage';
import CrimesListPage       from './pages/crimes/CrimesListPage';
import CrimeDetailPage      from './pages/crimes/CrimeDetailPage';
import AddCrimePage         from './pages/crimes/AddCrimePage';
import UploadCrimesPage     from './pages/crimes/UploadCrimesPage';
import AnalysisPage         from './pages/analysis/AnalysisPage';
import ChatPage             from './pages/analysis/ChatPage';
import ReportsPage          from './pages/reports/ReportsPage';

function App() {
    return (
        <BrowserRouter>
            <Toaster
                position="top-right"
                toastOptions={{
                    duration: 4000,
                    style: {
                        background:   '#0f2744',
                        color:        'white',
                        fontSize:     '13px',
                        borderRadius: '10px',
                        padding:      '12px 16px',
                        boxShadow:    '0 8px 24px rgba(0,0,0,0.2)',
                    },
                    success: {
                        iconTheme: { primary: '#4ade80', secondary: '#0f2744' },
                    },
                    error: {
                        iconTheme: { primary: '#f87171', secondary: '#0f2744' },
                    },
                }}
            />
            <Routes>
                {/* ── Public Routes ──────────────────────────── */}
                <Route path="/login"    element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* ── Protected Routes ───────────────────────── */}
                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <Layout />
                        </ProtectedRoute>
                    }
                >
                    <Route index                    element={<Navigate to="/dashboard" replace />} />
                    <Route path="dashboard"         element={<DashboardPage />} />

                    {/* Crimes */}
                    <Route path="crimes"            element={<CrimesListPage />} />
                    <Route path="crimes/add"        element={<AddCrimePage />} />
                    <Route path="crimes/upload"     element={<UploadCrimesPage />} />
                    <Route path="crimes/:id"        element={<CrimeDetailPage />} />

                    {/* AI */}
                    <Route path="analysis"          element={<AnalysisPage />} />
                    <Route path="chat"              element={<ChatPage />} />

                    {/* Reports */}
                    <Route path="reports"           element={<ReportsPage />} />
                </Route>

                {/* ── Catch All ──────────────────────────────── */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;