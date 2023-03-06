CREATE TABLE `Users` ( `id` int(10) NOT NULL ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
CREATE TABLE `Tags` ( `id` int(9) NOT NULL, `tag` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
CREATE TABLE `News` ( `News` varchar(500) NOT NULL, `Link` varchar(500) NOT NULL, `Tags` varchar(250) NOT NULL, `Datepublisher` int(200) NOT NULL, `DateInsert` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
