import { useState, useMemo } from 'react';
import { calendarEntries, obligationTypes } from '../mockData';
import { Download, RefreshCw } from 'lucide-react';

const typeLabels: Record<string, string> = {
  dph_mesicni: 'DPH měsíční', dph_ctvrtletni: 'DPH čtvrtletní',
  kontrolni_hlaseni_mesicni: 'Kontrolní hlášení měs.', kontrolni_hlaseni_ctvrtletni: 'Kontrolní hlášení čtvrt.',
  dpfo: 'Daň z příjmů FO', dppo: 'Daň z příjmů PO',
  socialni_osvc: 'Sociální poj. OSVČ', zdravotni_osvc: 'Zdravotní poj. OSVČ',
  zamestnanci_mesicni: 'Zaměstnanci měsíčně', zamestnanci_rocni: 'Zaměstnanci ročně',
  silnicni_dan: 'Silniční daň',
};

export default function CalendarPage() {
  const [typeFilter, setTypeFilter] = useState('');
  const [flashMsg, setFlashMsg] = useState<string | null>(null);

  const filtered = useMemo(() => {
    if (!typeFilter) return calendarEntries;
    return calendarEntries.filter(e => e.obligation_type === typeFilter);
  }, [typeFilter]);

  const flash = (msg: string) => { setFlashMsg(msg); setTimeout(() => setFlashMsg(null), 4000); };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Daňový kalendář</h1>
        <div className="flex gap-2">
          <button onClick={() => flash('Import MFČR: fallback data — otevřená data MFČR nejsou momentálně dostupná')} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
            <Download size={16} /> Import z MFČR
          </button>
          <button onClick={() => flash('Povinnosti přepočteny pro všechny aktivní klienty')} className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
            <RefreshCw size={16} /> Přepočítat povinnosti
          </button>
        </div>
      </div>

      <div className="mb-6 grid grid-cols-2 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-1">Import MFČR</h3>
          <div className="text-sm">Stav: <span className="text-yellow-600">fallback</span> <span className="text-gray-500">(použita lokální data)</span></div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-1">Helios Sync</h3>
          <div className="text-sm">Stav: <span className="text-green-600">success</span> <span className="text-gray-500">(seed data)</span></div>
        </div>
      </div>

      {flashMsg && <div className="mb-4 p-3 rounded-lg text-sm bg-yellow-50 text-yellow-800">{flashMsg}</div>}

      <div className="mb-4">
        <select className="px-4 py-2 border border-gray-300 rounded-lg text-sm" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
          <option value="">Všechny typy ({calendarEntries.length})</option>
          {obligationTypes.map((t) => (
            <option key={t} value={t}>{typeLabels[t] || t}</option>
          ))}
        </select>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Termín</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Povinnost</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Typ</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Zdroj</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((e) => {
              const isPast = new Date(e.deadline_date) < new Date();
              return (
                <tr key={e.id} className={`border-b border-gray-50 ${isPast ? 'opacity-50' : ''}`}>
                  <td className="px-4 py-3 text-gray-900 font-medium">{new Date(e.deadline_date).toLocaleDateString('cs-CZ')}</td>
                  <td className="px-4 py-3">
                    <div className="text-gray-900">{e.title}</div>
                    {e.description && <div className="text-xs text-gray-500 mt-0.5">{e.description}</div>}
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-flex px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">{typeLabels[e.obligation_type] || e.obligation_type}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-500">{e.source}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
