# CampusConnect

**CSDS 341 – Introduction to Database Systems | Spring 2026**

A college search and comparison tool that lets students filter U.S. institutions by tuition,
location, size, and academic profile. Backed by a relational database populated from IPEDS data
(~20,000 rows across all tables), with a web interface and CLI for searching and saving schools.

---

## Team Members

- Caio
- Tommaso
- Dilon

---

## Project Structure

```
CampusConnectOhio/
├── sql/
│   ├── schema.sql          # CREATE TABLE statements (Caio)
│   └── queries.sql         # Core SQL queries for the app (Dilon)
├── web/
│   ├── app.py              # Flask backend (Caio)
│   ├── templates/          # HTML pages (Caio)
│   └── static/             # CSS + JS (Caio)
├── cli/
│   └── campus_cli.py       # Command-line interface (Caio)
├── data/
│   └── load_data.py        # IPEDS CSV → database loader (Dilon)
└── docs/
    ├── er_diagram.png      # Final ER diagram (Tommaso)
    └── schemas.md          # Written-out relational schemas (Tommaso)
```

---

## Database Schema (Final — after ER redesign)

The original proposal had a critical error: `InstitutionID` was listed as a primary key
inside every entity, which introduces redundancy. The relationship sets (`Offers`, `Costs`,
`isIn`, `Accepts`) are what link entities — they carry the foreign keys. Entity tables
should only hold attributes intrinsic to that entity.

### Entity Tables

```sql
Institution(InstitutionID, Name, Type, Size, WebsiteURL)
State(StateCode, StateName, Region)
Program(ProgramCode, ProgramName, Field)
UserProfile(UserID, Name, Email, GPA, SATScore, ACTScore, PreferredState)
```

### Relationship Tables

```sql
isIn(InstitutionID, StateCode)
Costs(InstitutionID, TuitionInState, TuitionOutState, RoomBoard)
Offers(InstitutionID, ProgramCode)
Accepts(InstitutionID, MinGPA, MinSAT, MinACT)
SavedSchools(UserID, InstitutionID, SavedDate)
```

---

## Items to Fix (from Proposal Feedback)

### Tommaso — ER Diagram + Schemas + SQL Views

**SQL Views:** `sql/views.sql`
- `UserSummary` — each user with a count of their saved schools
- `UserSchoolMatches` — matches each user to schools they qualify for based on their stored GPA/SAT/ACT

**ER Diagram (was 15/25):** `docs/er_diagram.png`
- Remove `InstitutionID` from every entity box — it belongs on the relationship tables, not inside entities
- Add proper participation constraints (double line = total participation, single = partial)
- Add `UserProfile` and `SavedSchools` as entities with a `Saves` relationship
- Redraw using the Assignment 1 ER tool so lines and arrows are clean and readable

**Schemas (was 15/25):** `docs/schemas.md`
- Add the four missing relationship schemas (`isIn`, `Costs`, `Offers`, `Accepts`, `SavedSchools`)
- Verify all tables reach 3NF — no partial dependencies, no transitive dependencies

---

### Dilon — Data + CLI

**Data (scope was too small — ~200 Ohio schools → ~1,000 rows total):**
- Switch to full U.S. IPEDS dataset: https://nces.ed.gov/ipeds/use-the-data
- Download the Institutional Characteristics and Admissions tables
- Target row counts:

  | Table | Target Rows |
  |-------|-------------|
  | Institution | ~6,000 |
  | Costs | ~6,000 |
  | Accepts | ~6,000 |
  | isIn | ~6,000 |
  | Program + Offers | ~2,000 |
  | **Total** | **~20,000+** |

- Write `data/load_data.py` to parse the IPEDS CSVs and INSERT rows into the DB

**SQL Queries:** `sql/queries.sql` — 12 reference queries covering all major use cases

---

### Caio — Web Interface + DDL + CLI

**CREATE TABLE statements:** `sql/schema.sql`

**Flask web app:** `web/app.py` + `web/templates/` + `web/static/`
- Search form with filters (tuition, state, size, test scores)
- Results table with links to school websites
- User login (session-based, simple)
- Save school to profile
- View saved schools

**CLI:** `cli/campus_cli.py`
- Interactive menu to run all main queries from the terminal
- Filter by state, tuition, GPA/SAT/ACT
- View and save schools for a user profile

---

## Background (to expand in final report)

The current background section is solid but needs two additional paragraphs for the
final report:

1. **Existing tools:** Niche, College Board Big Future, Common App, and Peterson's all
   provide college search features. However, they are heavily commercial — results are
   influenced by advertising partnerships and data is spread across multiple platforms.

2. **Why a database:** A simple spreadsheet cannot handle multi-table joins across 6,000
   institutions, 120,000 program offerings, and hundreds of user profiles simultaneously.
   A relational database with proper indexing handles range queries (tuition filters),
   joins (institution + costs + admissions), and user-specific data (saved schools) in
   a structured, consistent way. This is precisely the scenario databases were designed for.

---

## Demo

Sign up for the TA demo slot before **April 22**. The app must be running locally
with real data loaded. All three team members should be present.
