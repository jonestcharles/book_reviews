'''
import.py opens a csv file containing a list of books that are then raed into
the database for Hawt Reads. import.py assume the format isbn, title, author,
publicaiton year for each row in the file. It also assumes that line 1 contains
column headers. These are not used, as the database tables was built before
running this app. See the project README.md for details.
'''
import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    with open("books.csv") as f:
        reader = csv.reader(f)
        next(reader) # skip line 1 (column headers)
    
        for isbn, title, author, year in reader:
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES \
                (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title,
                 "author": author, "year": year})
    
        db.commit()

if __name__ == "__main__":
    main()
