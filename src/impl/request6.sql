
-- 6. Pour chaque tranche de score moyen (1/5, 2/5, 3/5, ...) de restaurant, le type de nourriture le plus représenté
SELECT
    CASE 
        WHEN AVG(Stars) >= 0 AND AVG(Stars) <= 1 THEN '1/5'
        WHEN AVG(Stars) >= 1 AND AVG(Stars) <= 2 THEN '2/5'
        WHEN AVG(Stars) >= 2 AND AVG(Stars) <= 3 THEN '3/5'
        WHEN AVG(Stars) >= 3 AND AVG(Stars) <= 4 THEN '4/5'
        WHEN AVG(Stars) >= 4 AND AVG(Stars) <= 5 THEN '5/5'
    END AS Rating_Category,
    Cuisine
FROM
    Restaurants
GROUP BY Cuisine
ORDER BY Rating_Category asc;
