import { useEffect, useState } from 'react';
import { api } from '../api';
import StatusBadge from '../components/StatusBadge';
import { Send, RotateCcw } from 'lucide-react';

export default function Notifications() {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [actionResult, setActionResult] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    const params: Record<string, string> = { limit: '100' };
    if (statusFilter) params.status = statusFilter;
    const data = await api.getNotifications(params);
    setNotifications(data);
    setLoading(false);
  };

  useEffect(() => { load(); }, [statusFilter]);

  const planAndSend = async () => {
    setActionResult(null);
    const result = await api.runCycle();
    setActionResult(
      `Naplánováno: ${result.notifications_planned}, Odesláno: ${result.notifications_sent}, Chyby: ${result.errors}`
    );
    load();
  };

  const resend = async (id: number) => {
    await api.resendNotification(id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Notifikace</h1>
        <button onClick={planAndSend} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
          <Send size={16} /> Naplánovat a odeslat
        </button>
      </div>

      {actionResult && (
        <div className="mb-4 p-3 bg-blue-50 text-blue-800 rounded-lg text-sm">{actionResult}</div>
      )}

      <div className="mb-4">
        <select
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">Všechny stavy</option>
          <option value="scheduled">Naplánované</option>
          <option value="sent">Odeslané</option>
          <option value="error">Chyby</option>
        </select>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Klient</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Povinnost</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Termín</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Typ</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Stav</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Odesláno</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">E-mail</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={8} className="text-center py-8 text-gray-500">Načítání...</td></tr>
            ) : notifications.length === 0 ? (
              <tr><td colSpan={8} className="text-center py-8 text-gray-500">Žádné notifikace</td></tr>
            ) : (
              notifications.map((n) => (
                <tr key={n.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{n.client_name}</td>
                  <td className="px-4 py-3 text-gray-600">{n.obligation_title}</td>
                  <td className="px-4 py-3 text-gray-600">{new Date(n.deadline_date).toLocaleDateString('cs-CZ')}</td>
                  <td className="px-4 py-3"><StatusBadge status={n.notification_type} /></td>
                  <td className="px-4 py-3"><StatusBadge status={n.status} /></td>
                  <td className="px-4 py-3 text-gray-500 text-xs">
                    {n.sent_at ? new Date(n.sent_at).toLocaleString('cs-CZ') : '—'}
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{n.email_to}</td>
                  <td className="px-4 py-3">
                    {n.status === 'error' && (
                      <button
                        onClick={(e) => { e.stopPropagation(); resend(n.id); }}
                        className="text-blue-600 hover:text-blue-800"
                        title="Odeslat znovu"
                      >
                        <RotateCcw size={14} />
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
