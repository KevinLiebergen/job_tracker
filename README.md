# Job tracker


## Installation

```bash
$ conda create --name job_tracker python=3.12 
$ conda activate job_tracker
$ pip install -r requirements.txt 
```

## Running

```bash
python main.py
python main.py -k security developer cloud
```

Put it in a cronjob
```cron
0 9 * * * /path/environment/python3 /path/job_tracker/main.py -k security internship
```

## Notification

To send a Telegram notification, create a `.env` file with this 

```
TELEGRAM_TOKEN=000000000:AAAAAAAAAA-BBBBBBBBBBBBBBBBBBBBBBBB
TELEGRAM_CHAT_ID=-1234567890
DB_PATH=data/jobs.db
```

## Saving

The resuls are saved into a SQLite 3 database, with 1 table of this format:

```markdown
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

## Config

If you want to add a new company to track, add it to `URL_CONFIG` in the `config_urls.py` file,
filling the specific fields, and add a parser in the `parsers` directory the crawler has to know how to parse it!
