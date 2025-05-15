-- Créer les tables principales
CREATE TABLE IF NOT EXISTS train_sessions (
    session_id INT,
    item_id INT,
    date DATE,
    PRIMARY KEY (session_id, item_id)
);

CREATE TABLE IF NOT EXISTS train_purchases (
    session_id INT,
    item_id INT,
    date DATE,
    PRIMARY KEY (session_id, item_id)
);

-- Créer des tables temporaires pour éviter les doublons
CREATE TEMP TABLE temp_train_sessions (
    session_id INT,
    item_id INT,
    date DATE
);

CREATE TEMP TABLE temp_train_purchases (
    session_id INT,
    item_id INT,
    date DATE
);

-- Charger les données dans les tables temporaires
COPY temp_train_sessions(session_id, item_id, date)
FROM '/docker-entrypoint-initdb.d/train_sessions_1.csv'
DELIMITER ','
CSV HEADER;

COPY temp_train_purchases(session_id, item_id, date)
FROM '/docker-entrypoint-initdb.d/train_purchases_1.csv'
DELIMITER ','
CSV HEADER;

-- Insérer les données dans les tables principales sans doublons
INSERT INTO train_sessions(session_id, item_id, date)
SELECT session_id, item_id, date
FROM temp_train_sessions
ON CONFLICT (session_id, item_id) DO NOTHING;

INSERT INTO train_purchases(session_id, item_id, date)
SELECT session_id, item_id, date
FROM temp_train_purchases
ON CONFLICT (session_id, item_id) DO NOTHING;

-- Nettoyage des tables temporaires (optionnel, PostgreSQL s'en occupe automatiquement)
DROP TABLE IF EXISTS temp_train_sessions;
DROP TABLE IF EXISTS temp_train_purchases;
