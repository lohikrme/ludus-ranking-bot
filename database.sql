-- database.sql 
-- updated 6th october 2024

-- NOTE: THIS DATABASE IS BASED ON POSTGRE RELATIONAL DATABASE

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
    clan_id INT DEFAULT 1,
    FOREIGN KEY (clan_id) REFERENCES clans(id));

-- after creating clabs, add one clan with id = 1, clanname = "none", because some commands are based on on "old clan"
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
    opponent_clan_id INT NOT NULL,
    challenger_score INT DEFAULT 0 NOT NULL,
    opponent_score INT DEFAULT 0 NOT NULL,
    FOREIGN KEY (challenger_clan_id) REFERENCES clans(id),
    FOREIGN KEY (opponent_clan_id) REFERENCES clans(id));

CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(100) NOT NULL,
    FOREIGN KEY (discord_id) REFERENCES players(discord_id));


-- example: 
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


CREATE TABLE guilds (
    id VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL
);

-- so far 3 discord servers are using the bot, in future marchia and others will join
INSERT INTO guilds(id, name) VALUES ('1060303582487908423', 'middle-earth');
INSERT INTO guilds(id, name) VALUES ('1194360639544635482', 'legion');
INSERT INTO guilds(id, name) VALUES ('1274726630668894249', 'valkyrie');