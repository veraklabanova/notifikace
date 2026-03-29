interface Props {
  status: string;
  size?: 'sm' | 'md';
}

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  suspended: 'bg-yellow-100 text-yellow-800',
  terminated: 'bg-red-100 text-red-800',
  upcoming: 'bg-blue-100 text-blue-800',
  notified: 'bg-purple-100 text-purple-800',
  past_due: 'bg-red-100 text-red-800',
  scheduled: 'bg-yellow-100 text-yellow-800',
  sent: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800',
  success: 'bg-green-100 text-green-800',
  never: 'bg-gray-100 text-gray-800',
};

const statusLabels: Record<string, string> = {
  active: 'Aktivní',
  suspended: 'Pozastaven',
  terminated: 'Ukončen',
  upcoming: 'Nadcházející',
  notified: 'Notifikováno',
  past_due: 'Po termínu',
  scheduled: 'Naplánováno',
  sent: 'Odesláno',
  error: 'Chyba',
  success: 'OK',
  never: 'Nikdy',
  '30day': '30 dní',
  '7day': '7 dní',
};

export default function StatusBadge({ status, size = 'sm' }: Props) {
  const color = statusColors[status] || 'bg-gray-100 text-gray-800';
  const label = statusLabels[status] || status;
  const sizeClass = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${color} ${sizeClass}`}>
      {label}
    </span>
  );
}
