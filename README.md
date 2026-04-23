# Big Data Pipeline Monitor

Webová aplikace pro evidenci, spouštění a sledování datových pipeline nad datovými zdroji, včetně monitoringu běhů a upozornění na problémy.

> Školní projekt MSWA — simulace orchestrace a monitoringu (ne plná data platforma).

---

## Co aplikace dělá

- Eviduje **datasety** (zdroje dat) a **pipeline**
- Umožňuje **manuální spuštění pipeline** s simulací ETL kroků (Extract → Transform → Load)
- Sleduje **běhy** v reálném čase — stav, kroky, chyby, počet zpracovaných záznamů
- Spravuje **pravidla alertů** a automaticky vytváří alerty při selhání
- Poskytuje **dashboard** s přehledem celého systému

---

## Technologie

| Vrstva | Technologie |
|--------|-------------|
| Backend | Python 3, Flask 3 |
| Databáze | SQLite |
| Frontend | Vanilla HTML + CSS + JavaScript |

---

## Spuštění

```bash
# Klonování repozitáře
git clone https://github.com/nbobyleva0705-oss/pipeline-monitor.git
cd pipeline-monitor

# Vytvoření virtuálního prostředí
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / Mac

# Instalace závislostí
pip install -r requirements.txt

# Spuštění
python app.py
```

Aplikace běží na **http://localhost:5000**

---

## Struktura projektu

```
pipeline_monitor/
├── app.py              # Vstupní bod Flask aplikace
├── db.py               # Připojení k SQLite
├── routes/             # API endpointy (Blueprint)
├── services/           # Business logika
├── database/           # SQL schéma a seed data
└── frontend/           # HTML stránky + CSS + JS
```

---

## REST API

| Metoda | Endpoint | Popis |
|--------|----------|-------|
| GET | `/api/summary` | Dashboard statistiky |
| GET / POST | `/datasets/` | Seznam / vytvoření datasetu |
| GET / POST | `/pipelines/` | Seznam / vytvoření pipeline |
| PATCH | `/pipelines/:id` | Aktivace / deaktivace pipeline |
| POST | `/pipelines/:id/run` | Spuštění pipeline |
| GET / PATCH | `/runs/:id` | Detail / aktualizace běhu |
| GET / POST | `/alert-rules/` | Pravidla alertů |
| GET | `/alerts/` | Seznam alertů |

---

## Ukázka simulace ETL

Po spuštění pipeline se v pozadí (Python thread) provede simulace tří kroků:

```
Extract ──► Transform ──► Load
```

- S pravděpodobností **30 %** jeden krok selže → run = `failed` + automatický alert
- Při úspěchu se zaznamená 5 000–200 000 zpracovaných záznamů
- Průběh kroků je viditelný v reálném čase na stránce **Runs**
