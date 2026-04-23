# Big Data Pipeline Monitor

Webová aplikace pro evidenci, spouštění a sledování datových pipeline nad datovými zdroji, včetně monitoringu běhů a upozornění na problémy.

> Školní projekt MSWA — simulace orchestrace a monitoringu (ne plná data platforma).

---

## Co aplikace dělá

- Eviduje **datasety** a **pipeline** — vytváření, aktivace / deaktivace
- Spravuje **verze pipeline** — JSON config, datum expirace, historie verzí
- Umožňuje **manuální spuštění pipeline** se simulací ETL kroků (Extract → Transform → Load)
- Sleduje **běhy** v reálném čase — stav, kroky, chyby, počet zpracovaných záznamů
- Zobrazuje **statistiky pipeline** — počet úspěšných/failed běhů, průměrný runtime
- Spravuje **pravidla alertů** a automaticky vytváří alerty při selhání
- Poskytuje **dashboard** s přehledem a autorefreshem každých 10 sekund

---

## Technologie

| Vrstva | Technologie |
|--------|-------------|
| Backend | Python 3, Flask 3 |
| Databáze | SQLite (s automatickými migracemi při startu) |
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

## Stránky aplikace

| Stránka | URL | Popis |
|---------|-----|-------|
| Dashboard | `/` | Souhrnné karty + posledních 5 běhů |
| Datasets | `/datasets.html` | Seznam datasetů, formulář pro vytvoření |
| Pipelines | `/pipelines.html` | Pipeline s Run / Activate / Deactivate, detail s verzemi a statistikami |
| Runs | `/runs.html` | Historie běhů s filtry a kroky ETL |
| Alerts | `/alerts.html` | Alerty s legendou, správa pravidel |
| Versions | `/versions.html` | Přehled všech verzí všech pipeline |
| Popis | `/popis.html` | Dokumentace aplikace |

---

## Struktura projektu

```
pipeline_monitor/
├── app.py              # Vstupní bod Flask aplikace
├── db.py               # Připojení k SQLite + automatické migrace
├── routes/             # API endpointy (Flask Blueprint)
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
| GET | `/pipelines/:id` | Detail pipeline (se statistikami, verzemi, běhy) |
| PATCH | `/pipelines/:id` | Aktivace / deaktivace pipeline |
| POST | `/pipelines/:id/run` | Spuštění pipeline |
| GET | `/pipelines/versions/all` | Všechny verze všech pipeline |
| GET | `/pipelines/:id/versions` | Verze konkrétní pipeline |
| POST | `/pipelines/:id/versions` | Vytvoření nové verze |
| GET / PATCH | `/runs/` | Seznam běhů (filtry: pipeline, status, datum) |
| GET / PATCH | `/runs/:id` | Detail / aktualizace běhu |
| GET / POST | `/alert-rules/` | Pravidla alertů |
| GET / PATCH / DELETE | `/alert-rules/:id` | Detail / úprava / smazání pravidla |
| GET | `/alerts/` | Seznam alert eventů |
| GET | `/alerts/:id` | Detail alert eventu |

---

## Systém verzí pipeline

Každá pipeline má historii verzí konfigurace:

- **active** — aktuální platná verze
- **expired** — platnost vypršela (`expires_at` v minulosti)
- **inactive** — nahrazena novější verzí

Při vytvoření nové verze se předchozí automaticky deaktivuje. Každý běh zaznamenává číslo verze, se kterou byl spuštěn.

---

## Simulace ETL

Po spuštění pipeline se v pozadí (`threading.Thread`) provede simulace:

```
Extract ──► Transform ──► Load
```

- S pravděpodobností **30 %** jeden krok selže → run = `failed` + automatický alert
- Při úspěchu se zaznamená 5 000–200 000 zpracovaných záznamů
- Průběh kroků je viditelný v reálném čase na stránce **Runs**

---

## Systém alertů

| Severity | Kdy vzniká |
|----------|-----------|
| `critical` | Automaticky při každém `failed` runu (pokud má pipeline aktivní alert rule) |
| `warning` | Připraveno v schématu, negeneruje se automaticky |
| `info` | Připraveno v schématu, negeneruje se automaticky |

Stav alertu: `open` (výchozí) / `resolved` (připraveno pro budoucí použití).
