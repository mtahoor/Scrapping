import sqlite3
import requests
from bs4 import BeautifulSoup

# Function to fetch HTML data from the website
def fetch_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to fetch HTML data from the website")
        return None

def fetch_kids(story_id):
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json?print=pretty"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch comment with ID {story_id}")
        return None
    
def fetch_comments(kids, parent_id, conn):
    for kid in kids:
        url = f"https://hacker-news.firebaseio.com/v0/item/{kid}.json?print=pretty"
        response = requests.get(url)
        if response.status_code == 200:
            res = response.json()
            insert_comment(res, parent_id, conn)
        else:
            print(f"Failed to fetch comment with ID {kid}")

# Function to create SQLite3 database and table
def create_database():
    conn = sqlite3.connect('Data_base.sqlite3')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    url TEXT,
                    score INTEGER,
                    author TEXT,
                    comment_count INTEGER
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY,
                    parent_id INTEGER,
                    text TEXT,
                    author TEXT,
                    FOREIGN KEY (parent_id) REFERENCES stories (id)
                )''')
    conn.commit()
    return conn

# Function to insert story into the database
def insert_story(story, conn):
    c = conn.cursor()
    try:
        c.execute("INSERT INTO stories (id, title, url, score, author, comment_count) VALUES (?, ?, ?, ?, ?, ?)",
                (story['id'], story['title'], story['url'], story['score'], story['author'], story['comment_count']))
        conn.commit()
    except:
        print('Story already exsisit')

# Function to insert comment into the database
def insert_comment(comment, parent_id, conn):
    c = conn.cursor()
    try:
        c.execute("INSERT INTO comments (id, parent_id, text, author) VALUES (?, ?, ?, ?)",
                (comment['id'], parent_id, comment['text'], comment['by']))
        conn.commit()
    except:
        print('Deleted Comment')

# Function to parse HTML data and extract relevant information
def parse_html(html, conn):
    soup = BeautifulSoup(html, 'html.parser')
    spans = soup.select('span.titleline')
    scores = soup.select('span.score')
    by = soup.select('a.hnuser')
    comments = soup.select('span.subline')

    for i in range(len(spans)):
        anchor = spans[i].find('a')
        if anchor:
            title = anchor.get_text(strip=True)
            url = anchor.get('href')
        score = scores[i].get_text(strip=True).split()[0]
        author = by[i].get_text(strip=True)
        anchors = comments[i].find_all('a')
        story_id = anchors[-1].get('href').split('=')[1]
        comment_count = anchors[-1].text.strip()
        comment_count = comment_count.split()[0]
        if comment_count == "discuss":
            comment_count = 0
        else:
            comment_count = int(comment_count)
        story = {'id': story_id, 'title': title, 'url': url, 'score': score, 'author': author, 'comment_count': comment_count}
        insert_story(story, conn)
        if comment_count > 0:
            kids = fetch_kids(story_id)
            if kids and 'kids' in kids:
                fetch_comments(kids['kids'], int(story_id), conn)

# Main function
if __name__ == "__main__":
    # Get page number from user input
    while True:
        try:
            page = int(input("Enter the page number to fetch data (2-5): "))
            if page < 2 or page > 5:
                print("Page number must be between 2 and 5. Please try again.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a valid page number.")

    # URL of the website to scrape
    url = f"https://news.ycombinator.com/news?p={page}"
    # Fetch HTML data
    html = fetch_html(url)
    if html:
        # Create SQLite3 database and table
        conn = create_database()
        # Parse HTML data and insert into the database
        parse_html(html, conn)
        # Close database connection
        conn.close()
        print("Data stored successfully in SQLite database!")
    else:
        print("Failed to fetch HTML data. Exiting...")
