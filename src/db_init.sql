-- На боевом сервере будет не localhost, а ip сервера

CREATE USER 'stuffman'@'localhost' IDENTIFIED BY 'stuff';
create database shabilka_db;
GRANT DELETE, INSERT, SELECT, UPDATE ON shabilka_db.* TO 'stuffman'@'localhost';
use shabilka_db;


CREATE TABLE IF NOT EXISTS shabilka_db.recipes (
  id VARCHAR(255) PRIMARY KEY,
  description TEXT,
  template TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shabilka_db.alphas (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  md5hash VARCHAR(255) UNIQUE,
  author VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP(),
  submittable BOOLEAN DEFAULT FALSE,
  submitted BOOLEAN DEFAULT FALSE,
  submitted_time DATETIME DEFAULT '1970-01-01 00:00:01',
  recipe_id VARCHAR(255),
  INDEX `md5hash_index` (`md5hash`),
  CONSTRAINT FOREIGN KEY `recipes_foreign_key` (`recipe_id`) REFERENCES recipes(`id`)
);

CREATE TABLE IF NOT EXISTS shabilka_db.alphas_stats (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  alpha_id INTEGER NOT NULL,
  year VARCHAR(50) NOT NULL COMMENT 'Just year in format like 2018. Or 2007-2017 for the final report',
  fitness FLOAT,
  returns FLOAT COMMENT 'Percent',
  sharpe FLOAT,
  long_count INTEGER,
  short_count INTEGER,
  margin FLOAT COMMENT 'bpm',
  turn_over FLOAT COMMENT 'Percent',
  draw_down FLOAT COMMENT 'Percent',
  booksize FLOAT COMMENT 'Millions',
  pnl FLOAT COMMENT 'Millions',
  CONSTRAINT FOREIGN KEY `alphas_foreign_key` (`alpha_id`) REFERENCES alphas(`id`)
);