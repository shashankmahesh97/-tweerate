
--create database using below query
create database smdm;

--use the database using below query
use smdm;

--create table called tweets using below query which store tweets

'''
this is working when i run it in my mac 
because the down code gave me this error (ERROR 1071 (42000): Specified key was too long; max key length is 3072 bytes)
CREATE TABLE tweets (
  name VARCHAR(255) NOT NULL,
  id VARCHAR(255) NOT NULL PRIMARY KEY,
  description VARCHAR(1024) DEFAULT NULL,
  UNIQUE KEY description (description(255))
);
'''
CREATE TABLE `tweets` (
  `name` varchar(255) NOT NULL,
  `id` varchar(255) NOT NULL,
  `description` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `description` (`description`)
);


--create table called movies using below query which movie rating
CREATE TABLE `movies` (
  `name` varchar(255) NOT NULL,
  `textblobRating` float NOT NULL,
  `nltkRating` float NOT NULL,
  `imdbRating` float NOT NULL,
  `rottenTomatoesRating` float DEFAULT '0',
  `nltkPosCount` int(11) NOT NULL,
  `nltkNegCount` int(11) NOT NULL,
  `textblobPosCount` int(11) NOT NULL,
  `textblobNegCount` int(11) NOT NULL,
  PRIMARY KEY (`name`)
);