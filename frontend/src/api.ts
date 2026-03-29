const BASE = '/api';

async function request(path: string, options?: RequestInit) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Dashboard
  getStats: () => request('/dashboard/stats'),
  getUpcoming: (days = 30) => request(`/dashboard/upcoming?days=${days}`),
  getRecentNotifications: (limit = 20) => request(`/dashboard/recent-notifications?limit=${limit}`),

  // Clients
  getClients: (params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request(`/clients${qs}`);
  },
  getClient: (id: number) => request(`/clients/${id}`),
  getClientObligations: (id: number) => request(`/clients/${id}/obligations`),
  createClient: (data: any) => request('/clients', { method: 'POST', body: JSON.stringify(data) }),
  updateClient: (id: number, data: any) => request(`/clients/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  // Calendar
  getCalendar: (params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request(`/calendar${qs}`);
  },
  importMfcr: () => request('/calendar/import-mfcr', { method: 'POST' }),
  computeObligations: () => request('/calendar/compute-obligations', { method: 'POST' }),
  getImportStatus: () => request('/calendar/import-status'),
  getObligationTypes: () => request('/calendar/obligation-types'),

  // Notifications
  getNotifications: (params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request(`/notifications${qs}`);
  },
  planNotifications: () => request('/notifications/plan', { method: 'POST' }),
  sendNotifications: () => request('/notifications/send', { method: 'POST' }),
  runCycle: () => request('/notifications/run-cycle', { method: 'POST' }),
  resendNotification: (id: number) => request(`/notifications/${id}/resend`, { method: 'POST' }),

  // Rules
  getRules: () => request('/rules'),
  createRule: (data: any) => request('/rules', { method: 'POST', body: JSON.stringify(data) }),
  updateRule: (id: number, data: any) => request(`/rules/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteRule: (id: number) => request(`/rules/${id}`, { method: 'DELETE' }),
};
