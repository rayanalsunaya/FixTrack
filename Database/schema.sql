-- ============================================================
-- FixTrack Database Schema (SQLite)
-- ============================================================
-- 6 tables total:
-- 1. users              -> app accounts
-- 2. vehicles           -> cars owned by a user
-- 3. usage_patterns     -> the 8 fixed usage patterns (lookup/reference table)
-- 4. vehicle_profile    -> one row per vehicle: chosen pattern, preferred
--                          interval, and the LEARNED usage rate (this is
--                          what the AI model updates over time )
-- 5. maintenance_records-> every time the user taps "Done"
-- 6. predictions_log    -> history of predicted-vs-actual dates, used to
--                          measure how accurate the model becomes over time
--                          
-- ============================================================


-- ------------------------------------------------------------
-- 1. USERS
-- Basic account table. Password is never stored in plain text —
-- password_hash holds the output of a hashing function (e.g. bcrypt),
-- computed in the Python code, never the raw password itself.
-- ------------------------------------------------------------
CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ------------------------------------------------------------
-- 2. VEHICLES
-- A user can own more than one vehicle (FK user_id), matching
-- survey question 4 ("how many vehicles do you own?").
-- current_mileage is the last known odometer reading.
-- ------------------------------------------------------------
CREATE TABLE vehicles (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    make                TEXT,
    model               TEXT,
    year                INTEGER,
    plate_number        TEXT,
    current_mileage     INTEGER DEFAULT 0,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- ------------------------------------------------------------
-- 3. USAGE_PATTERNS  (reference/lookup table — 8 fixed rows)
-- This is the same 8 patterns from the onboarding questionnaire
-- and the research survey (Q5). estimated_km_per_day is the
-- DEFAULT starting rate used for a brand-new vehicle with no
-- service history yet — this is what solves the "cold start"
-- problem: instead of guessing from nothing, we start from a
-- population-level average for that pattern.
-- ------------------------------------------------------------
CREATE TABLE usage_patterns (
    id                      INTEGER PRIMARY KEY,
    pattern_name_ar         TEXT NOT NULL,
    pattern_name_en         TEXT NOT NULL,
    estimated_km_per_day    REAL NOT NULL
);


-- ------------------------------------------------------------
-- 4. VEHICLE_PROFILE
-- One row per vehicle (UNIQUE vehicle_id). This is the table the
-- AI logic reads and writes most often:
--   - usage_pattern_id + preferred_interval_km: set ONCE by the
--     user during onboarding (this was the whole point of my
--     "set it once" requirement).
--   - current_usage_rate: starts as a COPY of the pattern's
--     estimated_km_per_day, then gets adjusted after every
--     "Done" tap (this is the adaptive learning part).
--   - last_service_date / last_service_mileage: needed to
--     calculate the next predicted date.
-- ------------------------------------------------------------
CREATE TABLE vehicle_profile (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id              INTEGER NOT NULL UNIQUE,
    usage_pattern_id        INTEGER NOT NULL,
    preferred_interval_km   INTEGER NOT NULL,
    current_usage_rate      REAL NOT NULL,
    last_service_date       DATE,
    last_service_mileage    INTEGER,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (usage_pattern_id) REFERENCES usage_patterns(id)
);


-- ------------------------------------------------------------
-- 5. MAINTENANCE_RECORDS
-- One row every time the user taps "Done ✅" on a reminder.
-- predicted_date is copied from what we predicted BEFORE they
-- tapped done — comparing it to service_date later is how we
-- measure prediction error.
--
-- cost is OPTIONAL (nullable) — the user can skip entering it.
-- This is the foundation for the future "expense tracking" and
-- "price comparison" features: once enough users log real costs,
-- the average cost per service type becomes a benchmark for other
-- users can compare their own quote against.
-- ------------------------------------------------------------
CREATE TABLE maintenance_records (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id          INTEGER NOT NULL,
    service_date         DATE NOT NULL,
    mileage_at_service  INTEGER,
    predicted_date       DATE,
    cost                REAL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);


-- ------------------------------------------------------------
-- 6. PREDICTIONS_LOG
-- Every time the model (re)computes a prediction, we log it here.
-- actual_date stays NULL until the corresponding "Done" happens.
-- This table is what lets me plot "predicted vs actual" charts
-- in my report to show the model improving over time.
-- ------------------------------------------------------------
CREATE TABLE predictions_log (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id          INTEGER NOT NULL,
    predicted_date      DATE NOT NULL,
    actual_date         DATE,
    usage_rate_used     REAL NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);
