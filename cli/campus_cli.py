"""
CampusConnect - Command Line Interface
CSDS 341 - Spring 2026
Caio Albuquerque (caio-a18)

Connects to the campusconnect PostgreSQL database and lets you run
the main queries interactively from the terminal.

To run:
    python cli/campus_cli.py

Make sure the database is running and populated before using this.
"""

import os
import psycopg2
import psycopg2.extras
import sys

DB_CONFIG = {
    "dbname":   os.environ.get("DB_NAME", "campusconnect"),
    "user":     os.environ.get("DB_USER", os.environ.get("USER", "postgres")),
    "password": os.environ.get("DB_PASSWORD", ""),
    "host":     os.environ.get("DB_HOST", "localhost"),
    "port":     int(os.environ.get("DB_PORT", 5432)),
}


def get_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.cursor_factory = psycopg2.extras.DictCursor
        return conn
    except psycopg2.OperationalError as e:
        print(f"\nCould not connect to the database: {e}")
        sys.exit(1)


def fmt_currency(value):
    if value is None:
        return "N/A"
    return "${:,}".format(int(value))


def fmt_float(value):
    if value is None:
        return "N/A"
    return str(value)


# ----------------------------------------------------------------
# 1. Search schools by state
# ----------------------------------------------------------------

def search_by_state():
    state = input("Enter state code (e.g. OH, CA, NY): ").strip().upper()
    if not state:
        print("No state entered.")
        return

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.Name, i.Type, i.Size, c.TuitionInState, c.TuitionOutOfState
        FROM Institution i
        JOIN isIn ii ON i.InstitutionID = ii.InstitutionID
        LEFT JOIN Costs c ON i.InstitutionID = c.InstitutionID
        WHERE ii.StateCode = %s
        ORDER BY i.Name
        LIMIT 50
    """, (state,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print(f"No schools found in {state}.")
        return

    print(f"\n{'School':<50} {'Type':<10} {'Size':<10} {'In-State':<12} {'Out-State'}")
    print("-" * 100)
    for r in rows:
        print(f"{r['name']:<50} {r['type'] or 'N/A':<10} {r['size'] or 'N/A':<10} "
              f"{fmt_currency(r['tuitioninstate']):<12} {fmt_currency(r['tuitionoutofstate'])}")
    print(f"\n{len(rows)} result(s) shown (max 50).")


# ----------------------------------------------------------------
# 2. Search schools by max tuition
# ----------------------------------------------------------------

def search_by_tuition():
    raw = input("Enter max in-state tuition (e.g. 20000): ").strip()
    if not raw.isdigit():
        print("Invalid amount.")
        return
    max_tuition = int(raw)

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.Name, s.StateCode, i.Type, c.TuitionInState, c.TuitionOutOfState
        FROM Institution i
        JOIN isIn ii ON i.InstitutionID = ii.InstitutionID
        JOIN State s ON ii.StateCode = s.StateCode
        JOIN Costs c ON i.InstitutionID = c.InstitutionID
        WHERE c.TuitionInState <= %s
        ORDER BY c.TuitionInState ASC
        LIMIT 50
    """, (max_tuition,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print(f"No schools found under {fmt_currency(max_tuition)} in-state tuition.")
        return

    print(f"\n{'School':<50} {'State':<6} {'Type':<10} {'In-State':<12} {'Out-State'}")
    print("-" * 100)
    for r in rows:
        print(f"{r['name']:<50} {r['statecode']:<6} {r['type'] or 'N/A':<10} "
              f"{fmt_currency(r['tuitioninstate']):<12} {fmt_currency(r['tuitionoutofstate'])}")
    print(f"\n{len(rows)} result(s) shown (max 50).")


# ----------------------------------------------------------------
# 3. Match schools to a student's academic profile
# ----------------------------------------------------------------

def search_by_profile():
    print("Enter your academic stats (press Enter to skip any):")
    gpa_raw = input("  GPA (e.g. 3.50): ").strip()
    sat_raw = input("  SAT score (e.g. 1200): ").strip()
    act_raw = input("  ACT score (e.g. 25): ").strip()

    try:
        gpa = float(gpa_raw) if gpa_raw else None
    except ValueError:
        print("Invalid GPA — must be a number like 3.50.")
        return
    sat = int(sat_raw)   if sat_raw.isdigit() else None
    act = int(act_raw)   if act_raw.isdigit() else None

    if gpa is None and sat is None and act is None:
        print("No stats entered.")
        return

    query = """
        SELECT i.Name, s.StateCode, i.Type, a.MinGPA, a.MinSAT, a.MinACT
        FROM Institution i
        JOIN Accepts a ON i.InstitutionID = a.InstitutionID
        JOIN isIn ii ON i.InstitutionID = ii.InstitutionID
        JOIN State s ON ii.StateCode = s.StateCode
        WHERE 1=1
    """
    params = []

    if gpa is not None:
        query += " AND (a.MinGPA IS NULL OR a.MinGPA <= %s)"
        params.append(gpa)
    if sat is not None:
        query += " AND (a.MinSAT IS NULL OR a.MinSAT <= %s)"
        params.append(sat)
    if act is not None:
        query += " AND (a.MinACT IS NULL OR a.MinACT <= %s)"
        params.append(act)

    query += " ORDER BY i.Name LIMIT 50"

    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("No matching schools found.")
        return

    print(f"\n{'School':<50} {'State':<6} {'Type':<10} {'Min GPA':<10} {'Min SAT':<10} {'Min ACT'}")
    print("-" * 105)
    for r in rows:
        print(f"{r['name']:<50} {r['statecode']:<6} {r['type'] or 'N/A':<10} "
              f"{fmt_float(r['mingpa']):<10} {fmt_float(r['minsat']):<10} {fmt_float(r['minact'])}")
    print(f"\n{len(rows)} result(s) shown (max 50).")


# ----------------------------------------------------------------
# 4. View a user's saved schools
# ----------------------------------------------------------------

def view_saved_schools():
    user_id_raw = input("Enter your user ID: ").strip()
    if not user_id_raw.isdigit():
        print("Invalid user ID.")
        return
    user_id = int(user_id_raw)

    conn = get_db()
    cur = conn.cursor()

    # Check the user exists
    cur.execute("SELECT Name FROM UserProfile WHERE UserID = %s", (user_id,))
    user = cur.fetchone()
    if not user:
        print(f"No user found with ID {user_id}.")
        cur.close()
        conn.close()
        return

    cur.execute("""
        SELECT i.Name, s.StateCode, i.Type, c.TuitionInState, ss.SavedDate
        FROM SavedSchools ss
        JOIN Institution i ON ss.InstitutionID = i.InstitutionID
        JOIN isIn ii ON i.InstitutionID = ii.InstitutionID
        JOIN State s ON ii.StateCode = s.StateCode
        LEFT JOIN Costs c ON i.InstitutionID = c.InstitutionID
        WHERE ss.UserID = %s
        ORDER BY ss.SavedDate DESC
    """, (user_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"\nSaved schools for {user['name']}:")
    if not rows:
        print("  No schools saved yet.")
        return

    print(f"\n{'School':<50} {'State':<6} {'Type':<10} {'In-State':<12} {'Saved On'}")
    print("-" * 100)
    for r in rows:
        print(f"{r['name']:<50} {r['statecode']:<6} {r['type'] or 'N/A':<10} "
              f"{fmt_currency(r['tuitioninstate']):<12} {r['saveddate']}")


# ----------------------------------------------------------------
# 5. Save a school to a user profile
# ----------------------------------------------------------------

def save_school():
    user_id_raw = input("Enter your user ID: ").strip()
    inst_id_raw = input("Enter the institution ID to save: ").strip()

    if not user_id_raw.isdigit() or not inst_id_raw.isdigit():
        print("Invalid input.")
        return

    user_id = int(user_id_raw)
    inst_id = int(inst_id_raw)

    conn = get_db()
    cur = conn.cursor()

    # Verify both exist
    cur.execute("SELECT Name FROM UserProfile WHERE UserID = %s", (user_id,))
    user = cur.fetchone()
    cur.execute("SELECT Name FROM Institution WHERE InstitutionID = %s", (inst_id,))
    school = cur.fetchone()

    if not user:
        print(f"No user found with ID {user_id}.")
        cur.close()
        conn.close()
        return
    if not school:
        print(f"No institution found with ID {inst_id}.")
        cur.close()
        conn.close()
        return

    cur.execute("""
        INSERT INTO SavedSchools (UserID, InstitutionID)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """, (user_id, inst_id))
    conn.commit()

    cur.close()
    conn.close()
    print(f"Saved '{school['name']}' to {user['name']}'s profile.")


# ----------------------------------------------------------------
# Main menu
# ----------------------------------------------------------------

MENU = """
=== CampusConnect CLI ===
1. Search schools by state
2. Search schools by max tuition
3. Match schools to academic profile (GPA / SAT / ACT)
4. View a user's saved schools
5. Save a school to a user profile
0. Exit
"""

def main():
    print("Connecting to CampusConnect database...")
    # Test connection on startup
    conn = get_db()
    conn.close()
    print("Connected.\n")

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            search_by_state()
        elif choice == "2":
            search_by_tuition()
        elif choice == "3":
            search_by_profile()
        elif choice == "4":
            view_saved_schools()
        elif choice == "5":
            save_school()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()
