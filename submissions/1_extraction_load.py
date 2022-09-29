
import os

# set location of working folder
work_dir = "C:/Users/tgber/vanguard_onramp_final/submissions"
os.chdir(work_dir)

# set spotify client id and client secret id
os.environ['SPOTIPY_CLIENT_ID'] = '77a493b7041e443b9563fxxxxxxxxxxx'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'd89c2763a12344b98e3e0cyyyyyyyyyyy'


import pandas as pd
import numpy as np
import time
import spotipy
import pprint
from spotipy.oauth2 import SpotifyClientCredentials

# authorise spotipy api
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


# ------------------------------------------ 
# Data extraction using API
# ------------------------------------------ 

# set name of 20 artists/musicians
artist_name_list = ["foo fighters", "hans zimmer", "imagine dragons", "linkin park", "green day", "ludovico einaudi", "rahman", 
                    "michael jackson", "britney spears", "elvis presley", "billy joel", "shakira", "mariah carey", 
                    "madonna", "eminem", "whitney houston", "taylor swift", "beyonce", "elton john", "lady gaga"]

## 1. Artists data

artist_id, artist_name, external_url, genre, image_url, followers, popularity, type_list, artist_uri = [], [], [], [], [], [], [], [], []

for i in range(len(artist_name_list)):
    
    # api call
    results = spotify.search(q='artist:' + artist_name_list[i], type='artist')
    items = results['artists']['items']
    
    if len(items) > 0:
       
        artist_id.append(items[0]['id'])
        artist_name.append(items[0]['name'])
        external_url.append(items[0]['external_urls']['spotify'])
        image_url.append(items[0]['images'][0]['url'])
        followers.append(items[0]['followers']['total'])
        popularity.append(items[0]['popularity'])
        type_list.append(items[0]['type'])
        artist_uri.append(items[0]['uri'])
        
        if len(items[0]['genres']) > 1:
            temp_str = ", ".join(items[0]['genres'])
        else:
            temp_str = "".join(items[0]['genres'])
        genre.append(temp_str)

# create dict with all lists 
artist_dict = {'artist_id' : artist_id, 'artist_name' : artist_name, 'external_url' : external_url, 'genre' : genre,
              'image_url' : image_url, 'followers' : followers, 'popularity' : popularity, 'type' : type_list, 'artist_uri' : artist_uri}

# create artist dataframe from dict
artist_df = pd.DataFrame(artist_dict)
artist_df.drop_duplicates(inplace = True)
print("Artist dataframe shape: ", artist_df.shape)
# artist_df.sample(7)


## 2. Albums data

album_id, album_name, external_url, image_url, release_date, total_tracks, type_list, album_uri, artist_id = [], [], [], [], [], [], [], [], []
    
for i in range(len(artist_uri)):
    
    # api call
    results = spotify.artist_albums(artist_id = artist_uri[i], album_type = 'album', country = 'US')

    for j in range(len(results['items'])): 
        album_id.append(results['items'][j]['id'])
        album_name.append(results['items'][j]['name'])
        external_url.append(results['items'][j]['external_urls']['spotify'])
        image_url.append(results['items'][j]['images'][0]['url'])
        release_date.append(results['items'][j]['release_date'])
        total_tracks.append(results['items'][j]['total_tracks'])
        type_list.append(results['items'][j]['type'])
        album_uri.append(results['items'][j]['uri'])
        artist_id.append(artist_uri[i])

# create dict with all lists
album_dict = {'album_id' : album_id, 'album_name' : album_name, 'external_url' : external_url, 'image_url' : image_url,
              'release_date' : release_date, 'total_tracks' : total_tracks, 'type' : type_list, 'album_uri' : album_uri, 'artist_id' : artist_id}

# create albums dataframe from dict
album_df = pd.DataFrame(album_dict)
album_df.drop_duplicates(inplace = True)
print("Albums dataframe shape: ", album_df.shape)
# album_df.sample(5)

## Data mining on albums data if there are more than 6 albums for an artist

# keep only one album which are unique in name
album_df["rank"] = album_df.groupby("album_name")["album_id"].rank(ascending=False)
album_df = album_df.loc[album_df['rank'] == 1]

# rank albums based on number of tracks and then keep only x per artist
album_df["rank"] = album_df.groupby("artist_id")["total_tracks"].rank(ascending = False)
album_limit_per_artist = 6
album_df = album_df.loc[album_df['rank'] <= album_limit_per_artist]
album_df.drop('rank', axis = 1, inplace = True)
print("Albums dataframe shape - after duplicate data removal: ", album_df.shape)


## 3. Tracks data

uq_album_id = album_df['album_id'].unique()

# system time to start timer
st_time = time.time()

track_id, song_name, external_url, duration_ms, explicit, disc_number, type_list, song_uri, album_id_mod = [], [], [], [], [], [], [], [], []
    
for i in range(len(uq_album_id)):
    
    # api call
    results = spotify.album_tracks(album_id = uq_album_id[i], limit = 50, offset = 0)

    for j in range(len(results['items'])): 
        track_id.append(results['items'][j]['id'])
        song_name.append(results['items'][j]['name'])
        external_url.append(results['items'][j]['external_urls']['spotify'])
        duration_ms.append(results['items'][j]['duration_ms'])
        explicit.append(results['items'][j]['explicit'])
        disc_number.append(results['items'][j]['disc_number'])
        type_list.append(results['items'][j]['type'])
        song_uri.append(results['items'][j]['uri'])
        album_id_mod.append(uq_album_id[i])

# create dict with all lists
track_dict = {'track_id' : track_id, 'song_name' : song_name, 'external_url' : external_url, 'duration_ms' : duration_ms,
              'explicit' : explicit, 'disc_number' : disc_number, 'type' : type_list, 'song_uri' : song_uri, 'album_id' : album_id_mod}

# calculate execution time of data extraction
duration = round(time.time() - st_time, 2)
print(f"Took {duration} seconds to extract all tracks details")

# create tracks dataframe from dict
track_df = pd.DataFrame(track_dict)
track_df.drop_duplicates(inplace = True)
print("Tracks dataframe shape: ", track_df.shape)
# track_df.sample(10)

## Data mining on Tracks data

# convert boolean to string as it is easier to store in SQL db
track_df['explicit'] = track_df['explicit'].astype(str)


## 4. Track features data

# system time to start timer
st_time = time.time()
# there can be some tracks with no info, we need a list to store those track ids
missing_track_info = []
track_id_mod, danceability, energy, instrumentalness, liveness, loudness, speechiness, tempo, type_list, valence, song_uri = [], [], [], [], [], [], [], [], [], [], []
    
for i in range(len(track_id)):
    
    # api call
    results = spotify.audio_features([track_id[i]])
    
    # if api returns non-zero results, then store the info in respective lists
    if results[0] is not None:
        track_id_mod.append(track_id[i])
        danceability.append(results[0]['danceability'])
        energy.append(results[0]['energy'])
        instrumentalness.append(results[0]['instrumentalness'])
        liveness.append(results[0]['liveness'])
        loudness.append(results[0]['loudness'])
        speechiness.append(results[0]['speechiness'])
        tempo.append(results[0]['tempo'])
        type_list.append(results[0]['type'])
        valence.append(results[0]['valence'])
        song_uri.append(results[0]['uri'])
    # else store the track ids with zero info
    else:
        missing_track_info.append(track_id[i])

# create dict with all lists
track_features_dict = {'track_id' : track_id_mod, 'danceability' : danceability, 'energy' : energy, 'instrumentalness' : instrumentalness,
                       'liveness' : liveness, 'loudness' : loudness, 'speechiness' : speechiness, 'tempo' : tempo, 'type' : type_list,
                       'valence' : valence, 'song_uri' : song_uri}

# calculate execution time of data extraction
duration = round(time.time() - st_time, 2)
print(f"Took {round(duration/60, 2)} minutes to extract all track features")

# create track_features dataframe from dict
track_features_df = pd.DataFrame(track_features_dict)
track_features_df.drop_duplicates(inplace = True)
print("Track Features dataframe shape: ", track_features_df.shape)
# track_features_df.sample(10)

## Data mining on Track features data

# there might be few tracks for which we don't have any track feature - delete these tracks from track_df as well
print(f"# tracks w/o feature info: {len(missing_track_info)}")
print(f"Shape of track_df before: {track_df.shape}")
track_df = track_df.loc[~track_df['track_id'].isin(missing_track_info)]
print(f"Shape of track_df after: {track_df.shape}")


# ------------------------------------------ 
# Data storage on SQL db
# ------------------------------------------ 

import sqlite3

# create database in working folder and initiate connection 
conn = sqlite3.connect("spotify.db")
cur = conn.cursor()

# code debug:
# The below lines prevent int/double datatypes to be stored as some blob/binary numbers in SQL db
# Source: https://stackoverflow.com/questions/49456158/integer-in-python-pandas-becomes-blob-binary-in-sqlite and https://sqlite.org/forum/info/392b48aafca01fd5

sqlite3.register_adapter(np.int32, int)
sqlite3.register_adapter(np.int64, int)


## 1. Create Artist table in SQL db

# drop table
cur.execute('''DROP TABLE IF EXISTS artist''')

# Creating empty table
table = """ CREATE TABLE artist (
            artist_id varchar(50) NOT NULL,
            artist_name varchar(255) NOT NULL,
            external_url varchar(100),
            genre varchar(100),
            image_url varchar(100),
            followers integer,
            popularity integer,
            type varchar(50),
            artist_uri varchar(100)
        ); """

cur.execute(table)

# insert query
sqlite_insert_query = """INSERT INTO artist
                          (artist_id, artist_name, external_url, genre, image_url, followers, popularity, type, artist_uri)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""

# insert records
recordList_artist = [tuple(x) for x in artist_df.to_records(index = False)]

# execute
cur.executemany(sqlite_insert_query, recordList_artist)
conn.commit()
print("Total", cur.rowcount, "Records inserted successfully into artist table")
conn.commit()

# data can be read into pandas dataframe from sql db
pd.read_sql("select * from artist limit 10", conn)


## 2. Create Album table in SQL db

# drop table
cur.execute('''DROP TABLE IF EXISTS album''')

# Creating empty table
table = """ CREATE TABLE album (
            album_id varchar(50), 
            album_name varchar(255), 
            external_url varchar(100), 
            image_url varchar(100), 
            release_date date, 
            total_tracks integer, 
            type varchar(50), 
            album_uri varchar(100), 
            artist_id varchar(50)
        ); """

cur.execute(table)

# insert query
sqlite_insert_query = """INSERT INTO album
                          (album_id, album_name, external_url, image_url, release_date, total_tracks, type, album_uri, artist_id)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""

# insert records
recordList_album = [tuple(x) for x in album_df.to_records(index = False)]

# execute
cur.executemany(sqlite_insert_query, recordList_album)
conn.commit()
print("Total", cur.rowcount, "Records inserted successfully into album table")
conn.commit()

# data can be read into pandas dataframe from sql db
pd.read_sql("select * from album limit 10", conn)


## 3. Create Track table in SQL db

# drop table
cur.execute('''DROP TABLE IF EXISTS track''')

# Creating empty table
table = """ CREATE TABLE track (
            track_id varchar(50), 
            song_name varchar(255), 
            external_url varchar(100), 
            duration_ms integer, 
            explicit boolean, 
            disc_number integer, 
            type varchar(50), 
            song_uri varchar(100), 
            album_id varchar(50)
        ); """

cur.execute(table)

# insert query
sqlite_insert_query = """INSERT INTO track
                          (track_id, song_name, external_url, duration_ms, explicit, disc_number, type, song_uri, album_id)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""

# insert records
recordList_track = [tuple(x) for x in track_df.to_records(index = False)]

# execute
cur.executemany(sqlite_insert_query, recordList_track)
conn.commit()
print("Total", cur.rowcount, "Records inserted successfully into track table")
conn.commit()

# data can be read into pandas dataframe from sql db
pd.read_sql("select * from track limit 10", conn)


## 4. Create Track feature table in SQL db

# drop table
cur.execute('''DROP TABLE IF EXISTS track_feature''')

# Creating empty table
table = """ CREATE TABLE track_feature (
            track_id varchar(50), 
            danceability double, 
            energy double, 
            instrumentalness double, 
            liveness double, 
            loudness double, 
            speechiness double, 
            tempo double, 
            type varchar(50), 
            valence double, 
            song_uri varchar(100)
        ); """

cur.execute(table)

# insert query
sqlite_insert_query = """INSERT INTO track_feature
                          (track_id, danceability, energy, instrumentalness, liveness, loudness, speechiness, tempo, type, valence, song_uri)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

# insert records
recordList_track_f = [tuple(x) for x in track_features_df.to_records(index = False)]

# execute
cur.executemany(sqlite_insert_query, recordList_track_f)
conn.commit()
print("Total", cur.rowcount, "Records inserted successfully into track_feature table")
conn.commit()

# data can be read into pandas dataframe from sql db
pd.read_sql("select * from track_feature", conn)


## 5. Create Views in SQL db

## 5.1. Top 10 songs by artist in terms of duration_ms (ordered by artist ASC, duration_ms DESC)

# view
view_query_1 = """CREATE VIEW top_10_songs AS

select c.artist_name, c.song_name, c.duration_ms
from
(
    select distinct b.artist_name, b.song_name, b.duration_ms, rank() over (partition by b.artist_name order by b.duration_ms desc) as ranking
    from
    (
        select distinct a.artist_id, a.artist_name, a.album_id, tr.track_id, tr.song_name, tr.duration_ms
        from
        (
            select distinct ar.artist_id, ar.artist_name, al.album_id
            from artist ar 
            left join album al
            on ar.artist_uri = al.artist_id
        ) a
        left join track tr
        on a.album_id = tr.album_id
    ) b
) c
where c.ranking <= 10
order by c.artist_name, c.duration_ms desc
"""

# execute
cur.execute("""DROP VIEW IF EXISTS top_10_songs""")
cur.execute(view_query_1)
pd.read_sql("""select * from top_10_songs""", conn)


## 5.2. Top 20 artists in the database ordered by # of followers DESC

# view
view_query_2 = """CREATE VIEW top_20_artists AS

select artist_name, followers
from artist
order by followers desc
limit 20;
"""

# execute
cur.execute("""DROP VIEW IF EXISTS top_20_artists""")
cur.execute(view_query_2)
pd.read_sql("""select * from top_20_artists""", conn)


## 5.3. Top 10 songs by artist in terms of tempo (ordered by artist ASC, duration_ms DESC)

# view
view_query_3 = """CREATE VIEW top_10_songs_tempo AS

select d.artist_name, d.song_name, d.tempo
from
(
    select distinct c.artist_name, c.song_name, c.tempo, rank() over (partition by c.artist_name order by c.tempo desc) as ranking
    from
    (
        select distinct b.artist_id, b.artist_name, b.album_id, b.track_id, b.song_name, tf.tempo
        from
        (
            select distinct a.artist_id, a.artist_name, a.album_id, tr.track_id, tr.song_name
            from
            (
                select distinct ar.artist_id, ar.artist_name, al.album_id
                from artist ar 
                left join album al
                on ar.artist_uri = al.artist_id
            ) a
            left join track tr
            on a.album_id = tr.album_id
        ) b
        left join track_feature tf
        on b.track_id = tf.track_id
    ) c
) d
where d.ranking <= 10
order by d.artist_name, d.tempo desc
"""

# execute
cur.execute("""DROP VIEW IF EXISTS top_10_songs_tempo""")
cur.execute(view_query_3)
pd.read_sql("""select * from top_10_songs_tempo""", conn)


## 5.4. Top 10 artists with decreasing average loudness
# The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typically range between -60 and 0 db.

# view
view_query_4 = """CREATE VIEW top_10_artist_loudness AS

select c.artist_id, c.artist_name, avg(c.loudness) as avg_loudness
from
(
    select distinct b.artist_id, b.artist_name, b.album_id, b.track_id, b.song_name, tf.loudness
    from
    (
        select distinct a.artist_id, a.artist_name, a.album_id, tr.track_id, tr.song_name
        from
        (
            select distinct ar.artist_id, ar.artist_name, al.album_id
            from artist ar 
            left join album al
            on ar.artist_uri = al.artist_id
        ) a
        left join track tr
        on a.album_id = tr.album_id
    ) b
    left join track_feature tf
    on b.track_id = tf.track_id
) c
group by c.artist_id, c.artist_name
order by avg_loudness
limit 10;
"""

# execute
cur.execute("""DROP VIEW IF EXISTS top_10_artist_loudness""")
cur.execute(view_query_4)
pd.read_sql("""select * from top_10_artist_loudness""", conn)


## 5.5. Top 10 albums with decreasing average valence - More valence suggests more happiness index
# A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).

# view
view_query_5 = """CREATE VIEW top_10_album_valence AS

select c.album_id, c.album_name, c.artist_name, avg(c.valence) as avg_valence
from
(
    select distinct b.artist_id, b.artist_name, b.album_id, b.album_name, b.track_id, b.song_name, tf.valence
    from
    (
        select distinct a.artist_id, a.artist_name, a.album_id, a.album_name, tr.track_id, tr.song_name
        from
        (
            select distinct ar.artist_id, ar.artist_name, al.album_id, al.album_name
            from artist ar 
            left join album al
            on ar.artist_uri = al.artist_id
        ) a
        left join track tr
        on a.album_id = tr.album_id
    ) b
    left join track_feature tf
    on b.track_id = tf.track_id
) c
group by c.album_id, c.album_name, c.artist_name
order by avg_valence desc
limit 10;
"""

# execute
cur.execute("""DROP VIEW IF EXISTS top_10_album_valence""")
cur.execute(view_query_5)
pd.read_sql("""select * from top_10_album_valence""", conn)


## 5.6. Top 10 instrumental albums - if instrumental index is >= 0.5, consider to be instrumental track. Count # instrumental tracks per album
# Instrumentalness predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.

# view
view_query_6 = """CREATE VIEW top_10_album_instrumental AS

select c.album_id, c.album_name, c.artist_name, sum(c.is_instrumental) as num_instrumental
from
(
    select distinct b.artist_id, b.artist_name, b.album_id, b.album_name, b.track_id, b.song_name, tf.instrumentalness,
    case when tf.instrumentalness >= 0.5 then 1 else 0 end as is_instrumental
    from
    (
        select distinct a.artist_id, a.artist_name, a.album_id, a.album_name, tr.track_id, tr.song_name
        from
        (
            select distinct ar.artist_id, ar.artist_name, al.album_id, al.album_name
            from artist ar 
            left join album al
            on ar.artist_uri = al.artist_id
        ) a
        left join track tr
        on a.album_id = tr.album_id
    ) b
    left join track_feature tf
    on b.track_id = tf.track_id
) c
group by c.album_id, c.album_name, c.artist_name
order by num_instrumental desc
limit 10;
"""

# execute
cur.execute("""DROP VIEW IF EXISTS top_10_album_instrumental""")
cur.execute(view_query_6)
pd.read_sql("""select * from top_10_album_instrumental""", conn)

# Close SQL connection
conn.close()

# End of Code
