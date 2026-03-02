# uva-course-watch 🕵️‍♂️

A real-time monitoring and analytics tool for UVA course enrollment volatility. 

Instead of just showing a snapshot of what is open *now*, `uva-course-watch` tracks the **delta**—how quickly seats are filling up, when they drop, and historical trends for the most competitive classes at the University of Virginia.

## 🚀 The Concept
UVA students currently rely on manual refreshes of SIS or static snapshots from community tools. This project fills the "data gap" by treating enrollment as **time-series data**. 

By monitoring changes in the [UVA-Course-Explorer](https://github.com/UVA-Course-Explorer/course-data) dataset, this tool can:
* **Detect Volatility:** Identify which classes are "trending" or filling up fastest.
* **Instant Alerts:** Trigger notifications (Discord/Email) the moment a seat opens in a watched section.
* **Historical Analysis:** Visualize enrollment "burn-down" charts to help students plan for future registration cycles.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Data Source:** [UVA Course Explorer](https://github.com/UVA-Course-Explorer/course-data) (JSON via GitHub Actions)
* **Automation:** GitHub Actions (for scheduled "diff" checks)
* **Database:** *[Planned: Supabase/Firebase for user watchlists]*
* **Architecture:** 3-Layer Design (Data Ingestion -> Change Logic -> Notification Engine)

## 📂 Project Structure
```text
uva-course-watch/
├── .github/workflows/  # Scheduled scraping & diff logic
├── src/
│   ├── scraper.py      # Fetches latest data from UVA-Course-Explorer
│   ├── engine.py       # Core logic for comparing state changes (Diffing)
│   └── notifier.py     # Discord/Email alert dispatchers
├── data/               # Local cache for state comparison
└── README.md
