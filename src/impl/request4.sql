
-- 4. Le restaurant non-asiatique proposant le plus de plats qui sONt généralement proposés dans des restaurants asiatiques (basez-vous sur le nombre de restaurants de chaque type qui proposent le plat)
SELECT 
    r1.RestaurantName, Meals.MealName
FROM 
    Restaurants r1
    JOIN Menus 
        ON r1.RestaurantID = Menus.RestaurantID
    JOIN Meals 
        ON Menus.MenuID = Meals.MenuID
    JOIN Restaurants r2 
        ON r2.Cuisine = 'asiatique' 
WHERE 
    not r1.Cuisine = 'asiatique'
GROUP BY 
    r1.RestaurantName, MealName
ORDER BY 
    count(distinct Meals.MealID) desc
LIMIT 
    1
;
