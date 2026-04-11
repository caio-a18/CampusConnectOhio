# Caio's Work — CampusConnect

This branch contains my portion of the CampusConnect project for CSDS 341.

My two technical components are:

1. **SQL Table Creation (DDL)** — writing the `CREATE TABLE` statements that define the
   full database schema, including all primary keys, foreign keys, and constraints.

2. **Web Interface** — a Flask-based web app that lets users search schools, filter by
   tuition/location/test scores, and save schools to a personal profile.

---

## Files I'm Responsible For

```
sql/schema.sql          -- all CREATE TABLE and constraint definitions
web/app.py              -- Flask routes and database query logic
web/templates/          -- HTML pages (Jinja2 templates)
  base.html             -- shared layout with nav
  index.html            -- home / search page
  results.html          -- search results table
  school.html           -- individual school detail page
  profile.html          -- user saved schools
  login.html            -- simple login form
web/static/css/
  style.css             -- basic styling
web/static/js/
  main.js               -- small client-side helpers
```

---

## How to Run

### Prerequisites

```bash
pip install flask psycopg2-binary
```

You also need PostgreSQL running locally with the database already created and populated
(see Dilon's `data/load_data.py` for that step).

### Start the app

```bash
cd web
python app.py
```

Then open `http://localhost:5000` in your browser.

---

## Schema Overview

The `sql/schema.sql` file creates the following tables:

| Table | What it stores |
|-------|---------------|
| `State` | U.S. states and regions |
| `Institution` | College/university basic info |
| `isIn` | Which state each institution is in |
| `Costs` | Tuition and room/board per institution |
| `Accepts` | Admissions criteria (GPA, SAT, ACT) |
| `Program` | CIP program codes and fields |
| `Offers` | Which programs each institution offers |
| `UserProfile` | Registered users and their academic stats |
| `SavedSchools` | Schools a user has bookmarked |

---
