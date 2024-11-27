-- database.sql 
-- updated 25th october 2024

-- NOTE: THIS DATABASE IS BASED ON POSTGRE RELATIONAL DATABASE

-- check if database already exists, if not, create ludus database
DO $$ 
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ludus') THEN
      CREATE DATABASE ludus;
   END IF;
END
$$;

-- connect to ludus database
\connect ludus;

-- add clans table and a default clan which is used as none value
CREATE TABLE clans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    points INT DEFAULT 1000 NOT NULL,
    old_points INT DEFAULT 1000 NOT NULL,
    battles INT DEFAULT 0 NOT NULL,
    wins INT DEFAULT 0 NOT NULL,
    average_enemy_rank NUMERIC(12, 6) DEFAULT 1000.000000 NOT NULL);

-- insert a default clan, and then the most important active clans as pre-registered
INSERT INTO clans (name, points, old_points, average_enemy_rank) VALUES ('none', 0, 0, 0);
INSERT INTO clans (name) VALUES ('AG');
INSERT INTO clans (name) VALUES ('Dragons');
INSERT INTO clans (name) VALUES ('GRE');
INSERT INTO clans (name) VALUES ('Imperium');
INSERT INTO clans (name) VALUES ('LH');
INSERT INTO clans (name) VALUES ('LastAlive');
INSERT INTO clans (name) VALUES ('Legion');
INSERT INTO clans (name) VALUES ('Legion_SVD');
INSERT INTO clans (name) VALUES ('Marchia');
INSERT INTO clans (name) VALUES ('Mordor');
INSERT INTO clans (name) VALUES ('Meow');
INSERT INTO clans (name) VALUES ('MoB');
INSERT INTO clans (name) VALUES ('NoH');
INSERT INTO clans (name) VALUES ('RS');
INSERT INTO clans (name) VALUES ('VK');
INSERT INTO clans (name) VALUES ('Valkyrie');
INSERT INTO clans (name) VALUES ('WW');

-- create players table
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(100) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL,
    nickname VARCHAR(100) NOT NULL,
    registration_date DATE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    points INT DEFAULT 1000 NOT NULL,
    old_points INT DEFAULT 1000 NOT NULL,
    battles INT DEFAULT 0 NOT NULL,
    wins INT DEFAULT 0 NOT NULL,
    average_enemy_rank NUMERIC(12, 6) DEFAULT 1000.000000 NOT NULL,
    clan_id INT DEFAULT 1,
    FOREIGN KEY (clan_id) REFERENCES clans(id));

-- add clanwars table
CREATE TABLE clanwars (
    id SERIAL PRIMARY KEY, 
    date DATE NOT NULL,
    challenger_clan_id INT NOT NULL,
    opponent_clan_id INT NOT NULL,
    challenger_score INT DEFAULT 0 NOT NULL,
    opponent_score INT DEFAULT 0 NOT NULL,
    FOREIGN KEY (challenger_clan_id) REFERENCES clans(id),
    FOREIGN KEY (opponent_clan_id) REFERENCES clans(id));

-- add admins table
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(100) NOT NULL,
    FOREIGN KEY (discord_id) REFERENCES players(discord_id));

-- add duels table
-- example how duels table works (so timestamp etc. won't cause confusion): 
-- INSERT INTO duels (date, challenger_discord_id, opponent_discord_id, challenger_score, opponent_score) 
-- VALUES ('2024-9-12 20:30:00', '1234', '9876', 3, 7);
CREATE TABLE duels (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    challenger_discord_id VARCHAR(100) NOT NULL,
    opponent_discord_id VARCHAR(100) NOT NULL,
    challenger_score INT NOT NULL,
    opponent_score INT NOT NULL,
    FOREIGN KEY (challenger_discord_id) REFERENCES players(discord_id),
    FOREIGN KEY (opponent_discord_id) REFERENCES players(discord_id));

-- add guilds table
CREATE TABLE guilds (
    id VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL
);

-- add already registered guilds into the datatable
INSERT INTO guilds(id, name) VALUES ('1060303582487908423', 'middle-earth');
INSERT INTO guilds(id, name) VALUES ('1194360639544635482', 'legion');
INSERT INTO guilds(id, name) VALUES ('1274726630668894249', 'valkyrie');
INSERT INTO guilds (id, name) VALUES ('1225059828318343191', 'ludus-community');