
import os

# set location of working folder
work_dir = "C:/Users/tgber/vanguard_onramp_final/submissions"
os.chdir(work_dir)

import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Import all tables and views from SQLdb - to pandas dataframe

# The below lines prevent int/double datatypes to be stored as some blob/binary numbers in SQL db
# Source: https://stackoverflow.com/questions/49456158/integer-in-python-pandas-becomes-blob-binary-in-sqlite and https://sqlite.org/forum/info/392b48aafca01fd5

sqlite3.register_adapter(np.int32, int)
sqlite3.register_adapter(np.int64, int)

# Connect to SQL db saved earlier
conn = sqlite3.connect("spotify.db")
cur = conn.cursor()

# 1. Read Artist table as pandas dataframe
artist_df = pd.read_sql("select * from artist", conn)
# print(artist_df.info())

# 2. Read Album table as pandas dataframe
album_df = pd.read_sql("select * from album", conn)
# print(album_df.info())

# 3. Read Track table as pandas dataframe
track_df = pd.read_sql("select * from track", conn)
# print(track_df.info())

# 4. Read Track feature table as pandas dataframe
track_feature_df = pd.read_sql("select * from track_feature", conn)
# print(track_feature_df.info())

# close connection with SQL database
conn.close()

# ------------------------------------------ 
# Create Analytical Data Model (ADM)
# ------------------------------------------ 

# ADM is a single dataset with all info (from 4 tables). This is used to perform data mining

# left join artist with album on artist_id
df1 = artist_df.merge(album_df[['album_id', 'album_name', 'release_date', 'total_tracks', 'album_uri', 'artist_id']],
                      left_on = 'artist_uri', right_on = 'artist_id', how = 'left')
df1 = df1.rename(columns = {'artist_id_x' : 'artist_id'}).drop('artist_id_y', axis = 1)

# left join with track on album_id
df2 = df1.merge(track_df,
                on = 'album_id', how = 'left')
df2 = df2.rename(columns = {'external_url_x' : 'external_url'}).drop(['external_url_y', 'type_x', 'type_y'], axis = 1)

# left join with track_feature on track_id
adm = df2.merge(track_feature_df,
                on = 'track_id', how = 'left')
adm = adm.rename(columns = {'song_uri_x' : 'song_uri'}).drop(['song_uri_y', 'type'], axis = 1)

# ------------------------------------------ 
# Visualization
# ------------------------------------------ 

## 1. Artists with most number of followers

artist_df.sort_values('followers', ascending = False, inplace = True)

plt.figure(figsize = (15,10))
plt.bar(artist_df['artist_name'], artist_df['followers'], color = (0.2, 0.4, 0.6, 0.6))
plt.title('Artists with most followers', fontsize = 14)
plt.xlabel('Artists', fontsize = 14)
plt.ylabel('# Followers', fontsize = 14)
plt.rc('axes', labelsize = 5)
plt.xticks(rotation = 45, ha = 'right')
plt.grid(False)
# export_pdf.savefig()
# plt.close()
# plt.show()

## 2. Artists with average valence

# use adm to find the average valence per artist - valence is the happiness index - more the number, happier the song
valence_df = adm.groupby('artist_name').agg({'valence' : np.mean}).rename(columns = {'valence' : 'avg_valence'}).reset_index()
valence_df['avg_valence'] = round(valence_df['avg_valence'], 3)
valence_df.sort_values('avg_valence', ascending = False, inplace = True)

plt.figure(figsize = (15,10))
plt.bar(valence_df['artist_name'], valence_df['avg_valence'], color = (0.3, 0.5, 0.4, 0.6))
plt.title('Artists with most happy songs', fontsize = 14)
plt.xlabel('Artists', fontsize = 14)
plt.ylabel('Average Valence Index', fontsize = 14)
plt.rc('axes', labelsize = 5)
plt.xticks(rotation = 45, ha = 'right')
plt.grid(False)
# export_pdf.savefig()
# plt.close()
# plt.show()


## 3. Albums released per month 

# convert release date to date type and extract month/year
album_df['release_date'] = pd.to_datetime(album_df['release_date'])
album_df['release_month'] = album_df['release_date'].dt.month
album_df['release_year'] = album_df['release_date'].dt.year

# calculate unique num of albums released per month
album_df_rollup = album_df.groupby('release_month').agg({'album_name' : 'nunique'}).rename(columns = {'album_name' : 'album_count'}).reset_index()

plt.figure(figsize = (15,10))
plt.bar(album_df_rollup['release_month'], album_df_rollup['album_count'], color = (0.8, 0.5, 0.8, 0.5))
plt.title('# Albums released per month', fontsize = 14)
plt.xlabel('Month', fontsize = 14)
plt.ylabel('# albums released', fontsize = 14)
plt.rc('axes', labelsize = 5)
plt.grid(False)
# export_pdf.savefig()
# plt.close()
# plt.show()


# ------------------------------------------ 
# Export Visualization to PDF
# ------------------------------------------ 

with PdfPages(work_dir + '/visualization.pdf') as export_pdf:

    # 1
    plt.figure(figsize = (15,10))
    plt.bar(artist_df['artist_name'], artist_df['followers'], color = (0.2, 0.4, 0.6, 0.6))
    plt.title('Artists with most followers', fontsize = 14)
    plt.xlabel('Artists', fontsize = 14)
    plt.ylabel('# Followers', fontsize = 14)
    plt.rc('axes', labelsize = 5)
    plt.xticks(rotation = 45, ha = 'right')
    plt.grid(False)
    export_pdf.savefig()
    plt.close()

    # 2
    plt.figure(figsize = (15,10))
    plt.bar(valence_df['artist_name'], valence_df['avg_valence'], color = (0.3, 0.5, 0.4, 0.6))
    plt.title('Artists with most happy songs', fontsize = 14)
    plt.xlabel('Artists', fontsize = 14)
    plt.ylabel('Average Valence Index', fontsize = 14)
    plt.rc('axes', labelsize = 5)
    plt.xticks(rotation = 45, ha = 'right')
    plt.grid(False)
    export_pdf.savefig()
    plt.close()

    # 3
    plt.figure(figsize = (15,10))
    plt.bar(album_df_rollup['release_month'], album_df_rollup['album_count'], color = (0.8, 0.5, 0.8, 0.5))
    plt.title('# Albums released per month', fontsize = 14)
    plt.xlabel('Month', fontsize = 14)
    plt.ylabel('# albums released', fontsize = 14)
    plt.rc('axes', labelsize = 5)
    plt.grid(False)
    export_pdf.savefig()
    plt.close()


# End of Code
