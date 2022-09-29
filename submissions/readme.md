## Submission Readme

### Folder structure

The folder is structured in the following way:

Submissions (directory)
-- 1_extraction_load.py (python file)
-- 2_visualization.py (python file)
-- spotify.db (database file)
-- visualization.pdf (results pdf file)


### Objective of each file:

#### 1. 1_extraction_load.py

This code is used for the following tasks:
1. Connect to spotify API
2. 4 different API calls to extract spotify data on artists, albums, tracks and track features
3. Based on artist name, artist_id is obtained from API. Using these artist_id, we extract album_id. Each album_id has track_id which in turn has audio features connected to them
4. Each API call generates json result. These results are then parsed and converted into correponding pandas dataframes
5. SQL database is created using sqlite3 package
6. Each of the above 4 dataframes are stored as SQL tables in the SQL database - spotify.db
7. There are 6 SQL views that are created based on data manipulations using SQL queries and stored in the SQL database - spotify.db

#### 2. 2_visualization.py

This code is used for the following tasks:
1. Connect to the SQL database created in first code - spotify.db
2. Read the SQL tables into pandas dataframe as required
3. Create an Analytical Data Model (ADM) using all 4 tables - Join artist table with album table, then join track and track_feature table
4. This ADM stores all required datasets in one table and hence gives a better/detailed view of the relations between each table
5. Create different visualizations - top artists w.r.t followers, top artists with happy songs, distribution of # albums released per month
6. Export all these visualizations as a combined PDF file - visualization.pdf

#### 3. spotify.db

This is a SQL database created in first code - 1_extraction_load.py.
This database stores 4 SQL tables and 6 SQL views.

#### 4. visualization.pdf

This is a PDF file with charts created with the data in second code - 2_visualization.py.
This file contains 3 pages, with each page having one chart.


### Execution of each file:

The files should be executed in the following chronology:

1. Open 1_extraction_load.py code
2. change the working directory location (line # 5)
3. change the Spotipy client ID and client secret (obtained from spotify api dashboard page) (line # 9 and 10)
4. Save the code
5. Run the code
6. Output - spotify.db file in the submissions folder

7. Open 2_visualization.py
8. change the working directory location as the same location pasted in code 1_extraction_load.py (line # 5)
9. Save the code
10. Run the code
11. Output - visualization.pdf file in the submissions folder



                  ### Project Done By Berhanu Bekele ###

