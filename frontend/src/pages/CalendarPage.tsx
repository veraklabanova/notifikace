import { useEffect, useState } from 'react';
import { api } from '../api';
import { Download, RefreshCw } from 'lucide-react';

export default function CalendarPage() {
  const [entries, setEntries] = useState<any[]>([]);
  const [importStatus, setImportStatus] = useState<any>(null);
  const [typeFilter, setTypeFilter] = useState('');
  const [types, setTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [importResult, setImportResult] = useState<any>(null);

  const load = async () => {
    setLoading(true);
    const params: Record<string, string> = {};
    if (typeFilter) params.obligation_type = typeFilter;
    const [data, status, t] = await Promise.all([
      api.getCalendar(params),
      api.getImportStatus(),
      api.getObligationTypes(),
    ]);
    setEntries(data);
    setImportStatus(status);
    setTypes(t);
    setLoading(false);
  };

  useEffect(() => { load(); }, [typeFilter]);

  const doImport = async () => {
    setImportResult(null);
    const result = await api.importMfcr();
    setImportResult(result);
    load();
  };

  const doCompute = async () => {
    const result = await api.computeObligations();
    setImportResult({ status: 'success', message: `Přiřazeno ${result.computed} povinností klientům` });
  };

  const typeLabels: Record<string, string> = {
    dph_mesicni: 'DPH měsíční',
    dph_ctvrtletni: 'DPH čtvrtletní',
    kontrolni_hlaseni_mesicni: 'Kontrolní hlášení měs.',
    kontrolni_hlaseni_ctvrtletni: 'Kontrolní hlášení čtvrt.',
    dpfo: 'Daň z příjmů FO',
    dppo: 'Daň z příjmů PO',
    socialni_osvc: 'Sociální poj. OSVČ',
    zdravotni_osvc: 'Zdravotní poj. OSVČ',
    zamestnanci_mesicni: 'Zaměstnanci měsíčně',
    zamestnanci_rocni: 'Zaměstnanci ročně',
    silnicni_dan: 'Silniční daň',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Daňový kalendář</h1>
        <div className="flex gap-2">
          <button onClick={doImport} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
            <Download size={16} /> Import z MFČR
          </button>
          <button onClick={doCompute} className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
            <RefreshCw size={16} /> Přepočítat povinnosti
          </button>
        </div>
      </div>

      {/* Import status */}
      {importStatus && (
        <div className="mb-6 grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Import MFČR</h3>
            <div className="text-sm">
              Stav: <span className={importStatus.mfcr.status === 'success' ? 'text-green-600' : 'text-yellow-600'}>{importStatus.mfcr.status}</span>
              {importStatus.mfcr.last_import && (
                <span className="text-gray-500 ml-2">({new Date(importStatus.mfcr.last_import).toLocaleString('cs-CZ')})</span>
              )}
            </div>
            {importStatus.mfcr.error && <div className="text-xs text-red-500 mt-1">{importStatus.mfcr.error}</div>}
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Helios Sync</h3>
            <div className="text-sm">
              Stav: <span className={importStatus.helios.status === 'success' ? 'text-green-600' : 'text-yellow-600'}>{importStatus.helios.status}</span>
              {importStatus.helios.last_sync && (
                <span className="text-gray-500 ml-2">({new Date(importStatus.helios.last_sync).toLocaleString('cs-CZ')})</span>
              )}
            </div>
          </div>
        </div>
      )}

      {importResult && (
        <div className={`mb-4 p-3 rounded-lg text-sm ${importResult.status === 'success' ? 'bg-green-50 text-green-800' : 'bg-yellow-50 text-yellow-800'}`}>
          {importResult.message || `Import: ${importResult.status}, ${importResult.entries || 0} záznamů`}
        </div>
      )}

      {/* Filter */}
      <div className="mb-4">
        <select
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
        >
          <option value="">Všechny typy</option>
          {types.map((t) => (
            <option key={t} value={t}>{typeLabels[t] || t}</option>
          ))}
        </select>
      </div>

      {/* Calendar table */}
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
            {loading ? (
              <tr><td colSpan={4} className="text-center py-8 text-gray-500">Načítání...</td></tr>
            ) : entries.length === 0 ? (
              <tr><td colSpan={4} className="text-center py-8 text-gray-500">Žádné záznamy</td></tr>
            ) : (
              entries.map((e) => {
                const isPast = new Date(e.deadline_date) < new Date();
                return (
                  <tr key={e.id} className={`border-b border-gray-50 ${isPast ? 'opacity-50' : ''}`}>
                    <td className="px-4 py-3 text-gray-900 font-medium">{new Date(e.deadline_date).toLocaleDateString('cs-CZ')}</td>
                    <td className="px-4 py-3">
                      <div className="text-gray-900">{e.title}</div>
                      {e.description && <div className="text-xs text-gray-500 mt-0.5">{e.description}</div>}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">
                        {typeLabels[e.obligation_type] || e.obligation_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500">{e.source}</td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
