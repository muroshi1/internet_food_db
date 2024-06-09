from flask import Flask, render_template, url_for, request, redirect, url_for, session, Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from flask_mysqldb import MySQL

from sqlalchemy.engine import create_engine
from sqlalchemy.sql import text


app = Flask(__name__)

# Source : https://codeshack.io/login-system-python-flask-mysql/
# https://youtu.be/yBDHkveJUf4?si=9yyUxmhs3Sx2RYt2
# https://youtu.be/Z1RJmh_OqeA?si=O1ADurE4b9jEGglO
# https://www.w3schools.com/css/
# https://www.w3schools.com/html/default.asp 
# Adapted to fit the project (SQLAlchemy, etc.)

# Replace 'username' and 'password' below
engine = create_engine('mysql+mysqldb://root:machina@127.0.0.1/internet_food_db')

conn = engine.connect()


statement_addresses = text("""INSERT INTO Addresses(Street, StreetNumber, ZipCode, City, Country) VALUES(:street, :streetnumber, :zipcode, :city, :country);""")
statement_clients = text("""INSERT INTO Clients (Name, Surname, AddressID, username, password) VALUES(:name, :surname, LAST_INSERT_ID(), :username, :password);""")
statement_owners= text("""INSERT INTO Owners (Name, Surname, AddressID, username, password) VALUES(:name, :surname, LAST_INSERT_ID(), :username, :password);""")
statement_moderators = text("""INSERT INTO Moderators (Name, Surname, AddressID, username, password) VALUES(:name, :surname, LAST_INSERT_ID(), :username, :password);""")

session = {} # Current session's data

# http://localhost:5000/internet_food_db/


@app.route('/internet_food_db/', methods=['GET', 'POST'])
def login():

    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        # Check if account exists using MySQL
        # conn.execute('SELECT * FROM clients WHERE username = %s AND password = %s', (username, password,))
        # statement_login = text("""SELECT * FROM Clients WHERE username = :username AND password = :password""")
        
        # statement_login = text("""SELECT * FROM (SELECT * FROM Clients UNION SELECT * FROM Owners) as u WHERE u.username = :username AND u.password = :password""")
        
        statement_login = text("""SELECT * FROM (SELECT 'CL', ClientID, Name, Surname, AddressID, username, password FROM Clients UNION SELECT 'OW', OwnerID, Name, Surname, AddressID, username, password FROM Owners UNION SELECT 'MO', ModID, Name, Surname, AddressID, username, password FROM Moderators) as u WHERE u.username = :username AND u.password = :password""")

        result = conn.execute(statement=statement_login, parameters={"username" : username, "password" : password})
        
        conn.commit()


        account = result.fetchone() # either CL, OW or MO
        # CL, ID, Name, Surname, AddressID, username, password
                
        if account:
            # Session data
            session["loggedin"] = True
            session["user_type"] = account[0]
            session["id"] = account[1] 
            session["username"] = account[5]

            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'

    return render_template('index.html', msg=msg)


@app.route('/internet_food_db/logout')
def logout():
    session["loggedin"] = None
    session["id"] = None
    session["username"] = None

    return redirect(url_for('login'))


@app.route('/internet_food_db/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if (request.method == 'POST') and ('user_type' in request.form) and ('name' in request.form) and ('surname' in request.form) and ('username' in request.form) and ('password' in request.form):
        user_type = request.form['user_type']
        
        name = request.form['name']
        surname = request.form['surname']

        street = request.form['street']
        streetnumber = request.form['streetnumber']
        zipcode = request.form['zipcode']
        city = request.form['city']
        country = request.form['country']

        username = request.form['username']
        password = request.form['password']


        conn.execute(statement=statement_addresses, parameters={"street": street, "streetnumber" : streetnumber, "zipcode" : zipcode, "city" : city, "country" : country})

        if user_type == "client":
            conn.execute(statement=statement_clients, parameters={"name": name, "surname": surname, "username" : username, "password" : password})
        elif user_type == "owner":
            conn.execute(statement=statement_owners, parameters={"name": name, "surname": surname, "username" : username, "password" : password})

        elif user_type == "moderator":
            conn.execute(statement=statement_moderators, parameters={"name": name, "surname": surname, "username" : username, "password" : password})

        conn.commit()

        msg = 'You have successfully registered!'
    elif request.method == 'POST':

        msg = 'Please fill out the form!'

    return render_template('register.html', msg=msg)


def load_restaurants_from_db():
    result = conn.execute(text("SELECT * FROM Restaurants ORDER BY Stars DESC LIMIT 5;")) # show top rated restaurants by default, add filters later
    results_as_dict = result.mappings().all()

    return results_as_dict


@app.route('/internet_food_db/home')
def home():
    if session["loggedin"] == True:
        
        restaurants = load_restaurants_from_db()

        return render_template('home.html', username=session["username"], user_type=session["user_type"], restaurants=restaurants)


    # Not logged in
    return redirect(url_for('login'))


def load_restaurant_info(restaurant_id):
    result = conn.execute(text("SELECT * FROM Restaurants WHERE RestaurantID = :restaurant_id"), {"restaurant_id" : restaurant_id})

    if not result:
        return None
    
    d = result.mappings().all()

    return d

def load_menu_info(restaurant_id):
    menuID = conn.execute(text("SELECT * FROM Menus WHERE RestaurantID = :restaurant_id"), {"restaurant_id" : restaurant_id})

    m = menuID.mappings().all()

    if len(m) < 1:
        return []

    x = m[0].MenuID
    result = conn.execute(text("SELECT * FROM Meals WHERE MenuID = :menuID"), {"menuID" : x})

    if not result:
        return None
    
    d = result.mappings().all()

    return d

def load_restaurant_adress(adress_id):
    result = conn.execute(text("SELECT * FROM Addresses WHERE AddressID = :adress_id"), {"adress_id" : adress_id})
    if not result:
        return None
    
    d = result.mappings().all()

    return d

def load_restaurant_reviews(restaurant_id):
    result = conn.execute(text("SELECT * FROM Reviews WHERE RestaurantID = :restaurant_id AND IsBad = False ORDER BY Date DESC"), {"restaurant_id" : restaurant_id})

    if not result:
        return None
    
    d = result.mappings().all()

    return d

def load_visit_info(visitInfoIDs):
    visitInfos = {}
    for visitInfoID in visitInfoIDs:
        result = conn.execute(text("SELECT * FROM Visitinfos WHERE VisitInfoID = :visitInfo_id"), {"visitInfo_id" : visitInfoID}).mappings().all()
        visitInfos[visitInfoID] = result[0]
    
    return visitInfos

def load_client_info(clientIDs):
    clients = {}

    for clientID in clientIDs:
        result = conn.execute(text("SELECT * FROM Clients WHERE ClientID = :client_id"), {"client_id" : clientID}).mappings().all()
        clients[clientID] = result[0]
    
    
    return clients

def load_allergen_info(mealIDs):
    allergens = {}
    for mealID in mealIDs:
        result = conn.execute(text("SELECT * FROM Allergens WHERE MealID = :meal_id"), {"meal_id": mealID}).mappings().all()
        allergens[mealID] = result
    return allergens


@app.route('/internet_food_db/home/<restaurant_id>')
def restaurant_page(restaurant_id):

    restaurant_info = load_restaurant_info(restaurant_id)
    menu_info = load_menu_info(restaurant_id)
    adress_info = load_restaurant_adress(restaurant_info[0].AddressID)
    reviews_info = load_restaurant_reviews(restaurant_id)

    clientIDs = [review['ClientID'] for review in reviews_info]
    visitInfoIDs = [review['VisitInfoID'] for review in reviews_info]
    mealsIDs = [meal['MealID'] for meal in menu_info]

    visitInfo = load_visit_info(visitInfoIDs)
    clientInfo = load_client_info(clientIDs)
    allergen_info = load_allergen_info(mealsIDs)

    meals_by_visit = {}
    for review in reviews_info:
        visit_id = review.VisitInfoID
        meals = conn.execute(text("""
            SELECT Meals.MealID, Meals.MealName 
            FROM Meals 
            JOIN VisitInfosMeals ON Meals.MealID = VisitInfosMeals.MealID 
            WHERE VisitInfosMeals.VisitInfoID = :visit_id
        """), {"visit_id": visit_id}).mappings().all()
        meals_by_visit[visit_id] = meals

    if (session["user_type"] == "CL"): 
        return render_template('client_UI.html', restaurant=restaurant_info[0], menu=menu_info, adress=adress_info[0], reviews=reviews_info, visitInfo = visitInfo, client = clientInfo, allergens_info = allergen_info, meals_by_visit=meals_by_visit)
    elif (session["user_type"] == "MO"):
        return render_template('moderator_UI.html', restaurant=restaurant_info[0], menu=menu_info, adress=adress_info[0], reviews=reviews_info, visitInfo = visitInfo, client = clientInfo, allergens_info = allergen_info, meals_by_visit=meals_by_visit)
    elif (session["user_type"] == "OW"):
        return render_template('owner_UI.html', restaurant=restaurant_info[0], menu=menu_info, adress=adress_info[0], reviews=reviews_info, visitInfo = visitInfo, client = clientInfo, allergens_info = allergen_info, meals_by_visit=meals_by_visit)

@app.route('/internet_food_db/add_review/<int:restaurant_id>', methods=['POST'])
def add_review(restaurant_id):
    if 'loggedin' not in session or not session['loggedin']:
        return redirect(url_for('login'))

    # Retrieve form data
    comment = request.form['comment']
    stars = request.form['stars']
    client_id = session['id']
    visit_details_type = request.form['visit_details_type']
    visit_details_rating = request.form['visit_details_rating']
    visit_details = f"{visit_details_type}: {visit_details_rating}"
    visit_date = request.form['visit_date']
    visit_hours = request.form['visit_hours']
    total_pay = request.form['total_pay']
    mod_id = 1
    opinion = request.form['opinion']
    date = datetime.now().strftime('%Y-%m-%d')

    meals = request.form.getlist('meals')

    if not comment or not stars or not visit_details_type or not visit_details_rating or not visit_date or not visit_hours or not total_pay or not mod_id or not opinion:
        return "Missing required fields", 400

    # Insert new visit info
    statement_add_visitinfo = text("""
        INSERT INTO VisitInfos (Details, VisitDate, VisitHours, TotalPay)
        VALUES (:details, :visit_date, :visit_hours, :total_pay)
    """)

    conn.execute(statement_add_visitinfo, {
        'details': visit_details,
        'visit_date': visit_date,
        'visit_hours': visit_hours,
        'total_pay': total_pay
    })
    conn.commit()

    # Retrieve the last inserted VisitInfoID
    visit_info_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

    # Insert new review
    statement_add_review = text("""
        INSERT INTO Reviews (RestaurantID, VisitInfoID, ClientID, ModID, Date, Comment, Stars, Opinion)
        VALUES (:restaurant_id, :visit_info_id, :client_id, :mod_id, :date, :comment, :stars, :opinion)
    """)

    conn.execute(statement_add_review, {
        'restaurant_id': restaurant_id,
        'visit_info_id': visit_info_id,
        'client_id': client_id,
        'mod_id': mod_id,
        'date': date,
        'comment': comment,
        'stars': stars,
        'opinion': opinion
    })

    statement_add_visitinfos_meals = text("""
        INSERT INTO VisitInfosMeals (VisitInfoID, MealID)
        VALUES (:visit_info_id, :meal_id)
    """)

    for meal_id in meals:
        conn.execute(statement_add_visitinfos_meals, {
            'visit_info_id': visit_info_id,
            'meal_id': meal_id
        })

    conn.commit()

    return redirect(url_for('restaurant_page', restaurant_id=restaurant_id))

@app.route('/internet_food_db/add_meal/<int:restaurant_id>', methods=['POST'])
def add_meal(restaurant_id):
    if 'loggedin' not in session or not session['loggedin']:
        return redirect(url_for('login'))

    meal_name = request.form['meal_name']
    price = request.form['price']
    allergens = request.form['allergens']

    if not meal_name or not price:
        return "Missing required fields", 400

    # Find the MenuID for the given RestaurantID
    menu_id_result = conn.execute(text("SELECT MenuID FROM Menus WHERE RestaurantID = :restaurant_id"), {"restaurant_id": restaurant_id})
    menu_id = menu_id_result.scalar()

    if not menu_id:
        return "Menu not found", 404

    # Insert new meal
    statement_add_meal = text("""
        INSERT INTO Meals (MenuID, MealName, Price)
        VALUES (:menu_id, :meal_name, :price)
    """)

    conn.execute(statement_add_meal, {
        'menu_id': menu_id,
        'meal_name': meal_name,
        'price': price
    })
    meal_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
    if allergens:
        allergen_list = [a.strip() for a in allergens.split(',')]
        statement_add_allergen = text("""
            INSERT INTO Allergens (MealID, Name)
            VALUES (:meal_id, :name)
        """)

        for allergen in allergen_list:
            conn.execute(statement_add_allergen, {
                'meal_id': meal_id,
                'name': allergen
            })

    conn.commit()

    return redirect(url_for('restaurant_page', restaurant_id=restaurant_id))


# SEARCH BAR HOMEPAGE
@app.route('/internet_food_db/home/', methods=['GET', 'POST'])
def search_for_restaurant():

    if request.method == 'POST' and 'restaurant_name' in request.form:
        
        restaurant_name = request.form['restaurant_name']

        result = conn.execute(statement=text("""SELECT RestaurantID FROM Restaurants WHERE RestaurantName = :restaurant_name LIMIT 1"""), parameters={"restaurant_name" : restaurant_name})
        
        restaurant_result = result.fetchone()

        if restaurant_result:
            # print(restaurant_result[0])

            return redirect(url_for('restaurant_page', restaurant_id=restaurant_result[0]))

    return redirect(url_for('home'))

@app.route('/internet_food_db/home/add_restaurant/', methods=['GET', 'POST'])
def add_restaurant():
    if session["user_type"] != "OW": # only owner types can add restaurants
        return redirect(url_for('home'))

    if request.method == 'POST' and 'restaurant_name' in request.form:
        restaurant_name = request.form['restaurant_name']

        street = request.form['street']
        streetnumber = request.form['streetnumber']
        zipcode = request.form['zipcode']
        city = request.form['city']
        country = request.form['country']

        cuisine = request.form['cuisine']

        statement_insert_restaurant = text("INSERT INTO Restaurants (RestaurantName, Cuisine, AddressID) VALUES (:restaurant_name, :cuisine, LAST_INSERT_ID())")
        statement_insert_restaurantsowners = text("""INSERT INTO RestaurantsOwners (RestaurantID, OwnerID) VALUES (LAST_INSERT_ID(), :owner_id)""")

        conn.execute(statement=statement_addresses, parameters={"street": street, "streetnumber" : streetnumber, "zipcode" : zipcode, "city" : city, "country" : country})

        conn.execute(statement=statement_insert_restaurant, parameters={"restaurant_name" : restaurant_name, "cuisine" : cuisine})

        conn.execute(statement=statement_insert_restaurantsowners, parameters={"owner_id" : session["id"]}) # the last inserted id was the restaurant

        conn.commit()

        msg = 'You just added a restaurant!'

    return render_template('add_restaurant.html', username=session["username"], id = session["id"])


@app.route('/internet_food_db/home/remove_review/<int:review_id>', methods=['GET', 'POST'])
def remove_review(review_id):
    if request.method == 'POST' and 'reason' in request.form:

        reason = request.form["reason"]
        # adds the review to the badreviews table
        statement_bad_reviews = text("""INSERT INTO BadReviews (ModID, ReviewID, Reason) VALUES (:mod_id, :review_id, :reason);""")

        # set the review to bad by altering boolean value attribute "IsBad"
        statement_reviews = text("""UPDATE Reviews SET IsBad = TRUE WHERE (ReviewID = :review_id);""")

        conn.execute(statement=statement_bad_reviews, parameters={"mod_id" : session["id"], "review_id" : review_id, "reason" : reason})

        conn.execute(statement=statement_reviews, parameters={"review_id" : review_id})

        conn.commit()


    return render_template('remove_review.html')

#lit le fichier sql
def load_query_from_file(file_path, query_name):
    with open(file_path, 'r') as file:
        sql_script = file.read()

    queries = sql_script.split(';')
    for query in queries:
        if query_name in query:
            return query.strip()
    return None

@app.route('/internet_food_db/home/high_rated/<filter_type>', methods=['GET'])
def filter_page(filter_type):
    sql_request = ''
    html_file = ''
    match (filter_type):
        case "get_high_rated_restaurants":
            sql_request = '../impl/request1.sql'
            html_file = 'filter_page.html'

    with open(sql_request) as file:
        query = text(file.read())
        result_ = conn.execute(query)

        result = result_.mappings().all()

        restaurants = [dict(row) for row in result]
        return render_template(html_file, restaurants=restaurants)
    # return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='localhost', debug=True)

