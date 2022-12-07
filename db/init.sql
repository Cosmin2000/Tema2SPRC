-- DROP DATABASE IF EXISTS meteo_db;
-- CREATE DATABASE meteo_db;

CREATE TABLE IF NOT EXISTS Tari (
    id SERIAL PRIMARY KEY,
    nume_tara VARCHAR(30) UNIQUE NOT NULL,
    latitudine NUMERIC(10,3) NOT NULL,
    longitudine NUMERIC(10,3) NOT NULL
);

CREATE TABLE IF NOT  EXISTS Orase (
    id SERIAL PRIMARY KEY,
    id_tara INT NOT NULL,
    nume_oras VARCHAR(30) NOT NULL,
    latitudine NUMERIC(10,3) NOT NULL,
    longitudine NUMERIC(10,3) NOT NULL,
    UNIQUE(id_tara, nume_oras),
    CONSTRAINT fk_tara FOREIGN KEY(id_tara) REFERENCES Tari(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Temperaturi (
    id SERIAL PRIMARY KEY,
    valoare NUMERIC(10,3) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    id_oras INT NOT NULL,
    UNIQUE(id_oras, timestamp),
    CONSTRAINT fk_oras FOREIGN KEY(id_oras) REFERENCES Orase(id) ON DELETE CASCADE
);