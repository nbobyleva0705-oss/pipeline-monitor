/**
 * API client — thin wrappers around fetch for all backend endpoints.
 */
const API = {
    async _fetch(url, options = {}) {
        const resp = await fetch(url, {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        });
        if (resp.status === 204) return null;
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);
        return data;
    },

    // Summary
    getSummary: () => API._fetch('/api/summary'),

    // Datasets
    getDatasets:      ()       => API._fetch('/datasets/'),
    getDataset:       (id)     => API._fetch(`/datasets/${id}`),
    createDataset:    (body)   => API._fetch('/datasets/', { method: 'POST', body: JSON.stringify(body) }),

    // Pipelines
    getPipelines:     ()       => API._fetch('/pipelines/'),
    getPipeline:      (id)     => API._fetch(`/pipelines/${id}`),
    createPipeline:   (body)   => API._fetch('/pipelines/', { method: 'POST', body: JSON.stringify(body) }),
    patchPipeline:      (id, b)    => API._fetch(`/pipelines/${id}`, { method: 'PATCH', body: JSON.stringify(b) }),
    getAllVersions:      ()         => API._fetch('/pipelines/versions/all'),
    getPipelineVersions:(id)       => API._fetch(`/pipelines/${id}/versions`),
    createPipelineVersion:(id, b)  => API._fetch(`/pipelines/${id}/versions`, { method: 'POST', body: JSON.stringify(b) }),
    runPipeline:        (id)       => API._fetch(`/pipelines/${id}/run`, { method: 'POST' }),

    // Runs
    getRuns:          (params) => API._fetch('/runs/?' + new URLSearchParams(params || {})),
    getRun:           (id)     => API._fetch(`/runs/${id}`),
    patchRun:         (id, body) => API._fetch(`/runs/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),

    // Alert rules
    getAlertRules:    ()       => API._fetch('/alert-rules/'),
    getAlertRule:     (id)     => API._fetch(`/alert-rules/${id}`),
    createAlertRule:  (body)   => API._fetch('/alert-rules/', { method: 'POST', body: JSON.stringify(body) }),
    patchAlertRule:   (id, b)  => API._fetch(`/alert-rules/${id}`, { method: 'PATCH', body: JSON.stringify(b) }),
    deleteAlertRule:  (id)     => API._fetch(`/alert-rules/${id}`, { method: 'DELETE' }),

    // Alerts
    getAlerts:        ()       => API._fetch('/alerts/'),
    getAlert:         (id)     => API._fetch(`/alerts/${id}`),
};

// Helpers
function badge(status) {
    return `<span class="badge badge-${status}">${status}</span>`;
}

function normalizeTs(ts) {
    if (!ts) return null;
    // Python isoformat() returns +00:00, replace with Z
    const s = ts.replace('+00:00', 'Z');
    return s.endsWith('Z') ? s : s + 'Z';
}

function fmtDate(ts) {
    if (!ts) return '—';
    const d = new Date(normalizeTs(ts));
    return isNaN(d) ? ts : d.toLocaleString();
}

function fmtRuntime(start, end) {
    if (!start || !end) return '—';
    const s = Math.round((new Date(normalizeTs(end)) - new Date(normalizeTs(start))) / 1000);
    if (s < 60) return `${s}s`;
    return `${Math.floor(s / 60)}m ${s % 60}s`;
}

function showState(container, type, msg) {
    container.innerHTML = `<div class="state-msg ${type === 'error' ? 'error' : ''}">${msg}</div>`;
}

function navActive() {
    const path = location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('nav a').forEach(a => {
        const href = a.getAttribute('href').split('/').pop();
        a.classList.toggle('active', href === path);
    });
}
