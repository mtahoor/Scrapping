import sqlite3
import matplotlib.pyplot as plt

# Function to fetch data from the SQLite database
def fetch_data(query):
    conn = sqlite3.connect('Data_base.sqlite3')
    c = conn.cursor()
    c.execute(query)
    data = c.fetchall()
    conn.close()
    return data

# Function to create and save a bar plot
def create_bar_plot(x_labels, y_values, title, x_label, y_label, filename):
    plt.figure(figsize=(10, 10))
    plt.bar(x_labels, y_values)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

# Function to create and save a pie chart
def create_pie_chart(labels, sizes, title, filename):
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(title)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

if __name__ == "__main__":
    # Fetch data for visualizations
    highest_scores_data = fetch_data("SELECT title, score FROM stories ORDER BY score DESC LIMIT 3")
    authors_story_count_data = fetch_data("SELECT author, COUNT(*) AS story_count FROM stories GROUP BY author ORDER BY story_count DESC LIMIT 5")
    top_commented_stories_data = fetch_data("SELECT s.title, COUNT(c.id) AS comment_count FROM stories AS s JOIN comments AS c ON s.id = c.parent_id GROUP BY s.id ORDER BY comment_count DESC LIMIT 3")

    # Extract data for bar plot (top 3 stories with highest scores)
    top_stories_titles = [row[0] for row in highest_scores_data]
    top_stories_scores = [row[1] for row in highest_scores_data]

    # Create and save bar plot for top 3 stories with highest scores
    create_bar_plot(top_stories_titles, top_stories_scores, 
                    "Top 3 Stories with Highest Scores", "Story Title", "Score", "top_stories_bar_plot.png")

    # Extract data for pie chart (authors and their story counts)
    author_names = [row[0] for row in authors_story_count_data]
    story_counts = [row[1] for row in authors_story_count_data]

    # Create and save pie chart for authors and their story counts
    create_pie_chart(author_names, story_counts, 
                     "Top 5 Authors and Their Story Counts", "authors_story_counts_pie_chart.png")

    # Extract data for bar plot (top 3 most commented stories)
    top_commented_stories_titles = [row[0] for row in top_commented_stories_data]
    comment_counts = [row[1] for row in top_commented_stories_data]

    # Create and save bar plot for top 3 most commented stories
    create_bar_plot(top_commented_stories_titles, comment_counts, 
                    "Top 3 Most Commented Stories", "Story Title", "Comment Count", "top_commented_stories_bar_plot.png")
