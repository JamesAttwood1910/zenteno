import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main_2 import db, users  # Import your SQLAlchemy models

user_set = ""
password_set = ""

# Create engine and session
engine = create_engine('')
Session = sessionmaker(bind=engine)
session = Session()

# Query the record you want to update
user_to_update = session.query(users).filter_by(username=user_set).first()

# Modify the attributes of the queried object
user_to_update.password = password_set

# Commit the changes to the database session
session.commit()

# Close the session
session.close()
