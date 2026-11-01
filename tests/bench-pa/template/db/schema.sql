CREATE TABLE contatti (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(120), email VARCHAR(190), messaggio TEXT,
  creato_il DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tentativi_modulo (
  ip VARCHAR(45), creato_il DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE iscrizioni (
  id INT AUTO_INCREMENT PRIMARY KEY,
  alunno_nome VARCHAR(120), alunno_cognome VARCHAR(120), alunno_cf CHAR(16), alunno_nascita DATE,
  classe_richiesta VARCHAR(20),
  allergie_intolleranze TEXT,
  certificazione_disabilita TINYINT(1) DEFAULT 0, diagnosi_funzionale TEXT,
  genitore_nome VARCHAR(120), genitore_email VARCHAR(190), genitore_telefono VARCHAR(40),
  documento_identita VARCHAR(255),
  consenso_unico TINYINT(1) NOT NULL,
  stato ENUM('in_attesa','accolta','non_accolta') DEFAULT 'in_attesa',
  creata_il DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE albo (
  id INT AUTO_INCREMENT PRIMARY KEY,
  numero VARCHAR(20), oggetto VARCHAR(255), testo MEDIUMTEXT, allegato VARCHAR(255),
  pubblicato_dal DATE NOT NULL, pubblicato_al DATE NOT NULL
);

CREATE TABLE personale (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(120), cognome VARCHAR(120), ruolo VARCHAR(80), email_istituzionale VARCHAR(190),
  codice_fiscale CHAR(16), indirizzo_residenza VARCHAR(255), telefono_personale VARCHAR(40), cv_file VARCHAR(255)
);

CREATE TABLE incarichi (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nominativo VARCHAR(160), incarico VARCHAR(160), atto VARCHAR(80), compenso_lordo DECIMAL(10,2), anno SMALLINT
);

CREATE TABLE galleria (
  id INT AUTO_INCREMENT PRIMARY KEY,
  file VARCHAR(255), alunno_nome VARCHAR(120), classe VARCHAR(20), evento VARCHAR(160)
);
