# 🚀 Job Tracker

A Python-based tool to track big-tech job listings from various company career pages, save them to a database, and send notifications via Telegram.

## 🛠️ Installation

To set up the environment, run the following commands:

1. Create the environment:

```bash
conda create --name job_tracker python=3.12
```

2. Activate the environment:

```bash
conda activate job_tracker
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## 💾 Saving to database

The results are saved into a SQLite 3 database (`data/jobs.db`),
to check if the job found is new or not.
The database consists of a single table named `jobs` with the following schema:

```
+------------------------------------------------------+
|                     TABLE: jobs                      |
+----------------+--------------+----------------------+
|  COLUMN NAME   |  DATA TYPE   |       NOTES          |
+----------------+--------------+----------------------+
| 🔑 id          |     TEXT     |  PRIMARY KEY, Unique |
+----------------+--------------+----------------------+
|    title       |     TEXT     |  e.g. "Data Analyst" |
+----------------+--------------+----------------------+
|    company     |     TEXT     |  e.g. "Google"       |
+----------------+--------------+----------------------+
|    location    |     TEXT     |  e.g. "New York, NY" |
+----------------+--------------+----------------------+
|    link        |     TEXT     |  Direct Job URL      |
+----------------+--------------+----------------------+
|    date_added  |     TEXT     |  e.g. 2025/11/28     |
+----------------+--------------+----------------------+
```

## 🔔 Telegram Notification

To enable Telegram notifications, create a `.env` file in the root directory with your telegram credentials (telegram token and telegram chat id)
and configuration:

```
TELEGRAM_TOKEN=000000000:AAAAAAAAAA-BBBBBBBBBBBBBBBBBBBBBBBB
TELEGRAM_CHAT_ID=-1234567890
DB_PATH=data/jobs.db
```

![Telegram notification](assets/notification.png)

## ▶️ Running

You can run the script using default keywords defined in the code, or pass specific keywords as arguments.

Basic usage:

```bash
python main.py
```

Run with specific keywords:

```bash
python main.py -k security internship
```

Run with verbose logging (shows found jobs details):

```bash
python main.py -v
```

List last 10 jobs found:

```bash
python main.py --list
```

## 🕰️ Automating with Cron

To run the tracker automatically every day at 8:00 AM and 20:00 PM, add the following line to your crontab:

```
0 8,20 * * * /path/to/your/conda/environment/python3 /path/to/job_tracker/main.py
```

## ⚙️ Config

### Companies on a standard ATS

Most companies publish their openings through an applicant tracking system that exposes
a public JSON API. Those don't need a parser — add one entry to the `COMPANIES` list in
`config/companies.py`:

```python
{"name": "Dragos", "ats": "greenhouse", "token": "dragos"},
```

Supported values for `ats` are `greenhouse`, `lever`, `ashby`, `smartrecruiters`,
`workable`, `recruitee`, `personio`, `comeet` and `workday`. `token` is the board
identifier that appears in the company's careers URL (e.g. `jobs.lever.co/<token>`).
Workday additionally needs `wd` and `site`; Comeet needs `company`.

Check your edit with:

```bash
python tests/check_ats_config.py          # structure only, no network
python tests/check_ats_config.py --live   # also fetches every board
```

These entries are turned into parsers at runtime by `parsers/ats.py`. Because the APIs
return the whole board at once, they are fetched with `requests` and need no browser.

Companies whose careers site is not on a supported ATS are listed in
[`docs/companies_without_ats.md`](docs/companies_without_ats.md); those need a custom
parser as described below.

### Companies needing a custom parser

1. Create a new python file under the `parsers/` directory (e.g., `parsers/new_company.py`).
2. Implement a class that contains at least these two methods:
   - `build_urls()`: Returns the list of URLs to scrape.
   - `parse()`: Extracts the job data (title, location, link) from the HTML or API response.
3. Add it to the list of parsers in `main.py`
4. Stay alert for new positions!
