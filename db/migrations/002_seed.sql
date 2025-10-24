INSERT INTO users (name, region_code) VALUES ('Araya', 'ET-MK');
INSERT INTO households (user_id, household_size, monthly_income) VALUES (1, 4, 3000);
INSERT INTO transactions (household_id, type, category, amount) VALUES
 (1, 'recurring', 'rent', 1000),
 (1, 'recurring', 'food', 1200),
 (1, 'variable', 'transport', 200),
 (1, 'variable', 'phone', 150),
 (1, 'variable', 'school', 150);
