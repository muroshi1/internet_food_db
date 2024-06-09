--1. Les restaurants ayant un avis moyen de 3 ou plus
SELECT Restaurants.RestaurantName
FROM Restaurants 
WHERE Restaurants.Stars >= 3
;

--2. Le restaurant avec le plat le plus cher
SELECT Restaurants.RestaurantName
FROM Restaurants
JOIN Menus ON Restaurants.RestaurantID = Menus.RestaurantID
JOIN Meals ON Menus.MenuID = Meals.MenuID
WHERE max(Meals.Price)
;

--3. Les 10 clients ayant consommé le plus de plats mexicains
SELECT Clients.Name
FROM Clients 
JOIN Reviews ON Reviews.ClientID = Clients.ClientID
JOIN Restaurants ON Reviews.RestaurantID = Restaurants.RestaurantID
JOIN Menus ON Restaurants.RestaurantID = Menus.RestaurantID
JOIN Meals ON Menus.MenuID = Meals.MenuID
WHERE Restaurants.Cuisine = 'mexicain' 
GROUP BY Clients.ClientID
ORDER BY count(distinct Meals.MealID) desc
LIMIT 10
;

-- 4. Le restaurant non-asiatique proposant le plus de plats qui sONt généralement proposés dans des restaurants asiatiques (basez-vous sur le nombre de restaurants de chaque type qui proposent le plat)
SELECT r1.RestaurantName
FROM Restaurants r1
JOIN Menus ON Restaurants.RestaurantID = Menus.RestaurantID
JOIN Meals ON Menus.MealID = Meals.MealID
JOIN Restaurants r2 ON r2.Cuisine = 'asiatique' AND r2.RestaurantID = Meals.RestaurantID
WHERE not r1.Cuisine = 'asiatique'
GROUP BY r1.RestaurantName
ORDER BY count(distinct Meals.MealID) desc
LIMIT 1
;



--5. Le code postal de la ville dans laquelle les restaurants sont les moins bien notés en moyenne
SELECT Addresses.ZipCode
FROM Addresses
JOIN Restaurants ON Restaurants.AddressID = Addresses.AddressID
GROUP BY Addresses.ZipCode
ORDER BY Restaurants.Stars ASC
LIMIT 1
;

--6. Pour chaque tranche de score moyen (1/5, 2/5, 3/5, ...) de restaurant, le type de nourriture le plus représenté
SELECT Restaurants.Cuisine
FROM Restaurants
JOIN Menus ON Restaurants.RestaurantID = Menus.RestaurantID
GROUP BY CASE
        WHEN Restaurants.Stars = 1 THEN '1/5'
        WHEN Restaurants.Stars = 2 THEN '2/5'
        WHEN Restaurants.Stars = 3 THEN '3/5'
        WHEN Restaurants.Stars = 4 THEN '4/5'
        WHEN Restaurants.Stars = 5 THEN '5/5'
        END
ORDER BY Restaurants.Stars DESC
;


