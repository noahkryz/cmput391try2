#SQL STATEMENTS for Project - Unit 1
#NOT MOST RECENT - September 21 - Most updated version is in project.py

#5 TABLES TO CREATE
#node (id integer, lat float, lon float)
#way (id int, closed bit);
#nodetag (id integer, k text, v text)
#waytag  (id integer, k text, v text)
#waypoint (wayid integer, ordinal integer, nodeid integer)

#The following constraints should be enforced in the database:

#id is a primary key for way - DONE
#wayid in waypoint is a foreign key to way(id) - DONE
#nodeid in waypoint is a foreign key to node(id) - DONE
#ordinal in waypoint must be an integer between 0 and the number of nd elements in the path
#closed in way should be true if and only if the path is closed

CREATE table node(id int, lat float, lon float, PRIMARY KEY (id));

CREATE table way(id int, closed bit, PRIMARY KEY (id));

CREATE table nodetag(id int, k text, v text, PRIMARY KEY (id));

CREATE table waytag(id int, k text, v text, PRIMARY KEY (id));

CREATE table waypoint(wayid int, ordinal int, nodeid int, FOREIGN KEY (wayid) REFERENCES way(id), 
	FOREIGN KEY (nodeid) REFERENCES node(id), CHECK(ordinal >= 0));


INSERT into node values ({}, {}, {}).format(id, lat, lon);

WITH ord(wayid, nodeid) AS (
SELECT wayid, nodeid FROM waypoint WHERE ordinal = 0
),
maxord(val, wayid) AS (
SELECT max(ordinal), wayid FROM waypoint GROUP BY wayid
)
SELECT wp.wayid
FROM waypoint wp, way w, ord o, maxord mo
WHERE wp.wayid = w.id AND wp.ordinal = mo.val AND wp.nodeid = o.nodeid
GROUP BY wp.wayid;
#wp.wayid, wp.nodeid, o.nodeid