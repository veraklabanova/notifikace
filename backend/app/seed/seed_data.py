from datetime import date
from sqlalchemy.orm import Session
from ..models import (
    Client, CalendarEntry, MappingRule, SubjectType, VatFrequency, ClientStatus
)


SEED_CLIENTS = [
    {
        "name": "Jan Novák",
        "ico": "12345678",
        "subject_type": SubjectType.OSVC,
        "vat_payer": True,
        "vat_frequency": VatFrequency.MONTHLY,
        "has_employees": False,
        "email": "jan.novak@example.com",
        "status": ClientStatus.ACTIVE,
    },
    {
        "name": "Eva Svobodová",
        "ico": "23456789",
        "subject_type": SubjectType.OSVC,
        "vat_payer": False,
        "vat_frequency": None,
        "has_employees": False,
        "email": "eva.svobodova@example.com",
        "status": ClientStatus.ACTIVE,
    },
    {
        "name": "TechSoft s.r.o.",
        "ico": "34567890",
        "subject_type": SubjectType.SRO,
        "vat_payer": True,
        "vat_frequency": VatFrequency.MONTHLY,
        "has_employees": True,
        "email": "info@techsoft.cz",
        "status": ClientStatus.ACTIVE,
    },
    {
        "name": "Petr Dvořák",
        "ico": "45678901",
        "subject_type": SubjectType.OSVC,
        "vat_payer": True,
        "vat_frequency": VatFrequency.QUARTERLY,
        "has_employees": True,
        "email": "petr.dvorak@example.com",
        "status": ClientStatus.ACTIVE,
    },
    {
        "name": "DesignStudio s.r.o.",
        "ico": "56789012",
        "subject_type": SubjectType.SRO,
        "vat_payer": True,
        "vat_frequency": VatFrequency.QUARTERLY,
        "has_employees": True,
        "email": "office@designstudio.cz",
        "status": ClientStatus.ACTIVE,
    },
    {
        "name": "Marie Černá",
        "ico": "67890123",
        "subject_type": SubjectType.OSVC,
        "vat_payer": False,
        "vat_frequency": None,
        "has_employees": False,
        "email": "marie.cerna@example.com",
        "status": ClientStatus.SUSPENDED,
    },
    {
        "name": "GreenGarden s.r.o.",
        "ico": "78901234",
        "subject_type": SubjectType.SRO,
        "vat_payer": False,
        "vat_frequency": None,
        "has_employees": True,
        "email": "info@greengarden.cz",
        "status": ClientStatus.ACTIVE,
    },
    {
        "name": "Tomáš Horák",
        "ico": "89012345",
        "subject_type": SubjectType.OSVC,
        "vat_payer": True,
        "vat_frequency": VatFrequency.MONTHLY,
        "has_employees": True,
        "email": "tomas.horak@example.com",
        "status": ClientStatus.ACTIVE,
    },
    {
        "name": "FastBuild s.r.o.",
        "ico": "90123456",
        "subject_type": SubjectType.SRO,
        "vat_payer": True,
        "vat_frequency": VatFrequency.MONTHLY,
        "has_employees": True,
        "email": "info@fastbuild.cz",
        "status": ClientStatus.ACTIVE,
    },
    {
        "name": "Lucie Králová",
        "ico": "01234567",
        "subject_type": SubjectType.OSVC,
        "vat_payer": False,
        "vat_frequency": None,
        "has_employees": False,
        "email": "lucie.kralova@example.com",
        "status": ClientStatus.TERMINATED,
    },
]

SEED_MAPPING_RULES = [
    # DPH - mesicni
    {"subject_type": None, "vat_payer": True, "vat_frequency": "monthly", "has_employees": None,
     "obligation_type": "dph_mesicni", "description": "Přiznání k DPH — měsíční plátce"},
    # DPH - ctvrtletni
    {"subject_type": None, "vat_payer": True, "vat_frequency": "quarterly", "has_employees": None,
     "obligation_type": "dph_ctvrtletni", "description": "Přiznání k DPH — čtvrtletní plátce"},
    # Kontrolni hlaseni - mesicni (s.r.o. vzdy mesicne)
    {"subject_type": "sro", "vat_payer": True, "vat_frequency": None, "has_employees": None,
     "obligation_type": "kontrolni_hlaseni_mesicni", "description": "Kontrolní hlášení — s.r.o. (měsíčně)"},
    # Kontrolni hlaseni - OSVC dle frekvence DPH
    {"subject_type": "osvc", "vat_payer": True, "vat_frequency": "monthly", "has_employees": None,
     "obligation_type": "kontrolni_hlaseni_mesicni", "description": "Kontrolní hlášení — OSVČ měsíční plátce"},
    {"subject_type": "osvc", "vat_payer": True, "vat_frequency": "quarterly", "has_employees": None,
     "obligation_type": "kontrolni_hlaseni_ctvrtletni", "description": "Kontrolní hlášení — OSVČ čtvrtletní plátce"},
    # Dan z prijmu FO
    {"subject_type": "osvc", "vat_payer": None, "vat_frequency": None, "has_employees": None,
     "obligation_type": "dpfo", "description": "Daň z příjmů fyzických osob (OSVČ)"},
    # Dan z prijmu PO
    {"subject_type": "sro", "vat_payer": None, "vat_frequency": None, "has_employees": None,
     "obligation_type": "dppo", "description": "Daň z příjmů právnických osob (s.r.o.)"},
    # Socialni pojisteni OSVC
    {"subject_type": "osvc", "vat_payer": None, "vat_frequency": None, "has_employees": None,
     "obligation_type": "socialni_osvc", "description": "Přehled o příjmech a výdajích OSVČ — ČSSZ"},
    # Zdravotni pojisteni OSVC
    {"subject_type": "osvc", "vat_payer": None, "vat_frequency": None, "has_employees": None,
     "obligation_type": "zdravotni_osvc", "description": "Přehled OSVČ — zdravotní pojišťovna"},
    # Zamestnavatel - mesicni povinnosti
    {"subject_type": None, "vat_payer": None, "vat_frequency": None, "has_employees": True,
     "obligation_type": "zamestnanci_mesicni", "description": "Měsíční odvody za zaměstnance (SP, ZP, záloha daně)"},
    # Zamestnavatel - rocni
    {"subject_type": None, "vat_payer": None, "vat_frequency": None, "has_employees": True,
     "obligation_type": "zamestnanci_rocni", "description": "Roční vyúčtování daně ze závislé činnosti"},
    # Silnicni dan
    {"subject_type": None, "vat_payer": None, "vat_frequency": None, "has_employees": None,
     "obligation_type": "silnicni_dan", "description": "Silniční daň — přiznání a platba"},
]

# Fallback danovy kalendar 2026
FALLBACK_CALENDAR_2026 = [
    # DPH mesicni - kazdy 25. nasledujiciho mesice
    {"title": "DPH — přiznání za leden 2026", "obligation_type": "dph_mesicni",
     "deadline_date": date(2026, 2, 25), "description": "Podání přiznání k DPH a platba za leden 2026"},
    {"title": "DPH — přiznání za únor 2026", "obligation_type": "dph_mesicni",
     "deadline_date": date(2026, 3, 25), "description": "Podání přiznání k DPH a platba za únor 2026"},
    {"title": "DPH — přiznání za březen 2026", "obligation_type": "dph_mesicni",
     "deadline_date": date(2026, 4, 27), "description": "Podání přiznání k DPH a platba za březen 2026"},
    {"title": "DPH — přiznání za duben 2026", "obligation_type": "dph_mesicni",
     "deadline_date": date(2026, 5, 25), "description": "Podání přiznání k DPH a platba za duben 2026"},
    {"title": "DPH — přiznání za květen 2026", "obligation_type": "dph_mesicni",
     "deadline_date": date(2026, 6, 25), "description": "Podání přiznání k DPH a platba za květen 2026"},
    {"title": "DPH — přiznání za červen 2026", "obligation_type": "dph_mesicni",
     "deadline_date": date(2026, 7, 27), "description": "Podání přiznání k DPH a platba za červen 2026"},
    {"title": "DPH — přiznání za červenec 2026", "obligation_type": "dph_mesicni",
     "deadline_date": date(2026, 8, 25), "description": "Podání přiznání k DPH a platba za červenec 2026"},
    {"title": "DPH — přiznání za srpen 2026", "obligation_type": "dph_mesicni",
     "deadline_date": date(2026, 9, 25), "description": "Podání přiznání k DPH a platba za srpen 2026"},
    {"title": "DPH — přiznání za září 2026", "obligation_type": "dph_mesicni",
     "deadline_date": date(2026, 10, 26), "description": "Podání přiznání k DPH a platba za září 2026"},
    {"title": "DPH — přiznání za říjen 2026", "obligation_type": "dph_mesicni",
     "deadline_date": date(2026, 11, 25), "description": "Podání přiznání k DPH a platba za říjen 2026"},
    {"title": "DPH — přiznání za listopad 2026", "obligation_type": "dph_mesicni",
     "deadline_date": date(2026, 12, 28), "description": "Podání přiznání k DPH a platba za listopad 2026"},
    {"title": "DPH — přiznání za prosinec 2026", "obligation_type": "dph_mesicni",
     "deadline_date": date(2027, 1, 25), "description": "Podání přiznání k DPH a platba za prosinec 2026"},

    # DPH ctvrtletni
    {"title": "DPH — přiznání za Q1 2026", "obligation_type": "dph_ctvrtletni",
     "deadline_date": date(2026, 4, 27), "description": "Podání přiznání k DPH a platba za 1. čtvrtletí 2026"},
    {"title": "DPH — přiznání za Q2 2026", "obligation_type": "dph_ctvrtletni",
     "deadline_date": date(2026, 7, 27), "description": "Podání přiznání k DPH a platba za 2. čtvrtletí 2026"},
    {"title": "DPH — přiznání za Q3 2026", "obligation_type": "dph_ctvrtletni",
     "deadline_date": date(2026, 10, 26), "description": "Podání přiznání k DPH a platba za 3. čtvrtletí 2026"},
    {"title": "DPH — přiznání za Q4 2026", "obligation_type": "dph_ctvrtletni",
     "deadline_date": date(2027, 1, 25), "description": "Podání přiznání k DPH a platba za 4. čtvrtletí 2026"},

    # Kontrolni hlaseni - mesicni (shodne s DPH mesicni terminy)
    {"title": "Kontrolní hlášení — leden 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
     "deadline_date": date(2026, 2, 25), "description": "Kontrolní hlášení k DPH za leden 2026"},
    {"title": "Kontrolní hlášení — únor 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
     "deadline_date": date(2026, 3, 25), "description": "Kontrolní hlášení k DPH za únor 2026"},
    {"title": "Kontrolní hlášení — březen 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
     "deadline_date": date(2026, 4, 27), "description": "Kontrolní hlášení k DPH za březen 2026"},
    {"title": "Kontrolní hlášení — duben 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
     "deadline_date": date(2026, 5, 25), "description": "Kontrolní hlášení k DPH za duben 2026"},
    {"title": "Kontrolní hlášení — květen 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
     "deadline_date": date(2026, 6, 25), "description": "Kontrolní hlášení k DPH za květen 2026"},
    {"title": "Kontrolní hlášení — červen 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
     "deadline_date": date(2026, 7, 27), "description": "Kontrolní hlášení k DPH za červen 2026"},
    {"title": "Kontrolní hlášení — červenec 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
     "deadline_date": date(2026, 8, 25), "description": "Kontrolní hlášení k DPH za červenec 2026"},
    {"title": "Kontrolní hlášení — srpen 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
     "deadline_date": date(2026, 9, 25), "description": "Kontrolní hlášení k DPH za srpen 2026"},
    {"title": "Kontrolní hlášení — září 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
     "deadline_date": date(2026, 10, 26), "description": "Kontrolní hlášení k DPH za září 2026"},
    {"title": "Kontrolní hlášení — říjen 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
     "deadline_date": date(2026, 11, 25), "description": "Kontrolní hlášení k DPH za říjen 2026"},
    {"title": "Kontrolní hlášení — listopad 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
     "deadline_date": date(2026, 12, 28), "description": "Kontrolní hlášení k DPH za listopad 2026"},
    {"title": "Kontrolní hlášení — prosinec 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
     "deadline_date": date(2027, 1, 25), "description": "Kontrolní hlášení k DPH za prosinec 2026"},

    # Kontrolni hlaseni - ctvrtletni
    {"title": "Kontrolní hlášení — Q1 2026", "obligation_type": "kontrolni_hlaseni_ctvrtletni",
     "deadline_date": date(2026, 4, 27), "description": "Kontrolní hlášení k DPH za 1. čtvrtletí 2026"},
    {"title": "Kontrolní hlášení — Q2 2026", "obligation_type": "kontrolni_hlaseni_ctvrtletni",
     "deadline_date": date(2026, 7, 27), "description": "Kontrolní hlášení k DPH za 2. čtvrtletí 2026"},
    {"title": "Kontrolní hlášení — Q3 2026", "obligation_type": "kontrolni_hlaseni_ctvrtletni",
     "deadline_date": date(2026, 10, 26), "description": "Kontrolní hlášení k DPH za 3. čtvrtletí 2026"},
    {"title": "Kontrolní hlášení — Q4 2026", "obligation_type": "kontrolni_hlaseni_ctvrtletni",
     "deadline_date": date(2027, 1, 25), "description": "Kontrolní hlášení k DPH za 4. čtvrtletí 2026"},

    # Dan z prijmu FO - OSVC
    {"title": "Daň z příjmů FO — přiznání 2025", "obligation_type": "dpfo",
     "deadline_date": date(2026, 4, 1), "description": "Podání přiznání k dani z příjmů fyzických osob za rok 2025 (papírové)"},
    {"title": "Daň z příjmů FO — elektronické přiznání 2025", "obligation_type": "dpfo",
     "deadline_date": date(2026, 5, 4), "description": "Podání přiznání k dani z příjmů FO za 2025 (elektronicky)"},

    # Dan z prijmu PO - s.r.o.
    {"title": "Daň z příjmů PO — přiznání 2025", "obligation_type": "dppo",
     "deadline_date": date(2026, 4, 1), "description": "Podání přiznání k dani z příjmů právnických osob za rok 2025"},
    {"title": "Daň z příjmů PO — elektronické přiznání 2025", "obligation_type": "dppo",
     "deadline_date": date(2026, 5, 4), "description": "Podání přiznání k DPPO za 2025 (elektronicky)"},

    # Socialni pojisteni OSVC
    {"title": "Přehled OSVČ — ČSSZ za rok 2025", "obligation_type": "socialni_osvc",
     "deadline_date": date(2026, 5, 4), "description": "Podání přehledu o příjmech a výdajích OSVČ na ČSSZ za rok 2025"},

    # Zdravotni pojisteni OSVC
    {"title": "Přehled OSVČ — ZP za rok 2025", "obligation_type": "zdravotni_osvc",
     "deadline_date": date(2026, 5, 4), "description": "Podání přehledu OSVČ na zdravotní pojišťovnu za rok 2025"},

    # Zamestnavatel mesicni - odvody do 20. nasledujiciho mesice
    {"title": "Odvody za zaměstnance — leden 2026", "obligation_type": "zamestnanci_mesicni",
     "deadline_date": date(2026, 2, 20), "description": "Odvod SP, ZP a zálohy daně za zaměstnance za leden 2026"},
    {"title": "Odvody za zaměstnance — únor 2026", "obligation_type": "zamestnanci_mesicni",
     "deadline_date": date(2026, 3, 20), "description": "Odvod SP, ZP a zálohy daně za zaměstnance za únor 2026"},
    {"title": "Odvody za zaměstnance — březen 2026", "obligation_type": "zamestnanci_mesicni",
     "deadline_date": date(2026, 4, 20), "description": "Odvod SP, ZP a zálohy daně za zaměstnance za březen 2026"},
    {"title": "Odvody za zaměstnance — duben 2026", "obligation_type": "zamestnanci_mesicni",
     "deadline_date": date(2026, 5, 20), "description": "Odvod SP, ZP a zálohy daně za zaměstnance za duben 2026"},
    {"title": "Odvody za zaměstnance — květen 2026", "obligation_type": "zamestnanci_mesicni",
     "deadline_date": date(2026, 6, 22), "description": "Odvod SP, ZP a zálohy daně za zaměstnance za květen 2026"},
    {"title": "Odvody za zaměstnance — červen 2026", "obligation_type": "zamestnanci_mesicni",
     "deadline_date": date(2026, 7, 20), "description": "Odvod SP, ZP a zálohy daně za zaměstnance za červen 2026"},
    {"title": "Odvody za zaměstnance — červenec 2026", "obligation_type": "zamestnanci_mesicni",
     "deadline_date": date(2026, 8, 20), "description": "Odvod SP, ZP a zálohy daně za zaměstnance za červenec 2026"},
    {"title": "Odvody za zaměstnance — srpen 2026", "obligation_type": "zamestnanci_mesicni",
     "deadline_date": date(2026, 9, 21), "description": "Odvod SP, ZP a zálohy daně za zaměstnance za srpen 2026"},
    {"title": "Odvody za zaměstnance — září 2026", "obligation_type": "zamestnanci_mesicni",
     "deadline_date": date(2026, 10, 20), "description": "Odvod SP, ZP a zálohy daně za zaměstnance za září 2026"},
    {"title": "Odvody za zaměstnance — říjen 2026", "obligation_type": "zamestnanci_mesicni",
     "deadline_date": date(2026, 11, 20), "description": "Odvod SP, ZP a zálohy daně za zaměstnance za říjen 2026"},
    {"title": "Odvody za zaměstnance — listopad 2026", "obligation_type": "zamestnanci_mesicni",
     "deadline_date": date(2026, 12, 21), "description": "Odvod SP, ZP a zálohy daně za zaměstnance za listopad 2026"},
    {"title": "Odvody za zaměstnance — prosinec 2026", "obligation_type": "zamestnanci_mesicni",
     "deadline_date": date(2027, 1, 20), "description": "Odvod SP, ZP a zálohy daně za zaměstnance za prosinec 2026"},

    # Rocni vyuctovani zamestnavatele
    {"title": "Vyúčtování daně ze závislé činnosti 2025", "obligation_type": "zamestnanci_rocni",
     "deadline_date": date(2026, 3, 2), "description": "Roční vyúčtování daně ze závislé činnosti za rok 2025"},

    # Silnicni dan
    {"title": "Silniční daň — přiznání za rok 2025", "obligation_type": "silnicni_dan",
     "deadline_date": date(2026, 1, 31), "description": "Podání přiznání a platba silniční daně za rok 2025"},
]


def seed_database(db: Session):
    """Seed the database with initial data if empty."""
    if db.query(Client).count() > 0:
        return False

    # Seed clients
    for client_data in SEED_CLIENTS:
        db.add(Client(**client_data))

    # Seed mapping rules
    for rule_data in SEED_MAPPING_RULES:
        db.add(MappingRule(**rule_data))

    # Seed fallback calendar
    for entry_data in FALLBACK_CALENDAR_2026:
        db.add(CalendarEntry(
            title=entry_data["title"],
            description=entry_data["description"],
            obligation_type=entry_data["obligation_type"],
            deadline_date=entry_data["deadline_date"],
            source="fallback",
        ))

    db.commit()
    return True
