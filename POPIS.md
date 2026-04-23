# Pipeline Monitor — Úplný popis

## Co je to za program

**Pipeline Monitor** je webová aplikace pro sledování ETL pipeline (Extract, Transform, Load) v oblasti Big Data. Program umožňuje monitorovat stav pipeline zpracování dat: spouštět je, zobrazovat historii spuštění a spravovat alerty při selháních.

Jde o výukový projekt demonstrující architekturu REST API + SPA (Single Page Application) bez externích závislostí kromě Flasku.

---

## Technologický stack

| Vrstva | Technologie |
|---|---|
| Backend | Python 3, Flask 3 |
| Databáze | SQLite (soubor `pipeline_monitor.db`) |
| Frontend | Vanilla HTML + CSS + JavaScript (bez frameworků) |
| Závislosti | `flask`, `python-dotenv` |

---

## Architektura

```
pipeline_monitor/
├── app.py                  # vstupní bod, vytvoření Flask aplikace
├── db.py                   # připojení k SQLite
├── routes/                 # HTTP routy (API endpointy)
│   ├── datasets.py
│   ├── pipelines.py
│   ├── runs.py
│   └── alerts.py
├── services/               # business logika
│   ├── dataset_service.py
│   ├── pipeline_service.py
│   ├── run_service.py
│   └── alert_service.py
├── database/
│   ├── schema.sql          # struktura tabulek
│   └── seed_data.sql       # počáteční testovací data
└── frontend/               # statické HTML stránky
    ├── index.html          # dashboard
    ├── datasets.html
    ├── pipelines.html
    ├── runs.html
    ├── alerts.html
    ├── css/style.css
    └── js/api.js           # JavaScript klient pro API
```

Aplikace se řídí vzorem **Blueprint + Service Layer**: routy jsou zodpovědné pouze za HTTP protokol, veškerá logika je v services.

---

## Databáze

Šest tabulek SQLite:

| Tabulka | Účel |
|---|---|
| `datasets` | Zdroje dat (vlastník, verze schématu) |
| `pipelines` | Pipeline napojené na datasety (plán spouštění, aktivita) |
| `pipeline_versions` | Verze konfigurace každé pipeline (JSON) |
| `job_runs` | Spuštění pipeline (stav, čas, počet záznamů) |
| `job_run_steps` | Kroky každého spuštění: extract → transform → load |
| `alert_rules` | Pravidla alertů pro pipeline |
| `alert_events` | Události alertů (závažnost: info / warning / critical) |

Stavy spuštění se řídí konečným automatem: `pending → running → success / failed`.

---

## REST API

### Dashboard
| Metoda | URL | Popis |
|---|---|---|
| GET | `/api/summary` | Celková statistika + 5 posledních spuštění |

### Datasety (`/datasets/`)
| Metoda | URL | Popis |
|---|---|---|
| GET | `/datasets/` | Seznam všech datasetů |
| POST | `/datasets/` | Vytvořit dataset |
| GET | `/datasets/<id>` | Získat dataset podle ID |

### Pipeline (`/pipelines/`)
| Metoda | URL | Popis |
|---|---|---|
| GET | `/pipelines/` | Seznam pipeline (se stavem posledního spuštění) |
| POST | `/pipelines/` | Vytvořit pipeline |
| GET | `/pipelines/<id>` | Detail pipeline (s historií spuštění a alerty) |
| POST | `/pipelines/<id>/run` | Spustit pipeline |

### Spuštění (`/runs/`)
| Metoda | URL | Popis |
|---|---|---|
| GET | `/runs/` | Seznam spuštění (filtr: pipeline_id, status, date) |
| GET | `/runs/<id>` | Detail spuštění s kroky |
| PATCH | `/runs/<id>` | Ručně aktualizovat stav / záznamy / chybu |

### Alerty
| Metoda | URL | Popis |
|---|---|---|
| GET | `/alert-rules/` | Seznam pravidel alertů |
| POST | `/alert-rules/` | Vytvořit pravidlo |
| GET | `/alert-rules/<id>` | Získat pravidlo |
| PATCH | `/alert-rules/<id>` | Zapnout / vypnout pravidlo |
| DELETE | `/alert-rules/<id>` | Smazat pravidlo |
| GET | `/alerts/` | Seznam událostí alertů |
| GET | `/alerts/<id>` | Získat událost alertu |

---

## Jak funguje spuštění pipeline (simulace ETL)

Při volání `POST /pipelines/<id>/run` se odehrává následující:

1. Ověří se, že pipeline existuje a je aktivní.
2. Do tabulky `job_runs` se přidá záznam se stavem `running`.
3. Vytvoří se tři kroky v `job_run_steps`: **extract**, **transform**, **load** — všechny ve stavu `pending`.
4. Spustí se **vlákno na pozadí** (`threading.Thread`), které simuluje průběh:
   - S pauzou 1,5–3 sekundy kroky postupně přecházejí do `running` → `success`.
   - S pravděpodobností **30 %** jeden z kroků náhodně „selže" — stav se změní na `failed`.
   - Při selhání se automaticky vytvoří `alert_events` pro všechna aktivní pravidla alertů dané pipeline.
   - Při úspěchu se zaznamená náhodný počet zpracovaných záznamů (5 000 – 200 000).
5. Výsledný stav (`success` nebo `failed`) se zapíše do `job_runs`.

---

## Frontend

Pět HTML stránek, které komunikují s backendem přes `js/api.js`:

- **Dashboard** (`/`) — kartičky s celkovou statistikou a tabulka posledních 5 spuštění. Automatické obnovení každých 10 sekund.
- **Datasets** — seznam datasetů, formulář pro vytvoření nového.
- **Pipelines** — seznam pipeline, tlačítko „Run", stav posledního spuštění.
- **Runs** — historie všech spuštění s filtrováním.
- **Alerts** — seznam aktivovaných alertů.

---

## Jak spustit

```powershell
cd C:\Users\PC\Desktop\Unicorn\Bezpecnost\Learning-repository\pipeline_monitor

# Poprvé — vytvořit prostředí a nainstalovat závislosti
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Spuštění
python app.py
```

Otevřít v prohlížeči: **http://localhost:5000**

Při dalších spuštěních stačí:
```powershell
venv\Scripts\activate
python app.py
```

---

## Výukové koncepty, které projekt demonstruje

- REST API s Flask Blueprints a oddělením routes / services
- SQLite s cizími klíči a kontrolou CHECK constraints
- Konečný automat pro stavy (state machine)
- Vlákna na pozadí v Pythonu (`threading.Thread`)
- SPA frontend bez frameworků komunikující přes Fetch API
- Simulace reálného ETL procesu (Extract → Transform → Load)
- Systém alertů s pravidly a událostmi
