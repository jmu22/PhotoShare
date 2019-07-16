DROP DATABASE IF EXISTS photoshare;
CREATE DATABASE photoshare;
USE photoshare;

CREATE TABLE Users (
    user_id INT NOT NULL AUTO_INCREMENT,
    Fname VARCHAR(40) NOT NULL DEFAULT "DoJun",
    Lname VARCHAR(40) NOT NULL DEFAULT "Park",
    DOB DATE DEFAULT NULL,
    Hometown VARCHAR(255),
    gender VARCHAR(10),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255),
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);


CREATE TABLE Albums (
  album_id INT AUTO_INCREMENT,
  name VARCHAR(50),
  user_id INT NOT NULL,
  Date_created VARCHAR(50),
  picture_id INT,
  PRIMARY KEY (album_id),
  Foreign Key (user_id) REFERENCES Users(user_id)
);


CREATE TABLE Pictures (
  picture_id INT AUTO_INCREMENT,
  user_id INT NOT NULL,
  album_id int,
  imgdata LONGBLOB ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  PRIMARY KEY (picture_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id),
  FOREIGN KEY (album_id) REFERENCES Albums(album_id)
);

CREATE TABLE Comment(
	CID INT NOT NULL AUTO_INCREMENT,
	CONTENT VARCHAR(200) NOT NULL,
	DOC TIMESTAMP NOT NULL,
	UID INT NOT NULL,
	PID INT NOT NULL,
	PRIMARY KEY (CID),
	FOREIGN KEY (UID) REFERENCES Users(user_id) ON DELETE CASCADE,
	FOREIGN KEY (PID) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

CREATE TABLE Friendship(
	UID1 INT NOT NULL,
	UID2 INT NOT NULL,
	PRIMARY KEY(UID1, UID2),
	FOREIGN KEY (UID1) REFERENCES Users(user_id) ON DELETE CASCADE,
	FOREIGN KEY (UID2) REFERENCES Users(user_id) ON DELETE CASCADE
);


CREATE TABLE Likes (
    user_id INT NOT NULL,
    picture_id INT,
    name VARCHAR(40),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id)
);


CREATE TABLE Can_Make (
    user_id INT NOT NULL,
    album_id INT,
    PRIMARY KEY (user_id, album_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (album_id) REFERENCES Albums(album_id)
);


CREATE TABLE Can_Have (
    album_id INT,
    picture_id INT,
    PRIMARY KEY (album_id, picture_id),
    FOREIGN KEY (album_id) REFERENCES Albums(album_id),
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id)
);

CREATE TABLE Tag(
	tid INT NOT NULL AUTO_INCREMENT,
  tag_name VARCHAR(40) NOT NULL,
	PRIMARY KEY (tid)
);

-- CREATE Associate Table
CREATE TABLE Associate(
	pid INT NOT NULL,
	tid int,
  PRIMARY KEY (pid, tid),
	FOREIGN KEY (tid) REFERENCES Tag(tid) ON DELETE CASCADE,
	FOREIGN KEY (pid) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);


INSERT INTO Users (Fname, Lname, DOB, Hometown, gender, email, password) VALUES ('Do Jun', 'Park', '1997-04-01', 'Seoul', 'M', '2test@bu.edu', 'test');
INSERT INTO Users (Fname, Lname, DOB, Hometown, gender, email, password) VALUES ('Blah', 'Blahh', '1996-04-01', 'Los Angeles', 'F', '1test@bu.edu', 'test');
INSERT INTO Users (Fname, Lname, DOB, Hometown, gender, email, password) VALUES ('May', 'Fong', '1996-05-01', 'Thailand', 'F', 'fmay@bu.edu', 'test');
INSERT INTO Users (Fname, Lname, DOB, Hometown, gender, email, password) VALUES ('Charlie', 'Lyang', '1996-07-01', 'Amurica', 'F', 'yangc@bu.edu', 'test');