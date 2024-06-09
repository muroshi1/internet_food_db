

-- 5. Le code postal de la ville dans laquelle les restaurants sont les moins bien notés en moyenne
SELECT 
    Addresses.ZipCode, Restaurants.Stars
FROM 
    Addresses
    JOIN Restaurants 
        ON Restaurants.AddressID = Addresses.AddressID
GROUP BY
    Addresses.ZipCode,  Restaurants.Stars
ORDER BY
    AVG(DISTINCT Restaurants.Stars) ASC
LIMIT 
    1
;
