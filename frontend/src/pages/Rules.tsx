import { useState } from 'react';
import { mappingRules as initialRules } from '../mockData';
import { Plus, Trash2, ToggleLeft, ToggleRight } from 'lucide-react';

const typeLabels: Record<string, string> = {
  dph_mesicni: 'DPH měsíční', dph_ctvrtletni: 'DPH čtvrtletní',
  kontrolni_hlaseni_mesicni: 'Kontrolní hlášení měs.', kontrolni_hlaseni_ctvrtletni: 'Kontrolní hlášení čtvrt.',
  dpfo: 'Daň z příjmů FO', dppo: 'Daň z příjmů PO',
  socialni_osvc: 'Sociální poj. OSVČ', zdravotni_osvc: 'Zdravotní poj. OSVČ',
  zamestnanci_mesicni: 'Zaměstnanci měsíčně', zamestnanci_rocni: 'Zaměstnanci ročně',
  silnicni_dan: 'Silniční daň',
};

export default function Rules() {
  const [rules, setRules] = useState(initialRules);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ subject_type: '', vat_payer: '', vat_frequency: '', has_employees: '', obligation_type: '', description: '' });

  const toggleRule = (id: number) => {
    setRules(rules.map(r => r.id === id ? { ...r, is_active: !r.is_active } : r));
  };

  const deleteRule = (id: number) => {
    setRules(rules.filter(r => r.id !== id));
  };

  const addRule = () => {
    const newRule = {
      id: Math.max(...rules.map(r => r.id)) + 1,
      subject_type: form.subject_type || null,
      vat_payer: form.vat_payer === '' ? null : form.vat_payer === 'true',
      vat_frequency: form.vat_frequency || null,
      has_employees: form.has_employees === '' ? null : form.has_employees === 'true',
      obligation_type: form.obligation_type,
      description: form.description,
      is_active: true,
    };
    setRules([...rules, newRule]);
    setShowForm(false);
    setForm({ subject_type: '', vat_payer: '', vat_frequency: '', has_employees: '', obligation_type: '', description: '' });
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Mapovací pravidla</h1>
          <p className="text-sm text-gray-500 mt-1">Pravidla pro přiřazení povinností klientům dle jejich profilu</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
          <Plus size={16} /> Přidat pravidlo
        </button>
      </div>

      {showForm && (
        <div className="mb-6 bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Nové pravidlo</h2>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Typ subjektu</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" value={form.subject_type} onChange={(e) => setForm({ ...form, subject_type: e.target.value })}>
                <option value="">Libovolný</option><option value="osvc">OSVČ</option><option value="sro">s.r.o.</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Plátce DPH</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" value={form.vat_payer} onChange={(e) => setForm({ ...form, vat_payer: e.target.value })}>
                <option value="">Libovolný</option><option value="true">Ano</option><option value="false">Ne</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Frekvence DPH</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" value={form.vat_frequency} onChange={(e) => setForm({ ...form, vat_frequency: e.target.value })}>
                <option value="">Libovolná</option><option value="monthly">Měsíční</option><option value="quarterly">Čtvrtletní</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Má zaměstnance</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" value={form.has_employees} onChange={(e) => setForm({ ...form, has_employees: e.target.value })}>
                <option value="">Libovolný</option><option value="true">Ano</option><option value="false">Ne</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Typ povinnosti *</label>
              <input className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" value={form.obligation_type} onChange={(e) => setForm({ ...form, obligation_type: e.target.value })} placeholder="např. dph_mesicni" />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Popis</label>
              <input className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Popis pravidla" />
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={addRule} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm" disabled={!form.obligation_type}>Uložit</button>
            <button onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm">Zrušit</button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Typ subjektu</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">DPH</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Frekvence</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Zaměstnanci</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Typ povinnosti</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Popis</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">Aktivní</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {rules.map((r) => (
              <tr key={r.id} className={`border-b border-gray-50 ${!r.is_active ? 'opacity-50' : ''}`}>
                <td className="px-4 py-3">{r.subject_type ? (r.subject_type === 'osvc' ? 'OSVČ' : 's.r.o.') : '—'}</td>
                <td className="px-4 py-3">{r.vat_payer === null ? '—' : r.vat_payer ? 'Ano' : 'Ne'}</td>
                <td className="px-4 py-3">{r.vat_frequency || '—'}</td>
                <td className="px-4 py-3">{r.has_employees === null ? '—' : r.has_employees ? 'Ano' : 'Ne'}</td>
                <td className="px-4 py-3">
                  <span className="inline-flex px-2 py-0.5 rounded text-xs bg-blue-50 text-blue-700">{typeLabels[r.obligation_type] || r.obligation_type}</span>
                </td>
                <td className="px-4 py-3 text-gray-600 text-xs">{r.description || '—'}</td>
                <td className="px-4 py-3">
                  <button onClick={() => toggleRule(r.id)} className="text-gray-500 hover:text-blue-600">
                    {r.is_active ? <ToggleRight size={20} className="text-green-600" /> : <ToggleLeft size={20} />}
                  </button>
                </td>
                <td className="px-4 py-3">
                  <button onClick={() => deleteRule(r.id)} className="text-gray-400 hover:text-red-600"><Trash2 size={14} /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
