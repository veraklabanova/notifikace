// Embedded mock data — no API calls needed, instant load

export interface Client {
  id: number;
  name: string;
  ico: string;
  subject_type: 'osvc' | 'sro';
  vat_payer: boolean;
  vat_frequency: 'monthly' | 'quarterly' | null;
  has_employees: boolean;
  email: string;
  status: 'active' | 'suspended' | 'terminated';
  obligations_count: number;
  upcoming_count: number;
}

export interface CalendarEntry {
  id: number;
  title: string;
  description: string;
  obligation_type: string;
  deadline_date: string;
  source: string;
}

export interface Obligation {
  id: number;
  client_id: number;
  title: string;
  description: string;
  obligation_type: string;
  deadline_date: string;
  status: 'upcoming' | 'notified' | 'past_due';
}

export interface NotificationItem {
  id: number;
  client_name: string;
  client_id: number;
  obligation_title: string;
  deadline_date: string;
  notification_type: '30day' | '7day';
  status: 'scheduled' | 'sent' | 'error';
  email_to: string;
  subject: string;
  sent_at: string | null;
  error_message: string | null;
  created_at: string;
}

export interface MappingRule {
  id: number;
  subject_type: string | null;
  vat_payer: boolean | null;
  vat_frequency: string | null;
  has_employees: boolean | null;
  obligation_type: string;
  description: string;
  is_active: boolean;
}

export interface UpcomingObligation {
  id: number;
  client_name: string;
  client_id: number;
  title: string;
  deadline_date: string;
  days_remaining: number;
  status: string;
  obligation_type: string;
}

// --- Helpers ---
const today = new Date();
const fmt = (d: Date) => d.toISOString().split('T')[0];
const addDays = (d: Date, n: number) => { const r = new Date(d); r.setDate(r.getDate() + n); return r; };
const fmtDt = (d: Date) => d.toISOString();

// --- Clients ---
export const clients: Client[] = [
  { id: 1, name: "Jan Novák", ico: "12345678", subject_type: "osvc", vat_payer: true, vat_frequency: "monthly", has_employees: false, email: "jan.novak@example.com", status: "active", obligations_count: 28, upcoming_count: 14 },
  { id: 2, name: "Eva Svobodová", ico: "23456789", subject_type: "osvc", vat_payer: false, vat_frequency: null, has_employees: false, email: "eva.svobodova@example.com", status: "active", obligations_count: 4, upcoming_count: 3 },
  { id: 3, name: "TechSoft s.r.o.", ico: "34567890", subject_type: "sro", vat_payer: true, vat_frequency: "monthly", has_employees: true, email: "info@techsoft.cz", status: "active", obligations_count: 42, upcoming_count: 22 },
  { id: 4, name: "Petr Dvořák", ico: "45678901", subject_type: "osvc", vat_payer: true, vat_frequency: "quarterly", has_employees: true, email: "petr.dvorak@example.com", status: "active", obligations_count: 24, upcoming_count: 12 },
  { id: 5, name: "DesignStudio s.r.o.", ico: "56789012", subject_type: "sro", vat_payer: true, vat_frequency: "quarterly", has_employees: true, email: "office@designstudio.cz", status: "active", obligations_count: 30, upcoming_count: 16 },
  { id: 6, name: "Marie Černá", ico: "67890123", subject_type: "osvc", vat_payer: false, vat_frequency: null, has_employees: false, email: "marie.cerna@example.com", status: "suspended", obligations_count: 0, upcoming_count: 0 },
  { id: 7, name: "GreenGarden s.r.o.", ico: "78901234", subject_type: "sro", vat_payer: false, vat_frequency: null, has_employees: true, email: "info@greengarden.cz", status: "active", obligations_count: 16, upcoming_count: 8 },
  { id: 8, name: "Tomáš Horák", ico: "89012345", subject_type: "osvc", vat_payer: true, vat_frequency: "monthly", has_employees: true, email: "tomas.horak@example.com", status: "active", obligations_count: 38, upcoming_count: 20 },
  { id: 9, name: "FastBuild s.r.o.", ico: "90123456", subject_type: "sro", vat_payer: true, vat_frequency: "monthly", has_employees: true, email: "info@fastbuild.cz", status: "active", obligations_count: 42, upcoming_count: 22 },
  { id: 10, name: "Lucie Králová", ico: "01234567", subject_type: "osvc", vat_payer: false, vat_frequency: null, has_employees: false, email: "lucie.kralova@example.com", status: "terminated", obligations_count: 0, upcoming_count: 0 },
];

// --- Calendar ---
function generateCalendar(): CalendarEntry[] {
  const entries: CalendarEntry[] = [];
  let id = 1;

  const vatMonths = [
    ["leden", 2, 25], ["únor", 3, 25], ["březen", 4, 27], ["duben", 5, 25],
    ["květen", 6, 25], ["červen", 7, 27], ["červenec", 8, 25], ["srpen", 9, 25],
    ["září", 10, 26], ["říjen", 11, 25], ["listopad", 12, 28],
  ] as const;

  for (const [name, m, d] of vatMonths) {
    entries.push({ id: id++, title: `DPH — přiznání za ${name} 2026`, obligation_type: "dph_mesicni", deadline_date: `2026-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`, description: `Podání přiznání k DPH za ${name} 2026`, source: "fallback" });
    entries.push({ id: id++, title: `Kontrolní hlášení — ${name} 2026`, obligation_type: "kontrolni_hlaseni_mesicni", deadline_date: `2026-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`, description: `Kontrolní hlášení k DPH za ${name} 2026`, source: "fallback" });
  }
  entries.push({ id: id++, title: "DPH — přiznání za prosinec 2026", obligation_type: "dph_mesicni", deadline_date: "2027-01-25", description: "Podání přiznání k DPH za prosinec 2026", source: "fallback" });
  entries.push({ id: id++, title: "Kontrolní hlášení — prosinec 2026", obligation_type: "kontrolni_hlaseni_mesicni", deadline_date: "2027-01-25", description: "Kontrolní hlášení k DPH za prosinec 2026", source: "fallback" });

  for (const [q, m, d] of [["Q1", 4, 27], ["Q2", 7, 27], ["Q3", 10, 26]] as const) {
    entries.push({ id: id++, title: `DPH — přiznání za ${q} 2026`, obligation_type: "dph_ctvrtletni", deadline_date: `2026-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`, description: `Přiznání k DPH za ${q} 2026`, source: "fallback" });
    entries.push({ id: id++, title: `Kontrolní hlášení — ${q} 2026`, obligation_type: "kontrolni_hlaseni_ctvrtletni", deadline_date: `2026-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`, description: `Kontrolní hlášení za ${q} 2026`, source: "fallback" });
  }
  entries.push({ id: id++, title: "DPH — přiznání za Q4 2026", obligation_type: "dph_ctvrtletni", deadline_date: "2027-01-25", description: "Přiznání k DPH za Q4 2026", source: "fallback" });
  entries.push({ id: id++, title: "Kontrolní hlášení — Q4 2026", obligation_type: "kontrolni_hlaseni_ctvrtletni", deadline_date: "2027-01-25", description: "Kontrolní hlášení za Q4 2026", source: "fallback" });

  entries.push({ id: id++, title: "Daň z příjmů FO — přiznání 2025", obligation_type: "dpfo", deadline_date: "2026-04-01", description: "Přiznání DPFO za 2025 (papírové)", source: "fallback" });
  entries.push({ id: id++, title: "Daň z příjmů FO — elektronické 2025", obligation_type: "dpfo", deadline_date: "2026-05-04", description: "Přiznání DPFO za 2025 (elektronicky)", source: "fallback" });
  entries.push({ id: id++, title: "Daň z příjmů PO — přiznání 2025", obligation_type: "dppo", deadline_date: "2026-04-01", description: "Přiznání DPPO za 2025", source: "fallback" });
  entries.push({ id: id++, title: "Daň z příjmů PO — elektronické 2025", obligation_type: "dppo", deadline_date: "2026-05-04", description: "Přiznání DPPO za 2025 (elektronicky)", source: "fallback" });
  entries.push({ id: id++, title: "Přehled OSVČ — ČSSZ za 2025", obligation_type: "socialni_osvc", deadline_date: "2026-05-04", description: "Přehled příjmů a výdajů OSVČ — ČSSZ", source: "fallback" });
  entries.push({ id: id++, title: "Přehled OSVČ — ZP za 2025", obligation_type: "zdravotni_osvc", deadline_date: "2026-05-04", description: "Přehled OSVČ — zdravotní pojišťovna", source: "fallback" });

  const empMonths = [
    ["leden", 2, 20], ["únor", 3, 20], ["březen", 4, 20], ["duben", 5, 20],
    ["květen", 6, 22], ["červen", 7, 20], ["červenec", 8, 20], ["srpen", 9, 21],
    ["září", 10, 20], ["říjen", 11, 20], ["listopad", 12, 21],
  ] as const;
  for (const [name, m, d] of empMonths) {
    entries.push({ id: id++, title: `Odvody za zaměstnance — ${name} 2026`, obligation_type: "zamestnanci_mesicni", deadline_date: `2026-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`, description: `SP, ZP a záloha daně za ${name} 2026`, source: "fallback" });
  }
  entries.push({ id: id++, title: "Odvody za zaměstnance — prosinec 2026", obligation_type: "zamestnanci_mesicni", deadline_date: "2027-01-20", description: "SP, ZP a záloha daně za prosinec 2026", source: "fallback" });
  entries.push({ id: id++, title: "Vyúčtování daně ze závislé činnosti 2025", obligation_type: "zamestnanci_rocni", deadline_date: "2026-03-02", description: "Roční vyúčtování za 2025", source: "fallback" });
  entries.push({ id: id++, title: "Silniční daň — přiznání za 2025", obligation_type: "silnicni_dan", deadline_date: "2026-01-31", description: "Přiznání a platba silniční daně za 2025", source: "fallback" });

  return entries.sort((a, b) => a.deadline_date.localeCompare(b.deadline_date));
}

export const calendarEntries = generateCalendar();

// --- Mapping Rules ---
export const mappingRules: MappingRule[] = [
  { id: 1, subject_type: null, vat_payer: true, vat_frequency: "monthly", has_employees: null, obligation_type: "dph_mesicni", description: "Přiznání k DPH — měsíční plátce", is_active: true },
  { id: 2, subject_type: null, vat_payer: true, vat_frequency: "quarterly", has_employees: null, obligation_type: "dph_ctvrtletni", description: "Přiznání k DPH — čtvrtletní plátce", is_active: true },
  { id: 3, subject_type: "sro", vat_payer: true, vat_frequency: null, has_employees: null, obligation_type: "kontrolni_hlaseni_mesicni", description: "Kontrolní hlášení — s.r.o. (měsíčně)", is_active: true },
  { id: 4, subject_type: "osvc", vat_payer: true, vat_frequency: "monthly", has_employees: null, obligation_type: "kontrolni_hlaseni_mesicni", description: "Kontrolní hlášení — OSVČ měsíční", is_active: true },
  { id: 5, subject_type: "osvc", vat_payer: true, vat_frequency: "quarterly", has_employees: null, obligation_type: "kontrolni_hlaseni_ctvrtletni", description: "Kontrolní hlášení — OSVČ čtvrtletní", is_active: true },
  { id: 6, subject_type: "osvc", vat_payer: null, vat_frequency: null, has_employees: null, obligation_type: "dpfo", description: "Daň z příjmů fyzických osob (OSVČ)", is_active: true },
  { id: 7, subject_type: "sro", vat_payer: null, vat_frequency: null, has_employees: null, obligation_type: "dppo", description: "Daň z příjmů právnických osob (s.r.o.)", is_active: true },
  { id: 8, subject_type: "osvc", vat_payer: null, vat_frequency: null, has_employees: null, obligation_type: "socialni_osvc", description: "Přehled OSVČ — ČSSZ", is_active: true },
  { id: 9, subject_type: "osvc", vat_payer: null, vat_frequency: null, has_employees: null, obligation_type: "zdravotni_osvc", description: "Přehled OSVČ — zdravotní pojišťovna", is_active: true },
  { id: 10, subject_type: null, vat_payer: null, vat_frequency: null, has_employees: true, obligation_type: "zamestnanci_mesicni", description: "Měsíční odvody za zaměstnance", is_active: true },
  { id: 11, subject_type: null, vat_payer: null, vat_frequency: null, has_employees: true, obligation_type: "zamestnanci_rocni", description: "Roční vyúčtování daně ze závislé činnosti", is_active: true },
  { id: 12, subject_type: null, vat_payer: null, vat_frequency: null, has_employees: null, obligation_type: "silnicni_dan", description: "Silniční daň", is_active: true },
];

// --- Compute obligations per client ---
function matchRule(client: Client, rule: MappingRule): boolean {
  if (rule.subject_type && rule.subject_type !== client.subject_type) return false;
  if (rule.vat_payer !== null && rule.vat_payer !== client.vat_payer) return false;
  if (rule.vat_frequency && rule.vat_frequency !== client.vat_frequency) return false;
  if (rule.has_employees !== null && rule.has_employees !== client.has_employees) return false;
  return true;
}

function computeObligations(): Obligation[] {
  const obligations: Obligation[] = [];
  let id = 1;
  const todayStr = fmt(today);

  for (const client of clients.filter(c => c.status === 'active')) {
    const matchedTypes = new Set(
      mappingRules.filter(r => r.is_active && matchRule(client, r)).map(r => r.obligation_type)
    );
    for (const entry of calendarEntries) {
      if (matchedTypes.has(entry.obligation_type)) {
        let status: Obligation['status'] = 'upcoming';
        if (entry.deadline_date < todayStr) status = 'past_due';
        else {
          const daysUntil = Math.ceil((new Date(entry.deadline_date).getTime() - today.getTime()) / 86400000);
          if (daysUntil <= 30) status = 'notified';
        }
        obligations.push({
          id: id++, client_id: client.id,
          title: entry.title, description: entry.description,
          obligation_type: entry.obligation_type,
          deadline_date: entry.deadline_date, status,
        });
      }
    }
  }
  return obligations;
}

export const allObligations = computeObligations();

// --- Generate notifications ---
function generateNotifications(): NotificationItem[] {
  const notifications: NotificationItem[] = [];
  let id = 1;
  const todayStr = fmt(today);

  for (const ob of allObligations) {
    if (ob.deadline_date < todayStr) continue;
    const client = clients.find(c => c.id === ob.client_id)!;
    const daysUntil = Math.ceil((new Date(ob.deadline_date).getTime() - today.getTime()) / 86400000);

    if (daysUntil <= 30) {
      notifications.push({
        id: id++, client_name: client.name, client_id: client.id,
        obligation_title: ob.title, deadline_date: ob.deadline_date,
        notification_type: '30day', status: 'sent',
        email_to: client.email, subject: `Upozornění (30 dní): ${ob.title}`,
        sent_at: fmtDt(addDays(new Date(ob.deadline_date), -30)),
        error_message: null, created_at: fmtDt(addDays(new Date(ob.deadline_date), -30)),
      });
    }
    if (daysUntil <= 7) {
      notifications.push({
        id: id++, client_name: client.name, client_id: client.id,
        obligation_title: ob.title, deadline_date: ob.deadline_date,
        notification_type: '7day', status: daysUntil <= 2 ? 'error' : 'sent',
        email_to: client.email, subject: `Urgentní upozornění (7 dní): ${ob.title}`,
        sent_at: daysUntil <= 2 ? null : fmtDt(addDays(new Date(ob.deadline_date), -7)),
        error_message: daysUntil <= 2 ? 'SMTP timeout — connection refused' : null,
        created_at: fmtDt(addDays(new Date(ob.deadline_date), -7)),
      });
    }
  }
  return notifications.sort((a, b) => b.created_at.localeCompare(a.created_at));
}

export const allNotifications = generateNotifications();

// --- Upcoming obligations ---
export function getUpcoming(days: number): UpcomingObligation[] {
  const todayStr = fmt(today);
  const cutoff = fmt(addDays(today, days));
  return allObligations
    .filter(o => o.deadline_date >= todayStr && o.deadline_date <= cutoff)
    .map(o => ({
      id: o.id, client_name: clients.find(c => c.id === o.client_id)!.name,
      client_id: o.client_id, title: o.title, deadline_date: o.deadline_date,
      days_remaining: Math.ceil((new Date(o.deadline_date).getTime() - today.getTime()) / 86400000),
      status: o.status, obligation_type: o.obligation_type,
    }))
    .sort((a, b) => a.deadline_date.localeCompare(b.deadline_date));
}

// --- Stats ---
export function getStats() {
  const active = clients.filter(c => c.status === 'active').length;
  const todayStr = fmt(today);
  const next7 = fmt(addDays(today, 7));
  const upcoming = allObligations.filter(o => o.status === 'upcoming' && o.deadline_date >= todayStr).length;
  const urgent = allObligations.filter(o => o.deadline_date >= todayStr && o.deadline_date <= next7).length;
  const sent = allNotifications.filter(n => n.status === 'sent').length;
  const errors = allNotifications.filter(n => n.status === 'error').length;

  return {
    clients: { total: clients.length, active, suspended: clients.filter(c => c.status === 'suspended').length },
    obligations: { total: allObligations.length, upcoming, urgent_7_days: urgent },
    notifications: { total: allNotifications.length, sent, errors, pending: 0 },
    calendar: { entries: calendarEntries.length },
    imports: { mfcr_last: fmtDt(addDays(today, -2)), mfcr_status: "fallback", helios_last: fmtDt(addDays(today, -1)), helios_status: "success" },
  };
}

// --- Obligation types ---
export const obligationTypes = [...new Set(calendarEntries.map(e => e.obligation_type))];
