# ICSYAK

<p align="center">

   <img src="https://github.com/user-attachments/assets/c418c365-d036-45c0-a57e-822bd0312a57" width="200" height="200">
</p>

<p align="center">
   <em>A Discord bot for UCI's ICS courses that bridges course platforms like Ed Discussion, Piazza, Gradescope, and Discord — designed to keep students informed without switching tabs.</em>
</p>

---

## About

**ICSYAK** is a multi-purpose Discord bot designed for UCI students in Computer Science and Informatics classes. Originally built for ICS 6B and 6D, it has since expanded to support over a dozen courses across five quarters. The bot solves a key pain point: many instructors moved away from Discord to Ed Discussion or Piazza, leaving students out of the loop. ICSYAK brings that critical information *back* to Discord, with a full suite of features that automate, track, and notify.

---

## Features

### 📌 Course Forum Integration

- **Ed Discussion Support**:
  - Auto-post new threads by category.
  - Reacting to posts opens Discord threads with embedded replies (answers & comments).
  - Slash command `/link_thread [id]` embeds a specific Ed thread via number.
  - Replaces Ed URLs in user messages with rich embeds and reply threads.

- **Piazza Support** *(new!)*:
  - Automatically mirrors new posts from Piazza into Discord.
  - Built-in handling for follow-ups and responses.

### 🗂️ Gradescope Integration

- Uses the [`gradescope-tool`](https://pypi.org/project/gradescope-tool/) Python package (contributed to by the developer).
- Supports fetching assignment templates (e.g., PDFs for CS161/162).
- Automatically structures the templates and sends reminder messages in Discord before deadlines.

### ✅ Check-In System

- Custom `/checkin` command with persistent buttons (survive bot restarts).
- Tracks participant check-ins using a SQLite database.
- Designed for weekly CS161 check-ins — includes ranking and statistics output.
- Stores and restores interaction IDs on restart for seamless use.

### 🎨 Color Palette Role Manager

- Adds aesthetic role selection via buttons.
- Fully customizable with dynamic color role sets.
- Useful for branding student servers or for fun.

### 📈 Course Tracking

- Bot usage spans:
  - **13 courses**
  - **8 professors**
  - **5 academic quarters**
  - **1000+ students**

| Dept | #     | Prof       | Quarters             |
|------|-------|------------|----------------------|
| ICS  | 6B    | Gassko     | F23, S24, F24        |
| ICS  | 6D    | Gassko     | W24, W25             |
| ICS  | 45C   | Klefstad   | S24                  |
| ICS  | 46    | Shindler   | F24                  |
| ICS  | 51    | Dutt       | W24                  |
| ICS  | 53    | Wong-ma    | W25                  |
| STATS| 67    | Dogucu     | F24                  |
| INF  | 43    | Ziv        | W24                  |
| INF  | 133   | Jaganath   | F24                  |
| CS   | 122A  | Wong-ma    | F24                  |
| CS   | 161   | Shindler   | S25                  |
| CS   | 162   | Shindler   | S25                  |
| CS   | 178   | Ahmed      | S25                  |

---

## Hosting & Deployment

- Hosted on **UCI ICS servers** using `SLURM` for job scheduling.
- Uses Flask for web pinging (`keep_alive.py`).
- Compatible with `uptimerobot` or production cron systems.

---

## Tech Stack

- `discord.py` for the bot framework.
- `edapi`, `gradescope-tool`, `piazza-api` for API access.
- `sqlite3` for persistent state (check-ins, roles, interaction tracking).
- `Flask` for web server + uptime pings.
- `asyncio`, `tasks.loop` for periodic updates.

---

## Getting Started

> **Note:** You must provide a `.env` file with proper credentials and token setup.

```bash
pip install -r requirements.txt
python main.py
```

---

## Directory Overview

```
├── checkin.db                # SQLite DB for persistent check-ins
├── checkin.py                # Check-in system logic
├── ed.py                     # Ed Discussion utilities
├── piazza.py                 # Piazza integration
├── gradescope_helper.py      # Gradescope assignment and reminder handler
├── color_palette.py          # Color role system
├── eventhandlers.py          # Central event/router logic
├── keep_alive.py             # Flask uptime pings
├── main.py                   # Bot entry point
├── threadgrabber.py          # Ed reply fetcher + embedder
├── owner.py, view.py, admin.py # Admin utilities
```

---

## Contributing

Contributions welcome! Submit an issue or open a PR.

---

## License

MIT License © 2025 Yousef Khan

---
