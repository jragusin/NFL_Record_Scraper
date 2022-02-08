import datetime
import psycopg
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from config import DATABASE


# Info for web scraper
base_url = "https://www.pro-football-reference.com/years/"

gamelink_base_url = 'https://www.pro-football-reference.com/'

years_list = list(range(1966, 2025))
weeks_list = list(range(1,25))

containers = []
dates = []
road_teams = []
home_teams = []
home_scores = []
road_scores = []
links = []

# Info for db
conn = psycopg.connect(
    host=DATABASE['hostname'],
    dbname=DATABASE['dbname'],
    user=DATABASE['user'],
    password=DATABASE['password']
)

curr = conn.cursor()

def web_scraper():
    for year in years_list:
        for week in weeks_list:
            new_url = base_url+str(year)+"/"+"week_"+str(week)+".htm"
            try:
                uClient = uReq(new_url)
                page_html = uClient.read()
                uClient.close()
                page_soup = soup(page_html, "html.parser")
                containers.append(page_soup.findAll("div", {"class":"game_summary expanded nohover"}))
            except Exception as e:
                pass
    for i in range(0, len(containers)):
        for j in range(0, len(containers[i])):
            tables = containers[i][j].findAll('table', {'class': 'teams'})
            for table in tables:
                body = table.find('tbody')
                rows = body.findAll('tr')
                link = table.find('td', {'class': 'gamelink'})
                links.append(gamelink_base_url + link.a['href'])
                for k in range(len(rows)):
                    data = rows[k].findAll('td', {'class': 'right'})
                    if k % 3 == 0:
                        dates.append(get_proper_date(rows[k].td.text))
                    elif k % 2 == 0 and k % 3 != 0:
                        print("TEST")
                        current_team = get_current_team(rows[k].td.text)
                        home_teams.append(current_team)
                        add_team_to_db(current_team)
                        home_scores.append(int(data[0].text))
                    else:
                        road_teams.append(get_current_team(rows[k].td.text))
                        road_scores.append(int(data[0].text))

def get_current_team(team):
    if team == 'Los Angeles Raiders' or team == 'Oakland Raiders':
        return 'Las Vegas Raiders'
    elif team == 'Baltimore Colts':
        return 'Indianapolis Colts'
    elif team == 'St. Louis Cardinals' or team == 'Phoenix Cardinals':
        return 'Arizona Cardinals'
    elif team == 'St. Louis Rams':
        return 'Los Angeles Rams'
    elif team == 'Houston Oilers' or team == 'Tennessee Oilers':
        return 'Tennessee Titans'
    elif team == 'San Diego Chargers':
        return 'Los Angeles Chargers'
    elif team == 'Washington Redskins':
        return 'Washington Football Team'
    elif team == 'Boston Patriots':
        return 'New England Patriots'
    else:
        return team

def add_team_to_db(team):
    # Check for duplicate teams
    curr.execute("""
    SELECT * from games_teams WHERE team_name = %s
    """,
    (team,))
    result = curr.fetchone()
    if not result:
        curr.execute("""
        INSERT INTO games_teams (team_name) VALUES (%s)
        """, 
        (team,))
        conn.commit()
        print("Team Added: " + str(team))

def get_proper_date(date_text):
    date_string = date_text.replace(',', '')
    return datetime.datetime.strptime(date_string, '%b %d %Y')
    

def store_info():
    for i in range(len(dates)):
        if not is_duplicate_query(curr, road_teams[i], road_scores[i], home_teams[i], home_scores[i], dates[i]):
            curr.execute("""
            INSERT INTO games_games (road_team, road_score, home_team, home_score, date, link) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (road_teams[i], road_scores[i], home_teams[i], home_scores[i], dates[i], links[i],))
            conn.commit() 
    conn.close()

def is_duplicate_query(cursor, road_team, road_score, home_team, home_score, date):
    cursor.execute("""
    SELECT * FROM games_games WHERE road_team = %s AND road_score = %s AND home_team = %s AND home_score = %s AND date = %s
    """,
    (road_team, road_score, home_team, home_score, date,))
    result = cursor.fetchmany()
    return len(result) > 0
    

if __name__ == '__main__':
    print('Scraping...')
    web_scraper()
    print('Storing data...')
    store_info()
    print('Done!')
