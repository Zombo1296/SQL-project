CREATE TABLE `Artist` (
  `aid` char(22) NOT NULL,
  `aname` varchar(45) NOT NULL,
  `description` varchar(200) NOT NULL,
  PRIMARY KEY (`aname`),
  FULLTEXT KEY `anamedesc` (`aname`, `description`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `Track` (
  `tid` char(22) NOT NULL,
  `title` varchar(45) NOT NULL,
  `duration` int(11) NOT NULL,
  `by_aname` varchar(45) NOT NULL,
  `genre` varchar(45) NOT NULL,
  `alid` char(22) NOT NULL,
  PRIMARY KEY (`tid`),
  FULLTEXT KEY `title` (`title`),
  KEY `by_aname` (`by_aname`),
  CONSTRAINT `Track_ibfk_1` FOREIGN KEY (`by_aname`) REFERENCES `Artist` (`aname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `User` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `uname` varchar(45) NOT NULL,
  `nickname` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `password` varchar(10) NOT NULL,
  `city` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`uid`),
  UNIQUE KEY `uname` (`uname`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `Album` (
  `alid` char(22) NOT NULL,
  `title` varchar(200) NOT NULL,
  `time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `count` int(11),
  PRIMARY KEY (`alid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `Playlist` (
  `plid` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `count` int(11) NOT NULL,
  `by_uid` int(11) DEFAULT NULL,
  PRIMARY KEY (`plid`),
  KEY `by_uid` (`by_uid`),
  CONSTRAINT `Playlist_ibfk_1` FOREIGN KEY (`by_uid`) REFERENCES `User` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `Follow` (
  `uid` int(11) NOT NULL,
  `f_uid` int(11) NOT NULL,
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`uid`,`f_uid`),
  KEY `f_uid` (`f_uid`),
  CONSTRAINT `Follow_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `User` (`uid`),
  CONSTRAINT `Follow_ibfk_2` FOREIGN KEY (`f_uid`) REFERENCES `User` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `Likes` (
  `uid` int(11) NOT NULL,
  `aname` varchar(45) NOT NULL,
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`uid`,`time`),
  KEY `aname` (`aname`),
  CONSTRAINT `Likes_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `User` (`uid`),
  CONSTRAINT `Likes_ibfk_2` FOREIGN KEY (`aname`) REFERENCES `Artist` (`aname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `PlayHistory` (
  `uid` int(11) NOT NULL,
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tid` char(22) NOT NULL,
  PRIMARY KEY (`uid`,`time`),
  KEY `tid` (`tid`),
  CONSTRAINT `PlayHistory_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `User` (`uid`),
  CONSTRAINT `PlayHistory_ibfk_2` FOREIGN KEY (`tid`) REFERENCES `Track` (`tid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `Rating` (
  `uid` int(11) NOT NULL,
  `tid` char(22) NOT NULL,
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `rate` int(1) NOT NULL,
  PRIMARY KEY (`uid`,`tid`),
  KEY `tid` (`tid`),
  CONSTRAINT `Rating_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `User` (`uid`),
  CONSTRAINT `Rating_ibfk_2` FOREIGN KEY (`tid`) REFERENCES `Track` (`tid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;