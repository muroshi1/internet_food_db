-- 3. Les 10 clients ayant consommé le plus de plats mexicains
SELECT 
    Clients.Name
FROM 
    Clients 
    JOIN Reviews 
        ON Reviews.ClientID = Clients.ClientID
    JOIN Restaurants 
        ON Reviews.RestaurantID = Restaurants.RestaurantID
    JOIN Menus 
        ON Restaurants.RestaurantID = Menus.RestaurantID
    JOIN Meals 
        ON Menus.MenuID = Meals.MenuID
WHERE 
    Restaurants.Cuisine = 'mexicain' 
GROUP BY 
    Clients.ClientID
ORDER BY 
    count(distinct Meals.MealID) desc
LIMIT 
    10
;
