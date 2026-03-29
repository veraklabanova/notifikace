import { useEffect, useState } from 'react';
import { api } from '../api';
import StatusBadge from '../components/StatusBadge';
import { Search, ChevronDown, ChevronUp } from 'lucide-react';

export default function Clients() {
  const [clients, setClients] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [expanded, setExpanded] = useState<number | null>(null);
  const [obligations, setObligations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const params: Record<string, string> = {};
    if (search) params.search = search;
    if (statusFilter) params.status = statusFilter;
    const data = await api.getClients(params);
    setClients(data);
    setLoading(false);
  };

  useEffect(() => { load(); }, [statusFilter]);

  const toggleExpand = async (id: number) => {
    if (expanded === id) {
      setExpanded(null);
      return;
    }
    setExpanded(id);
    const obs = await api.getClientObligations(id);
    setObligations(obs);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Klienti</h1>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Hledat klienta..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && load()}
          />
        </div>
        <select
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">Všechny stavy</option>
          <option value="active">Aktivní</option>
          <option value="suspended">Pozastavení</option>
          <option value="terminated">Ukončení</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Jméno</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">IČO</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Typ</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">DPH</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Zaměstnanci</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Stav</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Povinnosti</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={8} className="text-center py-8 text-gray-500">Načítání...</td></tr>
            ) : clients.length === 0 ? (
              <tr><td colSpan={8} className="text-center py-8 text-gray-500">Žádní klienti</td></tr>
            ) : (
              clients.map((c) => (
                <>
                  <tr
                    key={c.id}
                    className="border-b border-gray-50 hover:bg-gray-50 cursor-pointer"
                    onClick={() => toggleExpand(c.id)}
                  >
                    <td className="px-4 py-3 font-medium text-gray-900">{c.name}</td>
                    <td className="px-4 py-3 text-gray-600">{c.ico}</td>
                    <td className="px-4 py-3 text-gray-600">{c.subject_type === 'osvc' ? 'OSVČ' : 's.r.o.'}</td>
                    <td className="px-4 py-3">
                      {c.vat_payer ? (
                        <span className="text-green-600">{c.vat_frequency === 'monthly' ? 'Měsíčně' : 'Čtvrtletně'}</span>
                      ) : (
                        <span className="text-gray-400">Ne</span>
                      )}
                    </td>
                    <td className="px-4 py-3">{c.has_employees ? 'Ano' : 'Ne'}</td>
                    <td className="px-4 py-3"><StatusBadge status={c.status} /></td>
                    <td className="px-4 py-3 text-gray-600">{c.upcoming_count}</td>
                    <td className="px-4 py-3">
                      {expanded === c.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </td>
                  </tr>
                  {expanded === c.id && (
                    <tr key={`${c.id}-detail`}>
                      <td colSpan={8} className="bg-gray-50 px-8 py-4">
                        <div className="mb-2 text-xs text-gray-500">E-mail: {c.email}</div>
                        <h3 className="text-sm font-semibold mb-2">Povinnosti klienta:</h3>
                        {obligations.length === 0 ? (
                          <p className="text-sm text-gray-500">Žádné povinnosti</p>
                        ) : (
                          <div className="grid gap-2">
                            {obligations.map((o: any) => (
                              <div key={o.id} className="flex items-center justify-between bg-white rounded px-3 py-2 border border-gray-200">
                                <div>
                                  <span className="text-sm">{o.title}</span>
                                  <span className="text-xs text-gray-500 ml-2">{o.obligation_type}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className="text-sm text-gray-600">{formatDate(o.deadline_date)}</span>
                                  <StatusBadge status={o.status} />
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </td>
                    </tr>
                  )}
                </>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('cs-CZ');
}
