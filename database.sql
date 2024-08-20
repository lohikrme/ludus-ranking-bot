-- database.sql 
-- 20th august 2024

-- NOTE: DATABASE IS BASED ON POSTGRE RELATIONAL DATABASE


-- creation of identical database
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    points INT DEFAULT 1000 NOT NULL,
    nickname VARCHAR(100) NOT NULL,
    registration_date DATE NOT NULL,
    old_points INT DEFAULT 1000 NOT NULL,
    battles INT DEFAULT 0 NOT NULL,
    wins INT DEFAULT 0 NOT NULL,
    average_enemy_rank NUMERIC(12, 6) DEFAULT 0.000000 NOT NULL,
    clanname VARCHAR(100) DEFAULT NULL
);
