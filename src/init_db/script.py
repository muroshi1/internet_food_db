import re
import json
import csv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, DataError
from xml.etree import ElementTree as ET
from datetime import datetime

# Create the database connection
engine = create_engine('mysql+mysqldb://root:1234@127.0.0.1/internet_food_db')
conn = engine.connect()

# Restaurant related statements
statement_check_restaurant = text("SELECT RestaurantID FROM Restaurants WHERE RestaurantName = :restaurant")
statement_update_restaurant = text("UPDATE Restaurants SET Cuisine = :cuisine, DeliveryOption = :delivery, AddressID = :addressID, PriceRange = :price_range, Stars = :rating  WHERE RestaurantName = :restaurant")
statement_insert_restaurant = text("INSERT INTO Restaurants (RestaurantName, Cuisine, DeliveryOption, AddressID, PriceRange, Stars) VALUES (:restaurant, :cuisine, :delivery, :addressID, :price_range, :rating)")

# Menu related statements
statement_check_menu = text("SELECT MenuID FROM Menus WHERE RestaurantID = :restaurantID")
statement_insert_menu = text("INSERT INTO Menus (RestaurantID) VALUES (:restaurantID)")

# Meal related statements
statement_check_menu_meal = text("SELECT MealID FROM Meals WHERE MenuID = :menuID AND MealName = :mealName")
statement_update_meal = text("UPDATE Meals SET Price = :price WHERE MenuID = :menuID AND MealName = :mealName")
statement_insert_meal = text("INSERT INTO Meals (MenuID, MealName, Price) VALUES (:menuID, :mealName, :price)")

# Allergen related statements
statement_insert_allergens = text("INSERT INTO Allergens (Name, MealID) VALUES (:name, :meal_id)")
statement_check_allergens = text("SELECT AllergenID FROM Allergens WHERE Name = :name")

# Address related statements
statement_check_address = text("SELECT AddressID FROM Addresses WHERE Street = :street AND StreetNumber = :number AND ZipCode = :zipcode AND City = :city AND Country = :country")
statement_insert_address = text("INSERT INTO Addresses (Street, StreetNumber, ZipCode, City, Country) VALUES (:street, :number, :zipcode, :city, :country)")

# Client related statements
statement_check_client = text("SELECT ClientID FROM Clients WHERE Name = :firstname AND Surname = :lastname")
statement_insert_client = text("INSERT INTO Clients (Name, Surname, Username, Password) VALUES (:firstname, :lastname, :username, :password)")

# Moderator related statements
statement_check_moderator = text("SELECT ModID FROM Moderators WHERE Name = :firstname AND Surname = :lastname")
statement_insert_moderator = text("INSERT INTO Moderators (Name, Surname, AddressID, Username, Password) VALUES (:firstname, :lastname, :addressID, :username, :password)")

# Owner related statements
statement_check_owner = text("SELECT OwnerID FROM Owners WHERE Name = :firstname AND Surname = :lastname")
statement_insert_owner = text("INSERT INTO Owners (Name, Surname, AddressID, Username, Password) VALUES (:firstname, :lastname, :addressID, :username, :password)")

# Restaurant-Owner relationship statement
statement_insert_restaurantsowners = text("INSERT INTO RestaurantsOwners (RestaurantID, OwnerID) VALUES (:restaurantID, :ownerID)")

# Visit information related statements
statement_check_visit_info = text("SELECT VisitInfoID FROM VisitInfos WHERE Details = :details AND VisitDate = :visit_date AND VisitHours = :visit_hours AND TotalPay = :total_pay")
statement_insert_visit_info = text("INSERT INTO VisitInfos (Details, VisitDate, VisitHours, TotalPay) VALUES (:details, :visit_date, :visit_hours, :total_pay)")

# Review related statements
statement_insert_review = text("INSERT INTO Reviews (RestaurantID, VisitInfoID, ClientID, ModID, Date, Comment, Stars, Opinion) VALUES (:restaurant_id, :visit_info_id, :client_id, :mod_id, :date, :comment, :stars, :opinion)")

# Visit information to meals relationship statement
statement_insert_visit_infos_meals = text("INSERT INTO VisitInfosMeals (VisitInfoID, MealID) VALUES (:visit_info_id, :meal_id)")

# Additional statement to check meal existence
statement_check_meal = text("SELECT MealID FROM Meals WHERE MealName = :mealName")

def import_reviews_tsv_to_mysql(tsv_file):
    with open(tsv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            try:
                if not all(row):  # Skip if any field is empty
                    continue

                comment, stars, visit_date_str, opinion, restaurant_name, visit_details, comment_date_str, meal_names, total_pay, start_hour, end_hour, client_name = row

                visit_date = datetime.strptime(visit_date_str, '%m/%d/%Y %H:%M').date()
                comment_date = datetime.strptime(comment_date_str, '%Y-%m-%d').date()
                total_pay = float(total_pay)
                stars = float(stars)  # Adjusting to float for fractional stars

                # Split client name
                client_firstname, client_lastname = client_name.split(" ")

                # Get or create visit info
                visit_info = {
                    'details': visit_details,
                    'visit_date': visit_date,
                    'visit_hours': start_hour + "h-" + end_hour + "h",
                    'total_pay': total_pay
                }
                visit_info_id = conn.execute(statement_check_visit_info, visit_info).scalar()
                if not visit_info_id:
                    conn.execute(statement_insert_visit_info, visit_info)
                    visit_info_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

                # Get client ID
                client = {
                    'firstname': client_firstname,
                    'lastname': client_lastname,
                    'addressID': 1,  # Assuming addressID is required but not present in the TSV, using a placeholder
                    'username' : client_firstname,
                    'password' : 1
                }
                client_id = conn.execute(statement_check_client, client).scalar()
                if not client_id:
                    conn.execute(statement_insert_client, client)
                    client_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

                # Get restaurant ID
                restaurant_id = conn.execute(statement_check_restaurant, {'restaurant': restaurant_name}).scalar()
                if not restaurant_id:
                    print(f"Restaurant not found: {restaurant_name}")
                    continue

                # Insert review
                review = {
                    'restaurant_id': restaurant_id,
                    'visit_info_id': visit_info_id,
                    'client_id': client_id,
                    'mod_id': 1,  # Assuming a moderator ID is required but not present in the TSV, using a placeholder
                    'date': comment_date,
                    'comment': comment,
                    'stars': stars,
                    'opinion': opinion
                }
                conn.execute(statement_insert_review, review)

                # Insert visit infos meals
                meal_names_list = meal_names.split(';')
                for meal_name in meal_names_list:
                    meal_name = meal_name.strip()
                    meal_id = conn.execute(statement_check_meal, {'mealName': meal_name}).scalar()
                    if meal_id:
                        visit_infos_meals = {
                            'visit_info_id': visit_info_id,
                            'meal_id': meal_id
                        }
                        # Check if the visit info meal combination already exists
                        existing = conn.execute(text("""
                            SELECT COUNT(*) FROM VisitInfosMeals
                            WHERE VisitInfoID = :visit_info_id AND MealID = :meal_id
                        """), visit_infos_meals).scalar()
                        if existing == 0:
                            conn.execute(statement_insert_visit_infos_meals, visit_infos_meals)

            except IntegrityError as e:
                print(f"IntegrityError: {e.orig}")
            except DataError as e:
                print(f"DataError: {e.orig}")
            except Exception as e:
                print(f"Error: {str(e)}")



def clean_price(price):
    cleaned_price = re.sub(r'[^\d.]', '', price)
    return float(cleaned_price)

def get_or_create_address(address):
    address_id = conn.execute(statement_check_address, address).scalar()
    if not address_id:
        conn.execute(statement_insert_address, address)
        address_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
    return address_id

def import_xml_to_mysql(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Load addresses from restaurateur.json into a dictionary
    addresses = {}
    with open('../../data/restaurateur.json', 'r', encoding='utf-8') as f:
        restaurateur_data = json.load(f)
        for entry in restaurateur_data:
            restaurant_name = entry['restaurant']
            address = entry['address']
            addresses[restaurant_name] = address

    for restaurant in root.findall('restaurant'):
        name = restaurant.find('name').text
        cuisine = restaurant.find('type').text
        delivery_option = restaurant.find('delivery').text
        rating = restaurant.find('evaluation').text
        price_range = restaurant.find('price_range').text

        delivery_option = 1 if delivery_option == 'Yes' else 0

        try:
            # Get the address for the restaurant
            address = addresses.get(name)
            if not address:
                raise ValueError(f"No address found for restaurant: {name}")

            # Get or create the address in the database
            address_id = get_or_create_address(address)

            # Check if the restaurant already exists
            restaurant_id = conn.execute(statement_check_restaurant, {'restaurant': name}).scalar()

            if not restaurant_id:
                # Insert new restaurant
                conn.execute(statement_insert_restaurant, {'restaurant': name, 'cuisine': cuisine, 'delivery': delivery_option, 'addressID': address_id, 'rating': rating, 'price_range':price_range})
                restaurant_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

            for menu in restaurant.findall('menu'):
                # Check if the menu already exists for this restaurant
                menu_id = conn.execute(statement_check_menu, {'restaurantID': restaurant_id}).scalar()

                if not menu_id:
                    # Insert new menu
                    conn.execute(statement_insert_menu, {'restaurantID': restaurant_id})
                    menu_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

                for meal in menu.findall('dish'):
                    meal_name = meal.find('name').text
                    price = clean_price(meal.find('price').text)

                    # Check if the meal already exists for this menu
                    meal_id = conn.execute(statement_check_menu_meal, {'menuID': menu_id, 'mealName': meal_name}).scalar()

                    for allergens in meal.findall('allergens'):
                        for allergen in allergens.findall('allergen'):

                            if meal_id:
                                # Update existing meal
                                conn.execute(statement_update_meal, {'menuID': menu_id, 'mealName': meal_name, 'price': price})
                            else:
                                # Insert new meal
                                conn.execute(statement_insert_meal, {'menuID': menu_id, 'mealName': meal_name, 'price': price})
                                meal_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

                            conn.execute(statement_insert_allergens, {'name' : allergen.text, 'meal_id' : meal_id})


        except IntegrityError as e:
            print(f"IntegrityError: {e.orig}")
        except Exception as e:
            print(f"Error: {str(e)}")



def import_json_data(file_path, statement_check, statement_insert):
    with open(file_path, 'r', encoding="utf-8") as f:
        data = json.load(f)
        for user in data:
            address_id = get_or_create_address(user["address"])
            user['addressID'] = address_id
            user['username'] = user['firstname']
            user['password'] = 1

            user_id = conn.execute(statement_check, user).scalar()
            if not user_id:
                conn.execute(statement_insert, user)

import_xml_to_mysql('../../data/restos.xml')

import_json_data('../../data/customers.json', statement_check_client, statement_insert_client)
import_json_data('../../data/moderators.json', statement_check_moderator, statement_insert_moderator)
import_json_data('../../data/restaurateur.json', statement_check_owner, statement_insert_owner)

import_reviews_tsv_to_mysql('../../data/valid_comments.tsv')

conn.commit()
conn.close()