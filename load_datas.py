import psycopg2
import pandas as pd
import os

# CIP codes in the CSV are formatted with Excel artifacts like ="01" instead of just 01
# This function strips those out and returns a clean string, or None if the value is missing
def clean_cip_code(value):
    if pd.isna(value):
        return None
    code = str(value).strip()
    code = code.replace('="', '').replace('"', '')
    return code

# Connect to PostgreSQL
DATABASE_URL = f"dbname=campusconnect user=postgres password={os.environ.get('DB_PASSWORD', '')} host=localhost port=5432"

#Load College Scorecard Dataset 
df = pd.read_csv("Most-Recent-Cohorts-Institution.csv", low_memory=False)

#Load CIP Code Dataset
cip_df = pd.read_csv("CIPCode2010.csv")
cip_df["CIPCode_clean"] = cip_df["CIPCode"].apply(clean_cip_code)
cip_df["CIPFamily_clean"] = cip_df["CIPFamily"].apply(clean_cip_code)
family_map = {}
for _, row in cip_df.iterrows():
    code = row["CIPCode_clean"]
    family = row["CIPFamily_clean"]
    title = row["CIPTitle"].strip().rstrip(".")
    # A row is a family-level entry when its code equals its family code
    if code == family:
        family_map[family] = title

#Load CIP Code Dataset for Offers
offers_df = pd.read_csv("c2024_a.csv", low_memory=False)

#Make sure you are connected
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
print("Connected!")

#Add Data to States 
state_names = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
    "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota",
    "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "DC": "District of Columbia"
}

state_regions = {
    "AL": "South", "AK": "West", "AZ": "West", "AR": "South",
    "CA": "West", "CO": "West", "CT": "Northeast",
    "DE": "South", "FL": "South", "GA": "South",
    "HI": "West", "ID": "West", "IL": "Midwest",
    "IN": "Midwest", "IA": "Midwest", "KS": "Midwest",
    "KY": "South", "LA": "South", "ME": "Northeast",
    "MD": "South", "MA": "Northeast", "MI": "Midwest",
    "MN": "Midwest", "MS": "South", "MO": "Midwest",
    "MT": "West", "NE": "Midwest", "NV": "West",
    "NH": "Northeast", "NJ": "Northeast", "NM": "West",
    "NY": "Northeast", "NC": "South", "ND": "Midwest",
    "OH": "Midwest", "OK": "South", "OR": "West",
    "PA": "Northeast", "RI": "Northeast",
    "SC": "South", "SD": "Midwest",
    "TN": "South", "TX": "South", "UT": "West",
    "VT": "Northeast", "VA": "South", "WA": "West",
    "WV": "South", "WI": "Midwest", "WY": "West",
    "DC": "South"
}

states = df[["STABBR"]].dropna().drop_duplicates()

for _, row in states.iterrows():
    state_code = row["STABBR"]
    state_name = state_names.get(state_code, state_code)
    region = state_regions.get(state_code, None)

    cur.execute(
        """
        INSERT INTO State (StateCode, StateName, Region)
        VALUES (%s, %s, %s)
        ON CONFLICT (StateCode) DO NOTHING;
        """,
        (state_code, state_name, region)
    )

conn.commit()
print("States inserted!")

#Add Data to Instituions 
for _, row in df.iterrows():
    inst_id = row["UNITID"]
    name = row["INSTNM"]
    control = row["CONTROL"]
    enrollment = row["UGDS"]
    website = row["INSTURL"] if "INSTURL" in df.columns and pd.notna(row["INSTURL"]) else None

    # Map CONTROL to schema values
    if control == 1:
        inst_type = "Public"
    elif control in [2, 3]:
        inst_type = "Private"
    else:
        inst_type = None

    # Bucket UGDS into schema size values
    if pd.isna(enrollment):
        size = None
    elif enrollment < 5000:
        size = "Small"
    elif enrollment < 15000:
        size = "Medium"
    else:
        size = "Large"

    cur.execute(
        """
        INSERT INTO Institution (InstitutionID, Name, Type, Size, WebsiteURL)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (InstitutionID) DO NOTHING;
        """,
        (int(inst_id), name, inst_type, size, website)
    )

conn.commit()
print("Institutions inserted!")

#Add data to programs
for _, row in cip_df.iterrows():
    code = row["CIPCode_clean"]
    name = row["CIPTitle"].strip().rstrip(".")
    family = row["CIPFamily_clean"]

    # Look up the human-readable family name instead of using the raw number
    field = family_map.get(family, family)

    cur.execute(
        """
        INSERT INTO Program (ProgramCode, ProgramName, Field)
        VALUES (%s, %s, %s)
        ON CONFLICT (ProgramCode) DO NOTHING;
        """,
        (code, name, field)
    )

conn.commit()
print("Programs inserted!")

# Add data to Offers
# c2024_a.csv has UNITID + CIPCODE — one row per institution/program/degree level
# We only care about distinct (institution, program) pairs for the Offers table

def format_cip_for_lookup(value):
    """Convert float CIP like 1.0999 → '01.0999' to match Program table format"""
    if pd.isna(value):
        return None
    # Convert to string, zero-pad the family prefix to 2 digits
    parts = str(value).split(".")
    family = parts[0].zfill(2)
    suffix = parts[1] if len(parts) > 1 else "0000"
    return f"{family}.{suffix}"

# Get distinct (UNITID, CIPCODE) pairs — drop duplicates from multiple degree levels
offers_pairs = offers_df[["UNITID", "CIPCODE"]].dropna().drop_duplicates()

inserted = 0
skipped = 0

for _, row in offers_pairs.iterrows():
    inst_id = int(row["UNITID"])
    program_code = format_cip_for_lookup(row["CIPCODE"])

    if program_code is None:
        skipped += 1
        continue

    try:
        cur.execute("SAVEPOINT sp;")
        cur.execute(
            """
            INSERT INTO Offers (InstitutionID, ProgramCode)
            VALUES (%s, %s)
            ON CONFLICT (InstitutionID, ProgramCode) DO NOTHING;
            """,
            (inst_id, program_code)
        )
        cur.execute("RELEASE SAVEPOINT sp;")
        inserted += 1
    except Exception as e:
        cur.execute("ROLLBACK TO SAVEPOINT sp;")
        skipped += 1
        continue

conn.commit()
print(f"Offers inserted: {inserted}, skipped: {skipped}")

# Add data to isIn
for _, row in df.iterrows():
    inst_id = row["UNITID"]
    state_code = row["STABBR"]

    if pd.isna(inst_id) or pd.isna(state_code):
        continue

    cur.execute(
        """
        INSERT INTO isIn (InstitutionID, StateCode)
        VALUES (%s, %s)
        ON CONFLICT (InstitutionID) DO NOTHING;
        """,
        (int(inst_id), state_code)
    )

conn.commit()
print("isIn inserted!")

# Add data to Costs
for _, row in df.iterrows():
    inst_id = row["UNITID"]
    in_state = row.get("TUITIONFEE_IN")
    out_state = row.get("TUITIONFEE_OUT")
    room_board = row.get("ROOMBOARD_ON")

    # Skip if no institution ID
    if pd.isna(inst_id):
        continue

    cur.execute(
        """
        INSERT INTO Costs (InstitutionID, TuitionInState, TuitionOutOfState, RoomAndBoard)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (InstitutionID) DO NOTHING;
        """,
        (
            int(inst_id),
            int(in_state) if pd.notna(in_state) else None,
            int(out_state) if pd.notna(out_state) else None,
            int(room_board) if pd.notna(room_board) else None
        )
    )

conn.commit()
print("Costs inserted!")

# Add data to Accepts
for _, row in df.iterrows():
    inst_id = row["UNITID"]

    if pd.isna(inst_id):
        continue

    sat_wr25 = row.get("SATWR25")
    sat_mr25 = row.get("SATMT25")
    sat_wr75 = row.get("SATWR75")
    sat_mr75 = row.get("SATMT75")
    sat_avg  = row.get("SAT_AVG")

    act_25  = row.get("ACTCM25")
    act_mid = row.get("ACTCMMID")
    act_75  = row.get("ACTCM75")

    min_sat = None
    min_act = None

    # SAT: prefer 25th percentile → average → 75th percentile
    if pd.notna(sat_wr25) and pd.notna(sat_mr25):
        min_sat = int(sat_wr25) + int(sat_mr25)
    elif pd.notna(sat_avg):
        min_sat = int(sat_avg)
    elif pd.notna(sat_wr75) and pd.notna(sat_mr75):
        min_sat = int(sat_wr75) + int(sat_mr75)

    # ACT: prefer 25th percentile → midpoint → 75th percentile
    if pd.notna(act_25):
        min_act = int(act_25)
    elif pd.notna(act_mid):
        min_act = int(act_mid)
    elif pd.notna(act_75):
        min_act = int(act_75)

    cur.execute(
        """
        INSERT INTO Accepts (InstitutionID, MinGPA, MinSAT, MinACT)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (InstitutionID) DO NOTHING;
        """,
        (int(inst_id), None, min_sat, min_act)
    )

conn.commit()
print("Accepts inserted!")


cur.close()
conn.close()
print("Connection closed.")