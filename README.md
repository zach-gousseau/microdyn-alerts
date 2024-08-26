# Micro-Dyn Medical Systems - Regulatory Update Scraper

## Overview

This app was built for Micro-Dyn Medical Systems to fetch updates from multiple content sources, analyze them for relevance, and notify Micro-Dyn employees of potentially relevant updates via email. It uses scrapers to gather data from various sources, processes the content to identify important updates, and sends an email summary with links to view the updates in Notion. All content is stored in a local SQLite database and synced to a Notion database.

## Key Features

- Scrapes content from CMS Transmittals, Federal Registry, and the MLN Newsletter.
- Analyzes content to detect updates may be important by first checking for specified keywords (see `search/keyword_search.py`), and on any match, send the scraped content to OpenAI (gpt4o-mini) to detect whether the content contains a potentially relevant update and if so, summarize it.
- Stores the fetched data in both a local SQLite database and a Notion database.
- Sends email notifications with summaries and links to the relevant updates.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/zach-gousseau/microdyn-alerts.git
```

### 2. Set up the environment

Create and activate a virtual environment:

```bash
python -m venv env
source env/bin/activate
```

### 3. Install dependencies

Run the following to install all required dependencies:

```bash
pip install -r requirements.txt
```

### 4. Set up the SQLite database

Use the provided script to initialize the SQLite database schema:

```bash
bash create_db.sh
```

Note that the path of the database can be changed within this file.

## Configuration

Create a .env file that stores tokens and keys. Here’s the format:

```bash
EMAIL_ADDRESS="cms.update.listener@gmail.com"
EMAIL_APP_PASSWORD="your_email_app_password"
OPENAI_API_KEY="your_openai_api_key"
NOTION_TOKEN="your_notion_token"
```

Where:

- `EMAIL_ADDRESS`: The email address used to receive Federal Registry emails, and send notifications.
- `EMAIL_APP_PASSWORD`: The app-specific password for sending emails.
- `OPENAI_API_KEY`: API key for integrating with OpenAI.
- `NOTION_TOKEN`: Token for connecting to the Notion API to store updates.

## Running the App

The main entry point of the app is `main.py`. It can be run as:

```bash
python main.py --emails recipient1@example.com recipient2@example.com --n_days 5 --db_path /path/to/your/database/alerts.db
```

With command line arguments being:

- `--emails`: Required list of email recipients (space-separated).
- `--n_days`: Number of days to look back when fetching updates (default is 5).
- `--db_path`: Path to your SQLite database file (required).

## Main Components

### `UpdateFinder` Class

Handles the core functionality of the app, including:
1. **Fetching Content**: Scrapes content from CMS, Federal Registry, and MLN Newsletter.
2. **Processing Content**: Uses keyword searches and classifiers to find relevant updates.
3. **Storing Data**: Saves updates in both the SQLite database and the Notion database.
4. **Sending Emails**: Notifies recipients if any important updates are detected.

### SQLite Database

The app stores fetched data in a local SQLite database. When you run `create_db.sh`, two tables are created:
- `content`: Contains the updates, URLs, summaries, keywords, and flags for important updates.
- `metadata`: Stores any extra metadata related to the content.

### Notion Database

In addition to local storage, the app also syncs updates to a Notion database. The `NotionClient` class manages the interaction with the Notion API.

### Email Notifications

Once the app processes the updates, it sends a summary email with links to the full content in Notion.

## Setting Up Daily Execution with a Cron Job

To execute the app daily, I recommend setting up a cron job. Below are steps to set that up. 

### 1. Open the Crontab Editor

Create a new cron job by opening your crontab file in edit mode with:

```bash
crontab -e
```

### 2. Add the Cron Job

Add the following line to the crontab to schedule the app to run daily at a specific time (e.g., 6:00 AM). Change the time (`0 6 * * *`) and paths to match your environment (!):

```bash
0 6 * * * /path/to/your/env/bin/python /path/to/your/project/main.py \
    --emails recipient1@example.com recipient2@example.com \
    --n_days 5 \
    --db_path /path/to/your/database/alerts.db \
    >> /path/to/your/logs/update_notification.log 2>&1

```

- `0 6 * * *`: This schedule specifies that the command will run every day at 6:00 AM. Adjust as needed.
- `/path/to/your/env/bin/python`: Absolute path to the Python interpreter in your virtual environment.
- `/path/to/your/project/main.py`: Absolute path to the main script of the app.
- `--emails`: List of email recipients (space-separated).
- `--n_days`: Number of days to look back when fetching updates.
- `--db_path`: Path to your SQLite database file.
- `>> /path/to/your/logs/update_notification.log 2>&1`: Redirects stdout and errors to a log file.

Save and exit.

### 3. Verify the Cron Job

To check whether the job is live, run:

```bash
crontab -l
```

This should show the job that was just created. 