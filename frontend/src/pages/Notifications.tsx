import { useState, useMemo } from 'react';
import { allNotifications } from '../mockData';
import StatusBadge from '../components/StatusBadge';
import { Send, RotateCcw } from 'lucide-react';

export default function Notifications() {
  const [statusFilter, setStatusFilter] = useState('');
  const [flashMsg, setFlashMsg] = useState<string | null>(null);

  const filtered = useMemo(() => {
    if (!statusFilter) return allNotifications;
    return allNotifications.filter(n => n.status === statusFilter);
  }, [statusFilter]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Notifikace</h1>
        <button
          onClick={() => { setFlashMsg('Naplánováno: 8, Odesláno: 8, Chyby: 0'); setTimeout(() => setFlashMsg(null), 4000); }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
        >
          <Send size={16} /> Naplánovat a odeslat
        </button>
      </div>

      {flashMsg && <div className="mb-4 p-3 bg-blue-50 text-blue-800 rounded-lg text-sm">{flashMsg}</div>}

      <div className="mb-4">
        <select className="px-4 py-2 border border-gray-300 rounded-lg text-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">Všechny stavy ({allNotifications.length})</option>
          <option value="scheduled">Naplánované</option>
          <option value="sent">Odeslané ({allNotifications.filter(n => n.status === 'sent').length})</option>
          <option value="error">Chyby ({allNotifications.filter(n => n.status === 'error').length})</option>
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
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr><td colSpan={8} className="text-center py-8 text-gray-500">Žádné notifikace</td></tr>
            ) : filtered.map((n) => (
              <tr key={n.id} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{n.client_name}</td>
                <td className="px-4 py-3 text-gray-600 max-w-48 truncate">{n.obligation_title}</td>
                <td className="px-4 py-3 text-gray-600">{new Date(n.deadline_date).toLocaleDateString('cs-CZ')}</td>
                <td className="px-4 py-3"><StatusBadge status={n.notification_type} /></td>
                <td className="px-4 py-3"><StatusBadge status={n.status} /></td>
                <td className="px-4 py-3 text-gray-500 text-xs">{n.sent_at ? new Date(n.sent_at).toLocaleString('cs-CZ') : '—'}</td>
                <td className="px-4 py-3 text-gray-500 text-xs">{n.email_to}</td>
                <td className="px-4 py-3">
                  {n.status === 'error' && (
                    <button className="text-blue-600 hover:text-blue-800" title="Odeslat znovu"><RotateCcw size={14} /></button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
