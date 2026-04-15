-- CampusConnect Database Schema
-- CSDS 341 - Spring 2026
-- Caio Albuquerque (caio-a18)
--
-- Run this file first before loading any data.
-- Assumes you're connected to a database named campusconnect.
--   psql -d campusconnect -f schema.sql

DROP TABLE IF EXISTS SavedSchools CASCADE;
DROP TABLE IF EXISTS Offers CASCADE;
DROP TABLE IF EXISTS Accepts CASCADE;
DROP TABLE IF EXISTS Costs CASCADE;
DROP TABLE IF EXISTS isIn CASCADE;
DROP TABLE IF EXISTS Program CASCADE;
DROP TABLE IF EXISTS UserProfile CASCADE;
DROP TABLE IF EXISTS Institution CASCADE;
DROP TABLE IF EXISTS State CASCADE;


-- ============================================================
-- State
-- Stores U.S. states and the region they belong to.
-- StateCode is the standard 2-letter abbreviation (e.g. 'OH').
-- ============================================================

CREATE TABLE State (
    StateCode   CHAR(2)      NOT NULL,
    StateName   VARCHAR(50)  NOT NULL,
    Region      VARCHAR(50),            -- e.g. 'Midwest', 'Northeast', etc.

    PRIMARY KEY (StateCode)
);


-- ============================================================
-- Institution
-- Core info about each college or university.
-- Does NOT store state or cost info here — those live in the
-- relationship tables below (isIn, Costs).
-- ============================================================

CREATE TABLE Institution (
    InstitutionID   SERIAL          NOT NULL,
    Name            VARCHAR(200)    NOT NULL,
    -- 'Public' or 'Private' (nonprofit/for-profit handled separately if needed)
    Type            VARCHAR(20)     CHECK (Type IN ('Public', 'Private')),
    -- Enrollment size bucket — easier to filter on than raw numbers
    Size            VARCHAR(20)     CHECK (Size IN ('Small', 'Medium', 'Large')),
    WebsiteURL      VARCHAR(300),

    PRIMARY KEY (InstitutionID)
);


-- ============================================================
-- isIn  (relationship: Institution is located in State)
-- An institution can only be in one state, so this is a
-- one-to-many relationship mapped as its own table.
-- ============================================================

CREATE TABLE isIn (
    InstitutionID   INT         NOT NULL,
    StateCode       CHAR(2)     NOT NULL,

    PRIMARY KEY (InstitutionID),
    FOREIGN KEY (InstitutionID) REFERENCES Institution(InstitutionID) ON DELETE CASCADE,
    FOREIGN KEY (StateCode)     REFERENCES State(StateCode)
);


-- ============================================================
-- Costs  (relationship: Institution has tuition/cost info)
-- Storing in-state vs out-of-state tuition separately because
-- that's one of the most common search filters.
-- ============================================================

CREATE TABLE Costs (
    InstitutionID       INT         NOT NULL,
    TuitionInState      INT,            -- annual in-state tuition in USD
    TuitionOutOfState   INT,            -- annual out-of-state tuition in USD
    RoomAndBoard        INT,            -- annual room and board cost in USD

    PRIMARY KEY (InstitutionID),
    FOREIGN KEY (InstitutionID) REFERENCES Institution(InstitutionID) ON DELETE CASCADE
);


-- ============================================================
-- Accepts  (relationship: Institution has admissions criteria)
-- Min values represent the rough lower bound a school accepts.
-- NULL means the school doesn't use that metric (test-optional, etc.)
-- ============================================================

CREATE TABLE Accepts (
    InstitutionID   INT             NOT NULL,
    MinGPA          DECIMAL(3, 2),      -- e.g. 3.50
    MinSAT          INT,                -- combined score out of 1600
    MinACT          INT,                -- composite score out of 36

    PRIMARY KEY (InstitutionID),
    FOREIGN KEY (InstitutionID) REFERENCES Institution(InstitutionID) ON DELETE CASCADE
);


-- ============================================================
-- Program
-- CIP (Classification of Instructional Programs) codes.
-- These are standardized across all U.S. institutions.
-- ============================================================

CREATE TABLE Program (
    ProgramCode     VARCHAR(10)     NOT NULL,   -- e.g. '14.0901' for Computer Engineering
    ProgramName     VARCHAR(200)    NOT NULL,
    Field           VARCHAR(100),               -- broad category, e.g. 'Engineering'

    PRIMARY KEY (ProgramCode)
);


-- ============================================================
-- Offers  (relationship: Institution offers Program)
-- This is a many-to-many relationship.
-- One institution offers many programs; one program can be
-- offered at many institutions.
-- ============================================================

CREATE TABLE Offers (
    InstitutionID   INT         NOT NULL,
    ProgramCode     VARCHAR(10) NOT NULL,

    PRIMARY KEY (InstitutionID, ProgramCode),
    FOREIGN KEY (InstitutionID) REFERENCES Institution(InstitutionID) ON DELETE CASCADE,
    FOREIGN KEY (ProgramCode)   REFERENCES Program(ProgramCode)
);


-- ============================================================
-- UserProfile
-- Stores registered users and their academic stats.
-- The academic stats (GPA, test scores) are used to match
-- users to schools they'd likely get into.
-- Real users would need hashed passwords — for the scope of
-- this project we're keeping auth simple.
-- ============================================================

CREATE TABLE UserProfile (
    UserID          SERIAL          NOT NULL,
    Name            VARCHAR(100)    NOT NULL,
    Email           VARCHAR(150)    NOT NULL UNIQUE,
    Password        VARCHAR(200),               -- would be hashed in production
    GPA             DECIMAL(3, 2),
    SATScore        INT,
    ACTScore        INT,
    PreferredState  CHAR(2),                    -- which state they want to study in

    PRIMARY KEY (UserID),
    FOREIGN KEY (PreferredState) REFERENCES State(StateCode)
);


-- ============================================================
-- SavedSchools  (relationship: User saves Institution)
-- Many-to-many between users and institutions.
-- SavedDate lets us sort the list by when they bookmarked it.
-- ============================================================

CREATE TABLE SavedSchools (
    UserID          INT     NOT NULL,
    InstitutionID   INT     NOT NULL,
    SavedDate       DATE    DEFAULT CURRENT_DATE,

    PRIMARY KEY (UserID, InstitutionID),
    FOREIGN KEY (UserID)        REFERENCES UserProfile(UserID) ON DELETE CASCADE,
    FOREIGN KEY (InstitutionID) REFERENCES Institution(InstitutionID) ON DELETE CASCADE
);


-- ============================================================
-- Indexes
-- These speed up the filters users are most likely to run.
-- ============================================================

-- Tuition filters are very common so index both tuition columns
CREATE INDEX idx_costs_tuition_in    ON Costs(TuitionInState);
CREATE INDEX idx_costs_tuition_out   ON Costs(TuitionOutOfState);

-- State lookups happen on almost every search
CREATE INDEX idx_isin_state          ON isIn(StateCode);

-- GPA/test score matching
CREATE INDEX idx_accepts_gpa         ON Accepts(MinGPA);
CREATE INDEX idx_accepts_sat         ON Accepts(MinSAT);

-- Looking up saved schools for a user
CREATE INDEX idx_saved_user          ON SavedSchools(UserID);
