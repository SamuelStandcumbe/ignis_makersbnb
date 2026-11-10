DROP TABLE IF EXISTS requests;
DROP TABLE IF EXISTS spaces;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
CREATE TABLE spaces (
    id SERIAL PRIMARY KEY,
    space_name VARCHAR(255) NOT NULL,
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
    # requested_space
    # requester
    );

INSERT INTO users (name, email, password) VALUES ('Alice Example', 'alice@example.com', 'password123');
INSERT INTO users (name, email, password) VALUES ('Bob Example', 'bob@example.com', 'password456');

INSERT INTO spaces
INSERT INTO 