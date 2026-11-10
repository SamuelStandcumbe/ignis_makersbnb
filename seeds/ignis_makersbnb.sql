DROP TABLE IF EXISTS requests;
DROP TABLE IF EXISTS spaces;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    host BOOLEAN NOT NULL
);
CREATE TABLE spaces (
    id SERIAL PRIMARY KEY,
    space_name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    user_id INTEGER NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    space_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    approved BOOLEAN NOT NULL DEFAULT FALSE,
    requested_date DATE NOT NULL,
    CONSTRAINT fk_space FOREIGN KEY (space_id) REFERENCES spaces(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

INSERT INTO users (username, email, password, host) VALUES ('Alice Example', 'alice@example.com', 'password123', TRUE);
INSERT INTO users (username, email, password, host) VALUES ('Bob Example', 'bob@example.com', 'password456', FALSE);

INSERT INTO spaces (space_name, location, description, price, user_id) VALUES ('Fishermans cottage by the harbour', 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.' , 95, 1);
INSERT INTO spaces (space_name, location, description, price, user_id) VALUES ('Stone barn in the Peak District', 'Edale, Derbyshire', 'Converted barn at the start of the Pennine Way. Boot room, drying rack and a big kitchen table.', 140, 1);

INSERT INTO requests (space_id, user_id, approved, requested_date) VALUES (1, 2, FALSE, '2026-10-10');
INSERT INTO requests (space_id, user_id, approved, requested_date) VALUES (2, 2, TRUE, '2026-10-11');
