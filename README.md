# NFL_Record_Scraper
NFL_Record_Scraper is a web scraping application made using Python's BeautifulSoup4 library. It traverses through Pro Football Reference's data and obtains information for every NFl game of the modern era (1966 - present). The information is the saved to a Postgresql database using the psycopg module.

# How to Use
(I highly recommend using a virtual environment)
1. Install the necessary modules with: 
```
pip install -r requirements.txt
```
2. Enter the information for your database in the "config.py.example" file. Make sure to rename the file to "config.py".
3. Run the script using: 
```
python nfl_record_scraper.py
```
