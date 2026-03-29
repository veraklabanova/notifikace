# Systém automatizovaných daňových notifikací

MVP prototyp systému pro automatické upozorňování klientů účetní firmy na jejich daňové a odvodové povinnosti.

## Architektura

Systém se skládá z 5 modulů:

- **M1 — Helios Sync**: Synchronizace klientských dat (v prototypu seed data)
- **M2 — Client Profiling**: Mapování profilu klienta na sadu povinností dle konfigurovatelných pravidel
- **M3 — Obligation Calendar Engine**: Import daňového kalendáře z MFČR Open Data s fallbackem
- **M4 — Notification Engine**: E-mailové notifikace s předstihy 30 a 7 dní, idempotentní logika
- **M5 — Admin Dashboard**: React dashboard pro účetní firmu

## Tech stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **E-mail**: SMTP (mock režim v dev — loguje do konzole)

## Spuštění

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend poběží na `http://localhost:8000`. Při prvním spuštění se automaticky:
- vytvoří SQLite databáze
- naplní seed data (10 klientů, mapovací pravidla, daňový kalendář 2026)
- přepočítají povinnosti klientů

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend poběží na `http://localhost:5173` s proxy na backend.

## API endpointy

| Endpoint | Popis |
|----------|-------|
| `GET /api/dashboard/stats` | Statistiky dashboardu |
| `GET /api/dashboard/upcoming` | Nadcházející povinnosti |
| `GET /api/clients` | Seznam klientů |
| `GET /api/clients/{id}/obligations` | Povinnosti klienta |
| `GET /api/calendar` | Daňový kalendář |
| `POST /api/calendar/import-mfcr` | Import z MFČR Open Data |
| `POST /api/calendar/compute-obligations` | Přepočet povinností |
| `GET /api/notifications` | Log notifikací |
| `POST /api/notifications/run-cycle` | Spustit notifikační cyklus |
| `GET /api/rules` | Mapovací pravidla |
| `POST /api/rules` | Přidat pravidlo |

Kompletní API dokumentace: `http://localhost:8000/docs`

## Konfigurace e-mailu (volitelné)

Pro reálné odesílání e-mailů nastavte proměnné prostředí:

```bash
export SMTP_HOST=smtp.example.com
export SMTP_PORT=587
export SMTP_USER=user@example.com
export SMTP_PASS=heslo
export SMTP_FROM=notifikace@ucetni-firma.cz
```

Bez těchto proměnných systém funguje v mock režimu — e-maily se logují do konzole.
