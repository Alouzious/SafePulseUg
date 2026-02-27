// ─────────────────────────────────────────────────────────────
// DOWNLOAD BLOB FILE (for PDF/Excel)
// ─────────────────────────────────────────────────────────────
export const downloadFile = (blob, filename) => {
    const url  = window.URL.createObjectURL(new Blob([blob]));
    const link = document.createElement('a');
    link.href  = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
};


// ─────────────────────────────────────────────────────────────
// SEVERITY COLOR
// ─────────────────────────────────────────────────────────────
export const getSeverityColor = (severity) => {
    const map = {
        low:      '#16a34a',
        medium:   '#f97316',
        high:     '#dc2626',
        critical: '#7c3aed',
    };
    return map[severity] || '#6b7280';
};

export const getSeverityBg = (severity) => {
    const map = {
        low:      '#dcfce7',
        medium:   '#ffedd5',
        high:     '#fee2e2',
        critical: '#ede9fe',
    };
    return map[severity] || '#f3f4f6';
};


// ─────────────────────────────────────────────────────────────
// STATUS COLOR
// ─────────────────────────────────────────────────────────────
export const getStatusColor = (status) => {
    const map = {
        reported:            '#3b82f6',
        under_investigation: '#f97316',
        solved:              '#16a34a',
        closed:              '#6b7280',
        cold_case:           '#7c3aed',
    };
    return map[status?.toLowerCase().replace(' ', '_')] || '#6b7280';
};


// ─────────────────────────────────────────────────────────────
// FORMAT DATE
// ─────────────────────────────────────────────────────────────
export const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-UG', {
        year:  'numeric',
        month: 'short',
        day:   'numeric',
    });
};

export const formatDateTime = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleString('en-UG', {
        year:   'numeric',
        month:  'short',
        day:    'numeric',
        hour:   '2-digit',
        minute: '2-digit',
    });
};


// ─────────────────────────────────────────────────────────────
// CAPITALIZE
// ─────────────────────────────────────────────────────────────
export const capitalize = (str) => {
    if (!str) return '';
    return str.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
};


// ─────────────────────────────────────────────────────────────
// TRUNCATE TEXT
// ─────────────────────────────────────────────────────────────
export const truncate = (str, length = 60) => {
    if (!str) return '';
    return str.length > length ? str.substring(0, length) + '...' : str;
};