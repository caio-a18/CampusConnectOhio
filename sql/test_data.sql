-- ============================================================
-- CampusConnect Test Data
-- CSDS 341 - Spring 2026
-- Tommaso Beretta (txb341)
--
-- Run this file after schema.sql to load test data.
-- Safe to re-run — truncates all tables first.
--   psql -d campusconnect -f sql/test_data.sql
-- ============================================================

-- Wipe all tables and reset auto-increment IDs
TRUNCATE State, Institution, isIn, Costs, Accepts, Program, Offers, UserProfile, SavedSchools
    RESTART IDENTITY CASCADE;


-- ============================================================
-- States
-- ============================================================

INSERT INTO State (StateCode, StateName, Region) VALUES
    ('OH', 'Ohio',       'Midwest'),
    ('CA', 'California', 'West'),
    ('NY', 'New York',   'Northeast'),
    ('TX', 'Texas',      'South'),
    ('MI', 'Michigan',   'Midwest');


-- ============================================================
-- Institutions
-- ============================================================

INSERT INTO Institution (Name, Type, Size, WebsiteURL) VALUES
    ('Ohio State University',                'Public',  'Large',  'https://osu.edu'),
    ('Case Western Reserve University',      'Private', 'Medium', 'https://case.edu'),
    ('University of Michigan',               'Public',  'Large',  'https://umich.edu'),
    ('Ohio University',                      'Public',  'Medium', 'https://ohio.edu'),
    ('Oberlin College',                      'Private', 'Small',  'https://oberlin.edu'),
    ('Bowling Green State University',       'Public',  'Medium', 'https://bgsu.edu'),
    ('University of California Berkeley',    'Public',  'Large',  'https://berkeley.edu'),
    ('New York University',                  'Private', 'Large',  'https://nyu.edu'),
    ('University of Texas at Austin',        'Public',  'Large',  'https://utexas.edu'),
    ('Texas A&M University',                 'Public',  'Large',  'https://tamu.edu'),
    ('Stanford University',                  'Private', 'Medium', 'https://stanford.edu'),
    ('University of California Los Angeles', 'Public',  'Large',  'https://ucla.edu'),
    ('Columbia University',                  'Private', 'Medium', 'https://columbia.edu'),
    ('Fordham University',                   'Private', 'Medium', 'https://fordham.edu'),
    ('Rice University',                      'Private', 'Medium', 'https://rice.edu'),
    ('Michigan State University',            'Public',  'Large',  'https://msu.edu'),
    ('Kenyon College',                       'Private', 'Small',  'https://kenyon.edu'),
    ('University of Michigan-Dearborn',      'Public',  'Medium', 'https://umd.umich.edu');


-- ============================================================
-- isIn (Institution → State)
-- ============================================================

INSERT INTO isIn (InstitutionID, StateCode) VALUES
    (1,  'OH'),
    (2,  'OH'),
    (3,  'MI'),
    (4,  'OH'),
    (5,  'OH'),
    (6,  'OH'),
    (7,  'CA'),
    (8,  'NY'),
    (9,  'TX'),
    (10, 'TX'),
    (11, 'CA'),
    (12, 'CA'),
    (13, 'NY'),
    (14, 'NY'),
    (15, 'TX'),
    (16, 'MI'),
    (17, 'OH'),
    (18, 'MI');


-- ============================================================
-- Costs (in USD per year)
-- ============================================================

INSERT INTO Costs (InstitutionID, TuitionInState, TuitionOutOfState, RoomAndBoard) VALUES
    (1,  11936, 32061, 13756),
    (2,  57750, 57750, 17000),
    (3,  15558, 52266, 13400),
    (4,  12192, 21334, 12000),
    (5,  62384, 62384, 16500),
    (6,  13012, 22066, 11800),
    (7,  14312, 44066, 19800),
    (8,  58072, 58072, 20000),
    (9,  11448, 40996, 12632),
    (10, 12413, 39227, 12200),
    (11, 61731, 61731, 18000),
    (12, 13401, 43473, 18000),
    (13, 65524, 65524, 21000),
    (14, 57722, 57722, 19500),
    (15, 54960, 54960, 16200),
    (16, 14460, 39766, 11600),
    (17, 55830, 55830, 14200),
    (18, 13758, 24206, 10800);


-- ============================================================
-- Accepts (admissions criteria)
-- NULL means test-optional or not reported
-- ============================================================

INSERT INTO Accepts (InstitutionID, MinGPA, MinSAT, MinACT) VALUES
    (1,  3.50, 1230, 27),
    (2,  3.75, 1450, 33),
    (3,  3.80, 1360, 32),
    (4,  3.20, 1060, 22),
    (5,  3.60, 1280, 29),
    (6,  3.10, 1020, 21),
    (7,  3.90, 1430, 34),
    (8,  3.65, 1350, 31),
    (9,  3.70, 1310, 29),
    (10, 3.60, 1220, 27),
    (11, 3.95, 1500, 35),
    (12, 3.85, 1370, 32),
    (13, 3.90, 1490, 34),
    (14, 3.55, 1240, 28),
    (15, 3.85, 1480, 34),
    (16, 3.30, 1100, 24),
    (17, 3.55, 1180, 26),
    (18, 3.10, 1020, 21);


-- ============================================================
-- Programs (CIP codes)
-- ============================================================

INSERT INTO Program (ProgramCode, ProgramName, Field) VALUES
    ('11.0101', 'Computer and Information Sciences', 'Computer Science'),
    ('14.0901', 'Computer Engineering',              'Engineering'),
    ('27.0101', 'Mathematics',                       'Mathematics'),
    ('52.0201', 'Business Administration',           'Business'),
    ('45.1001', 'Political Science',                 'Social Sciences');


-- ============================================================
-- Offers (Institution ↔ Program)
-- ============================================================

INSERT INTO Offers (InstitutionID, ProgramCode) VALUES
    (1,  '11.0101'), (1,  '14.0901'), (1,  '27.0101'), (1,  '52.0201'),
    (2,  '11.0101'), (2,  '14.0901'), (2,  '27.0101'),
    (3,  '11.0101'), (3,  '14.0901'), (3,  '52.0201'),
    (4,  '45.1001'), (4,  '52.0201'),
    (5,  '27.0101'), (5,  '45.1001'),
    (6,  '52.0201'),
    (7,  '11.0101'), (7,  '14.0901'),
    (8,  '45.1001'), (8,  '52.0201'),
    (9,  '11.0101'), (9,  '14.0901'), (9,  '45.1001'), (9,  '52.0201'),
    (10, '14.0901'), (10, '27.0101'), (10, '52.0201'),
    (11, '11.0101'), (11, '14.0901'), (11, '27.0101'),
    (12, '11.0101'), (12, '45.1001'), (12, '52.0201'),
    (13, '11.0101'), (13, '27.0101'), (13, '45.1001'),
    (14, '45.1001'), (14, '52.0201'),
    (15, '11.0101'), (15, '14.0901'), (15, '27.0101'),
    (16, '11.0101'), (16, '14.0901'), (16, '52.0201'),
    (17, '27.0101'), (17, '45.1001'),
    (18, '11.0101'), (18, '52.0201');


-- ============================================================
-- UserProfile (test users with varying academic stats)
-- ============================================================

INSERT INTO UserProfile (Name, Email, Password, GPA, SATScore, ACTScore, PreferredState) VALUES
    ('Alice Johnson', 'alice@test.com',  'pass', 3.90, 1480, 34, 'OH'),
    ('Bob Martinez',  'bob@test.com',    'pass', 3.50, 1220, 27, 'OH'),
    ('Claire Kim',    'claire@test.com', 'pass', 3.70, 1350, 30, 'CA'),
    ('David Patel',   'david@test.com',  'pass', 3.20, 1080, 22, 'MI'),
    ('Emma Wilson',   'emma@test.com',   'pass', 3.85, 1440, 33, 'NY');


-- ============================================================
-- SavedSchools
-- Alice: Case Western, Stanford, Columbia
-- Bob: Ohio State, Ohio University
-- Claire: UC Berkeley, Stanford, UCLA
-- David: Ohio University, Michigan State
-- Emma: NYU, Columbia
-- ============================================================

INSERT INTO SavedSchools (UserID, InstitutionID, SavedDate) VALUES
    (1, 2,  '2026-03-01'),
    (1, 11, '2026-03-05'),
    (1, 13, '2026-03-10'),
    (2, 1,  '2026-03-02'),
    (2, 4,  '2026-03-08'),
    (3, 7,  '2026-02-20'),
    (3, 11, '2026-02-25'),
    (3, 12, '2026-03-01'),
    (4, 4,  '2026-03-15'),
    (4, 16, '2026-03-15'),
    (5, 8,  '2026-03-03'),
    (5, 13, '2026-03-07');
