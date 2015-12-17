DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Posts;

CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
	username TEXT,
    password TEXT
);

CREATE TABLE Posts (
	id INTEGER PRIMARY KEY,
	title TEXT,
    username TEXT,
    date TEXT,
    last_update TEXT,
    post TEXT,
    is_published TEXT,
    category TEXT
);

INSERT INTO Users
(username, password)
VALUES
('BarackObama', 'illinois'),
('GeorgeBush', 'texas'),
('BillClinton', 'arkansas'),
('RonaldReagan', 'california'),
('JimmyCarter', 'georgia');