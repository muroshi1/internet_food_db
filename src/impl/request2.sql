-- 2. Le restaurant avec le plat le plus cher
SELECT
    Restaurants.RestaurantName,
    Meals.Price
FROM
    Restaurants
    JOIN Menus ON Restaurants.RestaurantID = Menus.RestaurantID
    JOIN Meals ON Menus.MenuID = Meals.MenuID
WHERE
    Meals.Price = (
        SELECT MAX(Meals.Price)
        FROM Meals
    );
