SET foreign_key_checks = 0;
DROP TABLE IF EXISTS movie;
SET foreign_key_checks = 1;
CREATE TABLE movie (
	mv_code INT PRIMARY KEY,
	mv_name TINYTEXT,
    altname TINYTEXT,
    playtime INT,
    release_date DATE,
    watched_rating_num INT,
    watched_rating FLOAT,
    commentor_rating INT,
    netizen_rating_num INT,
    netizen_rating FLOAT,
    director_short TINYTEXT,
    country_short TINYTEXT,
    actor_short TEXT,
    grade_short TEXT,
    poster_url TEXT,
    mv_year INT,
    story text
);

SET foreign_key_checks = 0;
DROP TABLE IF EXISTS actor;
SET foreign_key_checks = 1;
CREATE TABLE actor (
	ac_code INT PRIMARY KEY,
	ac_name TINYTEXT,
    img_url TEXT
);

SET foreign_key_checks = 0;
DROP TABLE IF EXISTS director;
SET foreign_key_checks = 1;

CREATE TABLE director (
	dr_code INT PRIMARY KEY,
	dr_name TINYTEXT,
    img_url TEXT
);

SET foreign_key_checks = 0;
DROP TABLE IF EXISTS reply;
SET foreign_key_checks = 1;
CREATE TABLE reply (
	mv_code INT,
	star INT,
    good INT,
    bad INT,
    reple Text,
    FOREIGN KEY (mv_code) REFERENCES movie(mv_code)
		ON UPDATE CASCADE
        ON DELETE CASCADE
);

DROP TABLE IF EXISTS who_directed;
CREATE TABLE who_directed (
	mv_code INT NOT NULL,
    dr_code INT NOT NULL,
    PRIMARY KEY(mv_code,dr_code),
    FOREIGN KEY (mv_code) REFERENCES movie(mv_code)
		ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (dr_code) REFERENCES director(dr_code)
		ON UPDATE CASCADE
        ON DELETE CASCADE
);

DROP TABLE IF EXISTS who_acted;
CREATE TABLE who_acted (
	mv_code INT NOT NULL,
    ac_code INT NOT NULL,
    ismain INT DEFAULT NULL,
    ac_role TINYTEXT,
    PRIMARY KEY(mv_code,ac_code),
    FOREIGN KEY (mv_code) REFERENCES movie(mv_code)
		ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (ac_code) REFERENCES actor(ac_code)
		ON UPDATE CASCADE
        ON DELETE CASCADE
);

DROP TABLE IF EXISTS where_made;
CREATE TABLE where_made (
	mv_code INT NOT NULL,
    country TINYTEXT NOT NULL,
    FOREIGN KEY (mv_code) REFERENCES movie(mv_code)
		ON UPDATE CASCADE
        ON DELETE CASCADE
);

DROP TABLE IF EXISTS what_grade;
CREATE TABLE what_grade (
	mv_code INT NOT NULL,
    grade TINYTEXT NOT NULL,
    FOREIGN KEY (mv_code) REFERENCES movie(mv_code)
		ON UPDATE CASCADE
        ON DELETE CASCADE
);