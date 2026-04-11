"""
CampusConnect - Flask Web Application
CSDS 341 - Spring 2026
Caio Albuquerque (caio-a18)

This is the main backend file. It handles all the routes and talks to
the PostgreSQL database using psycopg2.

To run:
    python app.py

Make sure your database is set up first (sql/schema.sql) and the
DB_CONFIG below matches your local PostgreSQL setup.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import psycopg2.extras

app = Flask(__name__)

# Secret key for session management — change this to something random if deploying
app.secret_key = "csds341_campusconnect_dev"

# Database connection settings — update these to match your local setup
DB_CONFIG = {
    "dbname":   "campusconnect",
    "user":     "postgres",
    "password": "password",
    "host":     "localhost",
    "port":     5432,
}


def get_db():
    """Open a new database connection and return it with a dict cursor."""
    conn = psycopg2.connect(**DB_CONFIG)
    # DictCursor lets us access columns by name instead of index
    conn.cursor_factory = psycopg2.extras.DictCursor
    return conn


# ================================================================
# Home / Search page
# ================================================================

@app.route("/", methods=["GET", "POST"])
def index():
    """
    The main search page. On GET just show the empty form.
    On POST, run the search query with whatever filters were filled in.
    """

    # We'll populate these lists for the dropdown menus
    states = []
    results = []
    searched = False

    conn = get_db()
    cur = conn.cursor()

    # Always load the state list for the dropdown
    cur.execute("SELECT StateCode, StateName FROM State ORDER BY StateName")
    states = cur.fetchall()

    if request.method == "POST":
        searched = True

        # Pull the filter values from the form — any of these can be empty
        state_code      = request.form.get("state") or None
        max_tuition     = request.form.get("max_tuition") or None
        inst_type       = request.form.get("inst_type") or None
        size            = request.form.get("size") or None
        min_gpa         = request.form.get("min_gpa") or None
        min_sat         = request.form.get("min_sat") or None
        min_act         = request.form.get("min_act") or None

        # Build the query dynamically based on what was filled in.
        # I'm using parameterized queries (%s placeholders) so there's
        # no risk of SQL injection from user input.
        query = """
            SELECT
                i.InstitutionID,
                i.Name,
                i.Type,
                i.Size,
                i.WebsiteURL,
                s.StateName,
                c.TuitionInState,
                c.TuitionOutOfState,
                c.RoomAndBoard,
                a.MinGPA,
                a.MinSAT,
                a.MinACT
            FROM Institution i
            JOIN isIn     ii ON i.InstitutionID = ii.InstitutionID
            JOIN State     s ON ii.StateCode = s.StateCode
            LEFT JOIN Costs   c ON i.InstitutionID = c.InstitutionID
            LEFT JOIN Accepts a ON i.InstitutionID = a.InstitutionID
            WHERE 1=1
        """

        params = []

        if state_code:
            query += " AND ii.StateCode = %s"
            params.append(state_code)

        if max_tuition:
            # Filter on in-state tuition — most relevant for state residents
            query += " AND c.TuitionInState <= %s"
            params.append(int(max_tuition))

        if inst_type:
            query += " AND i.Type = %s"
            params.append(inst_type)

        if size:
            query += " AND i.Size = %s"
            params.append(size)

        # For GPA/test score filtering: we show schools where the user's stats
        # are AT OR ABOVE the school's minimum (i.e. schools the user can get into)
        if min_gpa:
            query += " AND (a.MinGPA IS NULL OR a.MinGPA <= %s)"
            params.append(float(min_gpa))

        if min_sat:
            query += " AND (a.MinSAT IS NULL OR a.MinSAT <= %s)"
            params.append(int(min_sat))

        if min_act:
            query += " AND (a.MinACT IS NULL OR a.MinACT <= %s)"
            params.append(int(min_act))

        query += " ORDER BY i.Name LIMIT 100"

        cur.execute(query, params)
        results = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        states=states,
        results=results,
        searched=searched
    )


# ================================================================
# Individual school detail page
# ================================================================

@app.route("/school/<int:school_id>")
def school(school_id):
    """
    Shows full details for one institution, including all programs offered.
    """
    conn = get_db()
    cur = conn.cursor()

    # Get the main school info
    cur.execute("""
        SELECT
            i.InstitutionID,
            i.Name,
            i.Type,
            i.Size,
            i.WebsiteURL,
            s.StateName,
            c.TuitionInState,
            c.TuitionOutOfState,
            c.RoomAndBoard,
            a.MinGPA,
            a.MinSAT,
            a.MinACT
        FROM Institution i
        JOIN isIn     ii ON i.InstitutionID = ii.InstitutionID
        JOIN State     s ON ii.StateCode = s.StateCode
        LEFT JOIN Costs   c ON i.InstitutionID = c.InstitutionID
        LEFT JOIN Accepts a ON i.InstitutionID = a.InstitutionID
        WHERE i.InstitutionID = %s
    """, (school_id,))

    school_info = cur.fetchone()

    if not school_info:
        cur.close()
        conn.close()
        return "School not found", 404

    # Get all programs offered at this school
    cur.execute("""
        SELECT p.ProgramCode, p.ProgramName, p.Field
        FROM Program p
        JOIN Offers o ON p.ProgramCode = o.ProgramCode
        WHERE o.InstitutionID = %s
        ORDER BY p.Field, p.ProgramName
    """, (school_id,))

    programs = cur.fetchall()

    # Check if the logged-in user has already saved this school
    already_saved = False
    if "user_id" in session:
        cur.execute("""
            SELECT 1 FROM SavedSchools
            WHERE UserID = %s AND InstitutionID = %s
        """, (session["user_id"], school_id))
        already_saved = cur.fetchone() is not None

    cur.close()
    conn.close()

    return render_template(
        "school.html",
        school=school_info,
        programs=programs,
        already_saved=already_saved
    )


# ================================================================
# Save / unsave a school
# ================================================================

@app.route("/save/<int:school_id>", methods=["POST"])
def save_school(school_id):
    """Add a school to the logged-in user's saved list."""
    if "user_id" not in session:
        flash("You need to log in to save schools.")
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    # Use INSERT ... ON CONFLICT DO NOTHING so re-saving doesn't throw an error
    cur.execute("""
        INSERT INTO SavedSchools (UserID, InstitutionID)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """, (session["user_id"], school_id))

    conn.commit()
    cur.close()
    conn.close()

    flash("School saved to your profile!")
    return redirect(url_for("school", school_id=school_id))


@app.route("/unsave/<int:school_id>", methods=["POST"])
def unsave_school(school_id):
    """Remove a school from the logged-in user's saved list."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM SavedSchools
        WHERE UserID = %s AND InstitutionID = %s
    """, (session["user_id"], school_id))

    conn.commit()
    cur.close()
    conn.close()

    flash("School removed from your profile.")
    return redirect(url_for("school", school_id=school_id))


# ================================================================
# User profile — shows saved schools
# ================================================================

@app.route("/profile")
def profile():
    """Show the logged-in user's info and their saved schools."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    # Get user info
    cur.execute("""
        SELECT Name, Email, GPA, SATScore, ACTScore, PreferredState
        FROM UserProfile
        WHERE UserID = %s
    """, (session["user_id"],))
    user = cur.fetchone()

    # Get their saved schools with cost info
    cur.execute("""
        SELECT
            i.InstitutionID,
            i.Name,
            i.Type,
            i.Size,
            s.StateName,
            c.TuitionInState,
            ss.SavedDate
        FROM SavedSchools ss
        JOIN Institution i ON ss.InstitutionID = i.InstitutionID
        JOIN isIn ii       ON i.InstitutionID = ii.InstitutionID
        JOIN State s       ON ii.StateCode = s.StateCode
        LEFT JOIN Costs c  ON i.InstitutionID = c.InstitutionID
        WHERE ss.UserID = %s
        ORDER BY ss.SavedDate DESC
    """, (session["user_id"],))
    saved = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("profile.html", user=user, saved=saved)


# ================================================================
# Auth — login / logout / register
# ================================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT UserID, Name, Password
            FROM UserProfile
            WHERE Email = %s
        """, (email,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        # In a real app you'd use bcrypt to check the hash.
        # Keeping it plaintext for the scope of this class project.
        if user and user["password"] == password:
            session["user_id"]   = user["userid"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name    = request.form.get("name")
        email   = request.form.get("email")
        password = request.form.get("password")
        gpa     = request.form.get("gpa") or None
        sat     = request.form.get("sat") or None
        act     = request.form.get("act") or None
        state   = request.form.get("preferred_state") or None

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO UserProfile (Name, Email, Password, GPA, SATScore, ACTScore, PreferredState)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING UserID
            """, (name, email, password, gpa, sat, act, state))

            user_id = cur.fetchone()["userid"]
            conn.commit()

            session["user_id"]   = user_id
            session["user_name"] = name
            flash(f"Account created! Welcome, {name}.")
            return redirect(url_for("index"))

        except psycopg2.errors.UniqueViolation:
            # Email already in use
            conn.rollback()
            flash("An account with that email already exists.")
        finally:
            cur.close()
            conn.close()

    # Load states for the dropdown on the register form
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT StateCode, StateName FROM State ORDER BY StateName")
    states = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("login.html", register=True, states=states)


@app.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # debug=True auto-reloads the server when you save changes
    # turn this off if running in front of anyone else
    app.run(debug=True, port=5000)
