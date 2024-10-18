import os
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from bs4 import BeautifulSoup

# Step 1: Fetch the data from the URL
url = 'https://www.mlb.com/stats/san-francisco-giants/all-time-by-season'
response = requests.get(url)
html_content = response.text
# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'lxml')
# Find all tables on the webpage
tables = soup.find_all('table')
# Extract the first table (you may need to adjust the index based on the webpage structure)
df = pd.read_html(str(tables))[0]

# Step 2: Clean the data
# Rename the columns to more meaningful names
df.columns = ['PLAYER', 'YEAR', 'TEAM', 'G', 'AB', 'R', 'H', '2B', '3B', 'HR',
              'RBI', 'BB', 'SO', 'SB', 'CS', 'AVG', 'OBP', 'SLG', 'OPS']
# Convert 'YEAR' and 'R' (runs) to numeric, and drop rows with invalid values
df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
df['R'] = pd.to_numeric(df['R'], errors='coerce')
# Drop rows where 'YEAR' or 'R' is NaN
df = df.dropna(subset=['YEAR', 'R'])

# Step 3: Create SQLite database and insert data
# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('baseball_stats.db')
cur = conn.cursor()
# Create a table in the database
cur.execute('''
CREATE TABLE IF NOT EXISTS baseball_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player TEXT,
    year INTEGER,
    team TEXT,
    games INTEGER,
    at_bats INTEGER,
    runs INTEGER,
    hits INTEGER,
    doubles INTEGER,
    triples INTEGER,
    home_runs INTEGER,
    rbi INTEGER,
    walks INTEGER,
    strikeouts INTEGER,
    stolen_bases INTEGER,
    caught_stealing INTEGER,
    avg REAL,
    obp REAL,
    slg REAL,
    ops REAL
)
''')
# Commit the table creation
conn.commit()
# Insert the DataFrame values into the SQLite database
for index, row in df.iterrows():
    cur.execute('''
    INSERT INTO baseball_stats (player, year, team, games, at_bats, runs, hits, doubles, triples, home_runs,
                                rbi, walks, strikeouts, stolen_bases, caught_stealing, avg, obp, slg, ops)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
    (row['PLAYER'], row['YEAR'], row['TEAM'], row['G'], row['AB'], row['R'], row['H'], row['2B'],
     row['3B'], row['HR'], row['RBI'], row['BB'], row['SO'], row['SB'], row['CS'],
     row['AVG'], row['OBP'], row['SLG'], row['OPS']))
# Commit the changes to the database
conn.commit()

# Step 4: Verify the insert by querying the table
cur.execute('SELECT * FROM baseball_stats LIMIT 5')
rows = cur.fetchall()
for row in rows:
    print(row)

# Step 5: Visualize the number of runs over time by the Giants
# Query the data for visualization
cur.execute('SELECT year, runs FROM baseball_stats WHERE team="SF" ORDER BY year')
data = cur.fetchall()
# Close the connection to the database
conn.close()
# Convert the query result to a DataFrame for plotting
plot_df = pd.DataFrame(data, columns=['YEAR', 'R'])
# Plot the runs over time
plt.figure(figsize=(10, 6))
sns.lineplot(x='YEAR', y='R', data=plot_df, marker='o', label='Runs')
# Set the labels and title
plt.xlabel('Year')
plt.ylabel('Runs')
plt.title('San Francisco Giants Runs Over Time')
# Rotate x-axis labels if necessary
plt.xticks(rotation=45)
# Display the plot
plt.tight_layout()
plt.legend()
plt.grid(True)
plt.show()