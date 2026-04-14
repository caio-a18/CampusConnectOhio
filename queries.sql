-- ============================================================
-- Author: Dilan
-- Purpose: Core queries for CampusConnect
-- ============================================================

-- 1. View all institutions with full info
SELECT
    i.InstitutionID,
    i.Name,
    i.Type,
    i.Size,
    s.StateCode,
    s.StateName,
    c.TuitionInState,
    c.TuitionOutOfState,
    c.RoomAndBoard,
    a.MinGPA,
    a.MinSAT,
    a.MinACT,
    i.WebsiteURL
FROM Institution i
JOIN isIn ii ON i.InstitutionID = ii.InstitutionID
JOIN State s ON ii.StateCode = s.StateCode
LEFT JOIN Costs c ON i.InstitutionID = c.InstitutionID
LEFT JOIN Accepts a ON i.InstitutionID = a.InstitutionID
ORDER BY i.Name;


-- 2. Filter schools by state
-- Example: Ohio ('OH')
SELECT
    i.InstitutionID,
    i.Name,
    i.Type,
    i.Size,
    s.StateCode,
    i.WebsiteURL
FROM Institution i
JOIN isIn ii ON i.InstitutionID = ii.InstitutionID
JOIN State s ON ii.StateCode = s.StateCode
WHERE s.StateCode = 'OH'
ORDER BY i.Name;


-- 3. Filter by tuition range
-- Example: mid-range schools ($10k–$25k)
SELECT
    i.InstitutionID,
    i.Name,
    s.StateCode,
    c.TuitionInState,
    c.TuitionOutOfState
FROM Institution i
JOIN isIn ii ON i.InstitutionID = ii.InstitutionID
JOIN State s ON ii.StateCode = s.StateCode
JOIN Costs c ON i.InstitutionID = c.InstitutionID
WHERE c.TuitionInState BETWEEN 10000 AND 25000
ORDER BY c.TuitionInState ASC;


-- 4. Filter by school size
-- Example: Medium schools
SELECT
    i.InstitutionID,
    i.Name,
    i.Size,
    s.StateCode
FROM Institution i
JOIN isIn ii ON i.InstitutionID = ii.InstitutionID
JOIN State s ON ii.StateCode = s.StateCode
WHERE i.Size = 'Medium'
ORDER BY i.Name;


-- 5. Match schools based on student stats
-- Example student: GPA 3.5, SAT 1200, ACT 25
SELECT
    i.InstitutionID,
    i.Name,
    s.StateCode,
    a.MinGPA,
    a.MinSAT,
    a.MinACT
FROM Institution i
JOIN Accepts a ON i.InstitutionID = a.InstitutionID
JOIN isIn ii ON i.InstitutionID = ii.InstitutionID
JOIN State s ON ii.StateCode = s.StateCode
WHERE (a.MinGPA IS NULL OR a.MinGPA <= 3.50)
  AND (a.MinSAT IS NULL OR a.MinSAT <= 1200)
  AND (a.MinACT IS NULL OR a.MinACT <= 25)
ORDER BY i.Name;

-- 6. Find schools offering programs in a specific field
-- Example: Engineering
SELECT DISTINCT
    i.InstitutionID,
    i.Name,
    s.StateCode,
    p.ProgramName,
    p.Field
FROM Institution i
JOIN Offers o ON i.InstitutionID = o.InstitutionID
JOIN Program p ON o.ProgramCode = p.ProgramCode
JOIN isIn ii ON i.InstitutionID = ii.InstitutionID
JOIN State s ON ii.StateCode = s.StateCode
WHERE p.Field = 'Engineering'
ORDER BY i.Name, p.ProgramName;

-- 7. View a user profile
-- Example: UserID = 1
SELECT
    UserID,
    Name,
    Email,
    GPA,
    SATScore,
    ACTScore,
    PreferredState
FROM UserProfile
WHERE UserID = 1;


-- 8. View saved schools for a user
-- Example: UserID = 1
SELECT
    u.UserID,
    u.Name AS UserName,
    i.InstitutionID,
    i.Name AS InstitutionName,
    ss.SavedDate
FROM SavedSchools ss
JOIN UserProfile u ON ss.UserID = u.UserID
JOIN Institution i ON ss.InstitutionID = i.InstitutionID
WHERE u.UserID = 1
ORDER BY ss.SavedDate DESC;


-- 9. Save a school (example values)
INSERT INTO SavedSchools (UserID, InstitutionID, SavedDate)
VALUES (1, 10, CURRENT_DATE);


-- 10. Remove a saved school
DELETE FROM SavedSchools
WHERE UserID = 1
  AND InstitutionID = 10;


-- 11. Count institutions per state
SELECT
    s.StateCode,
    s.StateName,
    COUNT(i.InstitutionID) AS InstitutionCount
FROM State s
JOIN isIn ii ON s.StateCode = ii.StateCode
JOIN Institution i ON ii.InstitutionID = i.InstitutionID
GROUP BY s.StateCode, s.StateName
ORDER BY InstitutionCount DESC;


-- 12. Count programs per institution
SELECT
    i.InstitutionID,
    i.Name,
    COUNT(o.ProgramCode) AS ProgramCount
FROM Institution i
LEFT JOIN Offers o ON i.InstitutionID = o.InstitutionID
GROUP BY i.InstitutionID, i.Name
ORDER BY ProgramCount DESC, i.Name;