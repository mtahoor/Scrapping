import sqlite3

# Function to perform calculations and write results to a text file
def calculate_and_write_to_file():
    # Connect to the SQLite database
    conn = sqlite3.connect('Data_base.sqlite3')
    c = conn.cursor()

    # Perform SQL queries to select relevant data from tables
    hieghest_score_query = "SELECT id, title, score FROM stories ORDER BY score DESC LIMIT 3"
    get_comments_for_most_hieghest_score_query = """
        SELECT s.id AS story_id, s.title AS story_title, s.score AS story_score,
               c.id AS comment_id, c.text AS comment_text, c.author AS comment_author
        FROM stories AS s 
        JOIN comments AS c ON s.id = c.parent_id 
        WHERE s.score = (SELECT MAX(score) FROM stories) 
        ORDER BY c.id -- Order by comment id to group comments with the same story together
    """
    story_count_of_authors = """
        SELECT author, COUNT(*) AS story_count 
        FROM stories 
        GROUP BY author 
        ORDER BY story_count DESC
    """

    # Execute SQL queries
    c.execute(hieghest_score_query)
    highest_scores = c.fetchall()

    c.execute(get_comments_for_most_hieghest_score_query)
    stories_with_comments = c.fetchall()

    c.execute(story_count_of_authors)
    authors_story_count = c.fetchall()

    # Write calculated results to a text file
    with open('calculated_results.txt', 'w') as f:
        f.write("Top 3 stories with the highest scores:\n")
        for row in highest_scores:
            f.write("Story ID: {}, Title: {}, Score: {}\n".format(row[0], row[1], row[2]))
        f.write("\n")

        f.write("Stories with comments on the story with the highest score:\n")
        previous_story_id = None
        for row in stories_with_comments:
            if row[0] != previous_story_id:
                f.write("Story ID: {}, Title: {}, Score: {}\n".format(row[0], row[1], row[2]))
                previous_story_id = row[0]
            f.write("Comment ID: {}, Comment Text: {}, Comment Author: {}\n".format(row[3], row[4], row[5]))
        f.write("\n")

        f.write("Authors and their story counts:\n")
        for row in authors_story_count:
            f.write("Author: {}, Story Count: {}\n".format(row[0], row[1]))

    # Close the database connection
    conn.close()

# Main function
if __name__ == "__main__":
    # Call the function to perform calculations and write results to a file
    calculate_and_write_to_file()
