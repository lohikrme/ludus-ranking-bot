-- database.sql 
-- 20th august 2024

-- NOTE: DATABASE IS BASED ON POSTGRE RELATIONAL DATABASE


-- creation of identical database
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL,
    nickname VARCHAR(100) NOT NULL,
    registration_date DATE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    points INT DEFAULT 1000 NOT NULL,
    old_points INT DEFAULT 1000 NOT NULL,
    battles INT DEFAULT 0 NOT NULL,
    wins INT DEFAULT 0 NOT NULL,
    average_enemy_rank NUMERIC(12, 6) DEFAULT 1000.000000 NOT NULL,
    clan_id INT DEFAULT 1);

-- add one clan with id = 1, clanname = "none", points = 0, old_points = 0, average_enemyclan_rank = 0 at the start of creation
-- note that u must add this without manually specifying id, otherwise serialization wont work, and
-- later when people try to add clans, it will try to start again from 1
-- thats why this must also be done right after creation of the clans datatable
CREATE TABLE clans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    points INT DEFAULT 1000 NOT NULL,
    old_points INT DEFAULT 1000 NOT NULL,
    battles INT DEFAULT 0 NOT NULL,
    wins INT DEFAULT 0 NOT NULL,
    average_enemy_rank NUMERIC(12, 6) DEFAULT 1000.000000 NOT NULL);

INSERT INTO clans (name, points, old_points, average_enemy_rank) VALUES ('none', 0, 0, 0);


CREATE TABLE clanwars (
    id SERIAL PRIMARY KEY, 
    date DATE NOT NULL,
    challenger_clan_id INT NOT NULL,
    defender_clan_id INT NOT NULL,
    challenger_won_rounds INT DEFAULT 0 NOT NULL,
    defender_won_rounds INT DEFAULT 0 NOT NULL);

CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(100) NOT NULL);