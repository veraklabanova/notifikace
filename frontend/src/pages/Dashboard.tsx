import { useState } from 'react';
import { getStats, getUpcoming, allNotifications } from '../mockData';
import StatusBadge from '../components/StatusBadge';
import { Users, CalendarDays, Bell, AlertTriangle, Play } from 'lucide-react';

export default function Dashboard() {
  const stats = getStats();
  const upcoming = getUpcoming(14);
  const recent = allNotifications.slice(0, 10);
  const [cycleResult, setCycleResult] = useState<string | null>(null);

  const runCycle = () => {
    setCycleResult('Cyklus dokončen: 8 naplánováno, 8 odesláno, 0 chyb, 3 po termínu');
    setTimeout(() => setCycleResult(null), 5000);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <button onClick={runCycle} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
          <Play size={16} /> Spustit notifikační cyklus
        </button>
      </div>

      {cycleResult && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800">{cycleResult}</div>
      )}

      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard icon={Users} label="Aktivní klienti" value={stats.clients.active} sub={`${stats.clients.total} celkem`} color="blue" />
        <StatCard icon={CalendarDays} label="Nadcházející povinnosti" value={stats.obligations.upcoming} sub={`${stats.obligations.urgent_7_days} do 7 dní`} color="purple" />
        <StatCard icon={Bell} label="Odesláno notifikací" value={stats.notifications.sent} sub={`${stats.notifications.pending} čekajících`} color="green" />
        <StatCard icon={AlertTriangle} label="Chyby notifikací" value={stats.notifications.errors} sub={`Import MFČR: ${stats.imports.mfcr_status}`} color={stats.notifications.errors > 0 ? 'red' : 'gray'} />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Nadcházející povinnosti (14 dní)</h2>
          {upcoming.length === 0 ? (
            <p className="text-gray-500 text-sm">Žádné nadcházející povinnosti</p>
          ) : (
            <div className="space-y-3">
              {upcoming.slice(0, 8).map((o) => (
                <div key={o.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{o.title}</div>
                    <div className="text-xs text-gray-500">{o.client_name}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-600">{formatDate(o.deadline_date)}</div>
                    <div className={`text-xs ${o.days_remaining <= 7 ? 'text-red-600 font-medium' : 'text-gray-500'}`}>
                      {o.days_remaining} dní
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Poslední notifikace</h2>
          {recent.length === 0 ? (
            <p className="text-gray-500 text-sm">Zatím žádné notifikace</p>
          ) : (
            <div className="space-y-3">
              {recent.map((n) => (
                <div key={n.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{n.client_name}</div>
                    <div className="text-xs text-gray-500">{n.obligation_title}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={n.notification_type} />
                    <StatusBadge status={n.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, sub, color }: any) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600', purple: 'bg-purple-50 text-purple-600',
    green: 'bg-green-50 text-green-600', red: 'bg-red-50 text-red-600', gray: 'bg-gray-50 text-gray-600',
  };
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center gap-3 mb-3">
        <div className={`p-2 rounded-lg ${colors[color]}`}><Icon size={20} /></div>
        <span className="text-sm text-gray-500">{label}</span>
      </div>
      <div className="text-3xl font-bold text-gray-900">{value}</div>
      <div className="text-xs text-gray-500 mt-1">{sub}</div>
    </div>
  );
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('cs-CZ');
}
