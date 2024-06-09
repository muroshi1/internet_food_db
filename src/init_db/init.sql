DROP DATABASE IF EXISTS `internet_food_db`;
CREATE DATABASE `internet_food_db`;
USE `internet_food_db`;

CREATE TABLE Addresses (
    AddressID INT NOT NULL AUTO_INCREMENT,
    Street VARCHAR(255) NOT NULL,
    StreetNumber INT NOT NULL,
    ZipCode VARCHAR(255) NOT NULL,
    City VARCHAR(255) NOT NULL,
    Country VARCHAR(255) NOT NULL,
    PRIMARY KEY (AddressID)
);

CREATE TABLE Allergens (
    AllergenID INT NOT NULL AUTO_INCREMENT,
    MealID INT NOT NULL,
    Name VARCHAR(255) NOT NULL,
    PRIMARY KEY (AllergenID)
);

CREATE TABLE Restaurants (
    RestaurantID INT NOT NULL AUTO_INCREMENT,
    RestaurantName VARCHAR(255) NOT NULL,
    AddressID INT DEFAULT NULL,
    Cuisine VARCHAR(255) DEFAULT NULL,
    PriceRange VARCHAR(255) NOT NULL DEFAULT '1',
    Stars FLOAT DEFAULT NULL,
    DeliveryOption BOOLEAN DEFAULT NULL,
    OpeningHours VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (RestaurantID),
    KEY fk_Restaurants_Addresses_idx (AddressID),
    CONSTRAINT fk_Restaurants_Addresses FOREIGN KEY (AddressID) REFERENCES Addresses (AddressID) ON UPDATE CASCADE
);

CREATE TABLE PriceRanges (
    PriceRangeID INT NOT NULL AUTO_INCREMENT,
    RangeName VARCHAR(255) NOT NULL,
    PRIMARY KEY (PriceRangeID)
);

CREATE TABLE Menus (
    MenuID INT NOT NULL AUTO_INCREMENT,
    RestaurantID INT NOT NULL,
    PRIMARY KEY (MenuID),
    KEY fk_Menus_Restaurants_idx (RestaurantID),
    CONSTRAINT fk_Menus_Restaurants FOREIGN KEY (RestaurantID) REFERENCES Restaurants (RestaurantID) ON UPDATE CASCADE
);

CREATE TABLE Meals (
    MealID INT NOT NULL AUTO_INCREMENT,
    MenuID INT NOT NULL,
    MealName VARCHAR(255) NOT NULL,
    Price FLOAT NOT NULL,
    PRIMARY KEY (MealID),
    KEY fk_Meals_Menus_idx (MenuID),
    CONSTRAINT fk_Meals_Menus FOREIGN KEY (MenuID) REFERENCES Menus (MenuID) ON UPDATE CASCADE
);

CREATE TABLE Owners (
    OwnerID INT NOT NULL AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Surname VARCHAR(255) NOT NULL,
    AddressID INT NOT NULL,
    Username VARCHAR(50) DEFAULT NULL,
    Password VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (OwnerID),
    KEY fk_Owners_Addresses_idx (AddressID),
    CONSTRAINT fk_Owners_Addresses FOREIGN KEY (AddressID) REFERENCES Addresses (AddressID) ON UPDATE CASCADE
);

CREATE TABLE RestaurantsOwners (
    RestaurantID INT NOT NULL,
    OwnerID INT NOT NULL,
    PRIMARY KEY (RestaurantID, OwnerID),
    CONSTRAINT fk_RestaurantsOwners_Restaurants FOREIGN KEY (RestaurantID) REFERENCES Restaurants (RestaurantID) ON UPDATE CASCADE,
    CONSTRAINT fk_RestaurantsOwners_Owners FOREIGN KEY (OwnerID) REFERENCES Owners (OwnerID) ON UPDATE CASCADE
);

CREATE TABLE Clients (
    ClientID INT NOT NULL AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Surname VARCHAR(255) NOT NULL,
    AddressID INT DEFAULT NULL,
    Username VARCHAR(50) DEFAULT NULL,
    Password VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (ClientID),
    KEY fk_Clients_Addresses_idx (AddressID),
    CONSTRAINT fk_Clients_Addresses FOREIGN KEY (AddressID) REFERENCES Addresses (AddressID) ON UPDATE CASCADE
);

CREATE TABLE Moderators (
    ModID INT NOT NULL AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Surname VARCHAR(255) NOT NULL,
    AddressID INT NOT NULL,
    Username VARCHAR(50) DEFAULT NULL,
    Password VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (ModID),
    KEY fk_Moderators_Addresses_idx (AddressID),
    CONSTRAINT fk_Moderators_Addresses FOREIGN KEY (AddressID) REFERENCES Addresses (AddressID) ON UPDATE CASCADE
);

CREATE TABLE VisitInfos (
    VisitInfoID INT NOT NULL AUTO_INCREMENT,
    Details VARCHAR(255) DEFAULT NULL,
    VisitDate DATE DEFAULT NULL,
    VisitHours VARCHAR(255) DEFAULT NULL,
    TotalPay INT DEFAULT NULL,
    PRIMARY KEY (VisitInfoID)
);

CREATE TABLE Reviews (
    ReviewID INT NOT NULL AUTO_INCREMENT,
    RestaurantID INT NOT NULL,
    VisitInfoID INT NOT NULL,
    ClientID INT NOT NULL,
    ModID INT NOT NULL,
    Date DATE DEFAULT NULL,
    Comment MEDIUMTEXT DEFAULT NULL,
    Stars FLOAT NOT NULL,
    Opinion VARCHAR(255) DEFAULT NULL,

    IsBad BOOLEAN DEFAULT FALSE,

    PRIMARY KEY (ReviewID),

    KEY fk_Reviews_Restaurants_idx (RestaurantID),
    KEY fk_Reviews_VisitInfos_idx (VisitInfoID),
    KEY fk_Reviews_Clients_idx (ClientID),
    KEY fk_Reviews_Moderators_idx (ModID),
    CONSTRAINT fk_Reviews_Restaurants FOREIGN KEY (RestaurantID) REFERENCES Restaurants (RestaurantID) ON UPDATE CASCADE,
    CONSTRAINT fk_Reviews_VisitInfos FOREIGN KEY (VisitInfoID) REFERENCES VisitInfos (VisitInfoID) ON UPDATE CASCADE,
    CONSTRAINT fk_Reviews_Clients FOREIGN KEY (ClientID) REFERENCES Clients (ClientID) ON UPDATE CASCADE,
    CONSTRAINT fk_Reviews_Moderators FOREIGN KEY (ModID) REFERENCES Moderators (ModID) ON UPDATE CASCADE
);

CREATE TABLE VisitInfosMeals (
    VisitInfoID INT NOT NULL,
    MealID INT NOT NULL,
    PRIMARY KEY (VisitInfoID, MealID),
    CONSTRAINT fk_VisitInfosMeals_VisitInfos FOREIGN KEY (VisitInfoID) REFERENCES VisitInfos (VisitInfoID) ON UPDATE CASCADE,
    CONSTRAINT fk_VisitInfosMeals_Meals FOREIGN KEY (MealID) REFERENCES Meals (MealID) ON UPDATE CASCADE
);

CREATE TABLE BadReviews(
    ModID INT NOT NULL,
    ReviewID INT NOT NULL,
    Reason VARCHAR(255) DEFAULT NULL,

    PRIMARY KEY (ModID, ReviewID),
    CONSTRAINT fk_BadReviews_Moderators FOREIGN KEY (ModID) REFERENCES Moderators (ModID) ON UPDATE CASCADE,
    CONSTRAINT fk_BadReviews_Reviews FOREIGN KEY (ReviewID) REFERENCES Reviews (ReviewID) ON UPDATE CASCADE
);
