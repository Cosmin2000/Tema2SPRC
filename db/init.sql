-- DROP DATABASE IF EXISTS meteo_db;
-- CREATE DATABASE meteo_db;

CREATE TABLE IF NOT EXISTS Tari (
    id SERIAL PRIMARY KEY,
    nume_tara VARCHAR(30) UNIQUE NOT NULL,
    latitudine NUMERIC(10,2) NOT NULL,
    longitudine NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT  EXISTS Orase (
    id SERIAL PRIMARY KEY,
    id_tara INT NOT NULL,
    nume_oras INT NOT NULL,
    latitudine NUMERIC(10,2) NOT NULL,
    longitudine NUMERIC(10,2) NOT NULL,
    UNIQUE(id_tara, nume_oras)
);

CREATE TABLE IF NOT EXISTS Temperaturi (
    id SERIAL PRIMARY KEY,
    valoare NUMERIC(10,2) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    id_oras INT,
    UNIQUE(id_oras, timestamp),
    CONSTRAINT fk_oras FOREIGN KEY(id_oras) REFERENCES Orase(id) ON DELETE CASCADE
);