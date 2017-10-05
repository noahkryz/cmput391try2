#CMPUT 391 - Project #1
#Due Date: October 9, 2017
#Noah Kryzanowski


#Different Cases for storing the values in the database
#Case #1: Node Extraction
#---node (id integer, lat float, lon float)---
#	From <node , extract:
#		id=""
#		lat=""
#		lon=""
#	Each node begins with <node, followed by the data, ending with />
#---WE NEED TO STORE THE <tag/> DATA AS WELL. SEE CASE #3.

#Case #2: Way Extraction
#---way (id integer, closed boolean)---
#	From <way , extract:
#		id=""
#		closed="boolean"
#
#

#Case #3: Tag Extraction (Node and Way)
#---nodetag (id integer, k text, v text)
#---waytag  (id integer, k text, v text)
#	From <tag , extract:
#		id=""
#		k=""
#		v=""
#	Each tag is nested in either <node (CASE #1) or <way (CASE #2)
#	Each tag begins with <tag, followed by the data, ending with />

# Triggers
# 1. When inserting a value into way, check if the first id (ordinality of 0) is equal to the last, therefore 
#	causing a trigger to go off and closing the path
# 2. When deleting a value from way, check if the first id (ordinality of 0) is no longer equal to the last, therefore
#	causing a trigger to go off and making the path open
#
#


import xml.etree.ElementTree as ET
import sqlite3

def main():
	#---HARDCODED FILE NAME---		
	#inputFile = 'small.xml'
	inputFile = 'edmonton.osm'
	tree = ET.parse(inputFile)
	root = tree.getroot()
	print("Finished parsing through the XML file")
	closed = ''
	limit = 10000

	node_values = []
	nodetag_values = []
	waypoint_values = []
	waytag_values = []
	way_values = []

	zero = []
	last = []
	items = []


#---DATABASE INITIALIZATION---
	conn = sqlite3.connect('edmonton.db')
	conn.isolation_level = None
	c = conn.cursor()
#---DROP TABLES---
	#c.execute("PRAGMA foreign_keys = ON")
	#c.execute("isolation_level=None")
	c.execute("PRAGMA synchronous=OFF")
	c.execute("DROP TABLE IF EXISTS waypoint")
	c.execute("DROP TABLE IF EXISTS waytag")
	c.execute("DROP TABLE IF EXISTS way")
	c.execute("DROP TABLE IF EXISTS nodetag")
	c.execute("DROP TABLE IF EXISTS node")
	
	
	
	
#---CREATE TABLES---
	node_statement = "CREATE table IF NOT EXISTS node(id int, lat float, lon float, PRIMARY KEY (id))"
	c.execute(node_statement)
	node_tag_statement = "CREATE table IF NOT EXISTS nodetag(id int, k text, v text, FOREIGN KEY (id) REFERENCES node(id))"
	c.execute(node_tag_statement)
	way_statement = "CREATE table IF NOT EXISTS way(id int, closed bit, PRIMARY KEY (id))"
	c.execute(way_statement)
	way_tag_statement = "CREATE table IF NOT EXISTS waytag(id int, k text, v text, FOREIGN KEY (id) REFERENCES way(id))"
	c.execute(way_tag_statement)
	waypoint_statement = "CREATE table IF NOT EXISTS waypoint(wayid int, ordinal int, nodeid int, FOREIGN KEY (wayid) REFERENCES way(id), FOREIGN KEY (nodeid) REFERENCES node(id), CHECK(ordinal >= 0))"
	c.execute(waypoint_statement)
#-------------------
	#conn.commit() #Maybe don't commit it everytime ? After every group of executes
	#conn.close()
#-----------------------------


	for node in root.iter('node'):

		node_id = node.get('id')
		lat = node.get('lat')
		lon = node.get('lon')
		node_values.append((node_id, lat, lon))

		if len(node_values) > limit:
			c.execute("BEGIN")
			statement = "INSERT into node values (?, ?, ?)"#.format(node_id, lat, lon)
			c.executemany(statement, node_values)
			c.execute("COMMIT")
			node_values = []

		for tag in node:

			tag_id = node_id
			tag_k = tag.get('k')
			tag_v = tag.get('v')
			nodetag_values.append((tag_id, tag_k, tag_v))

			if len(nodetag_values) > limit:
				c.execute("BEGIN")
				statement = "INSERT into nodetag values (?, ?, ?)"#.format(tag_id, tag_k, tag_v)
				c.executemany(statement, nodetag_values)
				c.execute("COMMIT")
				nodetag_values = []

	#conn.commit()
			

	for way in root.iter('way'):

		ordinality = 0
		way_id = way.get('id')

		for child in way:

			if child.tag == 'nd':

				waypoint_id = way_id
				node_id = child.get('ref') 
				waypoint_values.append((waypoint_id, ordinality, node_id))

				if len(waypoint_values) > limit:
					c.execute("BEGIN")
					statement = "INSERT into waypoint values (?, ?, ?)"#.format(waypoint_id, ordinality, node_id)		
					c.executemany(statement, waypoint_values)
					c.execute("COMMIT")
					waypoint_values = []

				ordinality = ordinality + 1
			
			if child.tag == 'tag':

				waytag_id = way_id
				waytag_k = child.get('k')
				waytag_v = child.get('v')
				waytag_values.append((waytag_id, waytag_k, waytag_v))

				if len(waytag_values) > limit:
					#print('Here')
					c.execute("BEGIN")
					statement = "INSERT into waytag values (?, ?, ?)"#.format(waytag_id, waytag_k, waytag_v)
					c.executemany(statement, waytag_values)
					c.execute("COMMIT")
					waytag_values = []

		#----------------------------------------------------
		# #c.execute("BEGIN")
		# statement = "SELECT nodeid from waypoint where ordinal = 0 AND wayid = {}".format(way_id)
		# ordinal_zero = c.execute(statement)
		# #c.execute("COMMIT")
		# #ordinal_zero = c.fetchall()
		# zero.append(ordinal_zero)
		# #print(zero)

		# #print(ordinal_zero)
		# #c.execute("BEGIN")
		# statement = "SELECT nodeid from waypoint where ordinal = {} AND wayid = {}".format(ordinality - 1, way_id)
		# ordinal_last = c.execute(statement)
		# #c.execute("COMMIT")
		# #ordinal_last = c.fetchmany()
		# last.append(ordinal_last)
		#print(ordinal_last, ordinality - 1)
		# if ordinal_zero == ordinal_last:
		#  	closed = 1
		# else:
		#  	closed = 0
		#----------------------------------------------------


		way_values.append((way_id, 0))

		if len(way_values) > limit:
			c.execute("BEGIN")
			statement = "INSERT into way values (?, ?)"#.format(way_id, closed)
			c.executemany(statement, way_values)
			c.execute("COMMIT")
			way_values = []

	c.execute("BEGIN")
	statement = "INSERT into node values (?, ?, ?)"#.format(node_id, lat, lon)
	c.executemany(statement, node_values)
	statement = "INSERT into nodetag values (?, ?, ?)"#.format(tag_id, tag_k, tag_v)
	c.executemany(statement, nodetag_values)
	statement = "INSERT into waypoint values (?, ?, ?)"#.format(waypoint_id, ordinality, node_id)		
	c.executemany(statement, waypoint_values)
	statement = "INSERT into waytag values (?, ?, ?)"#.format(waytag_id, waytag_k, waytag_v)
	c.executemany(statement, waytag_values)
	statement = "INSERT into way values (?, ?)"#.format(way_id, closed)
	c.executemany(statement, way_values)
	c.execute("COMMIT")
	
	#statement = "WITH ord(wayid, nodeid) AS (SELECT wayid, nodeid FROM waypoint WHERE ordinal = 0), maxord(val, wayid) AS (SELECT max(ordinal), wayid FROM waypoint GROUP BY wayid) SELECT wp.wayid FROM waypoint wp, way w, ord o, maxord mo WHERE wp.wayid = w.id AND wp.ordinal = mo.val AND wp.nodeid = o.nodeid GROUP BY wp.wayid;"
	statement = "SELECT wayid, nodeid FROM waypoint WHERE ordinal = 0"
	ordinal_zero = c.execute(statement)
	ordinal_zero = ordinal_zero.fetchall()
	statement = "WITH find(ordinal, nodeid, wayid) AS (SELECT max(ordinal), nodeid, wayid FROM waypoint GROUP BY wayid) SELECT w.wayid, w.nodeid FROM find f, waypoint w WHERE f.ordinal = w.ordinal AND f.wayid = w.wayid;"
	ordinal_last = c.execute(statement)
	ordinal_last = c.fetchall()
	#print(len(ordinal_zero))
	#print(len(ordinal_last))

	for i in range(len(ordinal_zero)):
		if ordinal_zero[i] == ordinal_last[i]:
			#item = ordinal_zero[i][0]
			statement = "UPDATE way SET closed = 1 WHERE id = {}".format(ordinal_zero[i][0])
			c.execute(statement)
			#c.execute(statement, item)
	

	c.execute("PRAGMA foreign_keys = ON")
	conn.commit()
	conn.close()
	
main()

