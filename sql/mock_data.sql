-- 2 states
INSERT INTO State VALUES ('OH', 'Ohio', 'Midwest');
INSERT INTO State VALUES ('CA', 'California', 'West');

-- 2 institutions
INSERT INTO Institution (Name, Type, Size, WebsiteURL)
VALUES ('Ohio State University', 'Public', 'Large', 'https://osu.edu');
INSERT INTO Institution (Name, Type, Size, WebsiteURL)
VALUES ('Case Western Reserve University', 'Private', 'Medium', 'https://case.edu');

-- Link them to states (InstitutionID will be 1 and 2 from SERIAL)
INSERT INTO isIn VALUES (1, 'OH');
INSERT INTO isIn VALUES (2, 'OH');

-- Costs
INSERT INTO Costs VALUES (1, 11936, 32061, 12000);
INSERT INTO Costs VALUES (2, 58644, 58644, 15000);

-- Admissions
INSERT INTO Accepts VALUES (1, 3.50, 1200, 27);
INSERT INTO Accepts VALUES (2, 3.70, 1400, 32);

-- 1 program
INSERT INTO Program VALUES ('11.0701', 'Computer Science', 'Engineering');

-- Link programs to schools
INSERT INTO Offers VALUES (1, '11.0701');
INSERT INTO Offers VALUES (2, '11.0701');

-- 1 user
INSERT INTO UserProfile (Name, Email, Password, GPA, SATScore, ACTScore, PreferredState)
VALUES ('Test Student', 'test@test.com', 'pass', 3.60, 1300, 29, 'OH');

-- Save a school for that user
INSERT INTO SavedSchools (UserID, InstitutionID) VALUES (1, 1);