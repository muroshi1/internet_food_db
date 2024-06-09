# Internet Food Database

# Running locally

Assuming you have Python, MySQL, SQLAlchemy, Flask and flask_sqlalchemy properly installed

- Connect to your local MySQL server
- Run init.sql (projet/src/init_db/init.sql) to initialize the database
- Go to script.py (projet/src/init_db/script.py)
    - In the first line (with "engine = create_engine(...", replace username and password with yours
    - Run script.py
- Go to app.py (projet/src/frontend/app.py)
    - In the first line (with "engine = create_engine(...", replace username and password with yours
    - Run app.py
- Go to http://localhost:5000/internet_food_db/ on your preferred browser
