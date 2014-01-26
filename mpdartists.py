#!/usr/bin/python

import sys
from getopt import getopt
from urllib2 import urlopen, quote
from xml.dom.minidom import parseString
from mpd import MPDClient
from sqlite3 import connect

optlist, args = getopt(sys.argv[1:], 'h:p:d:')
host = 'localhost'
port = 6600
dbname = 'artists.db'
lastfmKey = '373a4f9504d83af8c44c7414c3769f3f'

for opt, arg in optlist:
	if opt == '-h':
		host = arg
	elif opt == '-p':
		port = arg
	elif opt == '-d':
		dbname = arg
	else:
		print("Usage: python %s [-h <mpdhost>] [-p <mpdport>]" % sys.argv[0])
		sys.exit(1)

# Retrieve artists from MPD
client = MPDClient()
client.connect(host, port)
artists = sorted(client.list("artist"))
client.close()
client.disconnect()

# Create SQLite connection
db = connect(dbname)
db.execute("DROP TABLE IF EXISTS artists")
db.execute("DROP TABLE IF EXISTS similarities")
db.commit()

db.execute("CREATE TABLE artists(artist varchar(1024) primary key asc)")
db.commit()

db.execute("CREATE TABLE similarities(" +
	"artist varchar(1024), " +
	"similarity varchar(1024), " +
	"match real, " +
	"primary key(artist, similarity), " +
	"foreign key(artist) references artists(artist), " +
	"foreign key(similarity) references artists(artist))")
db.commit()

print("Analyzing artists...")
for artist in artists:
	db.execute("INSERT INTO artists(artist) VALUES(?)", (artist.decode('utf-8'),))
db.commit()

for artist in artists:
	print("Processing [%s]... " % artist)
	try:
		www = urlopen("http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist=%s&api_key=%s" %
			(quote(artist), lastfmKey))

		document = parseString(www.read())
		for simartist in document.getElementsByTagName("artist"):
			name = simartist.getElementsByTagName("name")
			if len(name) > 0:
				name = name[0].firstChild.nodeValue
				match = simartist.getElementsByTagName("match")
				if len(match) > 0:
					match = float(match[0].firstChild.nodeValue)
					if name.encode('utf-8') in artists:
						db.execute("INSERT INTO similarities(artist, similarity, match) VALUES(?, ?, ?)", [\
							(artist.decode('utf-8')), \
							(name), \
							(match)])

		db.commit()

	except Exception as e:
		print("Error: [%s]" % (e))

db.close()

