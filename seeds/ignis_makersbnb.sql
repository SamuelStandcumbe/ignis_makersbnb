-- Needed for the no_double_booking rule on requests (lets space_id use = inside an EXCLUDE constraint)
CREATE EXTENSION IF NOT EXISTS btree_gist;

DROP TABLE IF EXISTS requests;
DROP TABLE IF EXISTS spaces;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
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
    host_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CONSTRAINT fk_space FOREIGN KEY (space_id) REFERENCES spaces(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_host FOREIGN key (host_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT valid_range CHECK (end_date >= start_date),
    -- Two APPROVED requests for the same space can never share a night (pending ones can)
    CONSTRAINT no_double_booking EXCLUDE USING gist (
        space_id WITH =,
        daterange(start_date, end_date, '[]') WITH &&
    ) WHERE (approved)
    );

INSERT INTO users (full_name, email, password, host) VALUES (
    'Alice Example',
    'alice@example.com',
    'scrypt:32768:8:1$ivbXQax5ryJvhuyU$67e46c6b01f0b9a7117538bd03796c8d36a324d9f6c8b510bbade1b41a6ac8bf63f629b466d05db10cd522c43c31fd76cf6d036d365cea8f9e19ea2b67ea83b5',
    TRUE
);
INSERT INTO users (full_name, email, password, host) VALUES (
    'Bob Example',
    'bob@example.com',
    'scrypt:32768:8:1$86HbV4IStqnYqIGO$085fb01fbddc70d1f74533692fc3d4b42bf8c3a2e3c2ba2bc70d5e95b7d31081163cc55c61b2a00a5488b339a8d8334cde0676c0ea6cc917699dc16713ed2d10',
    FALSE
);

INSERT INTO spaces (space_name, location, description, price, user_id) VALUES (
    'Fisherman''s cottage by the harbour',
    'Whitstable, Kent',
    'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.',
    95,
    1
);
INSERT INTO spaces (space_name, location, description, price, user_id) VALUES (
    'Stone barn in the Peak District',
    'Edale, Derbyshire',
    'Converted barn at the start of the Pennine Way. Boot room, drying rack and a big kitchen table.',
    140,
    1
);
INSERT INTO spaces (space_name, location, description, price, user_id) VALUES (
    'Bright studio near Brick Lane',
    'Shoreditch, London',
    'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.',
    120,
    1
);
INSERT INTO spaces (space_name, location, description, price, user_id) VALUES (
    'Coastal Retreat',
    'Deal, Kent',
    'A cosy seaside cottage with beautiful coastal views.',
    110,
    2
);

INSERT INTO requests (space_id, user_id, approved, start_date, end_date, host_id) VALUES (1, 2, FALSE, '2026-10-10', '2026-10-12', 1);
INSERT INTO requests (space_id, user_id, approved, start_date, end_date, host_id) VALUES (2, 2, TRUE, '2026-11-28', '2026-11-30', 1);
INSERT INTO requests (space_id, user_id, approved, start_date, end_date, host_id) VALUES (2, 2, TRUE, '2026-11-25', '2026-11-27', 1);
INSERT INTO requests (space_id, user_id, approved, start_date, end_date, host_id) VALUES (4, 1, FALSE, '2026-12-10', '2026-12-12', 2);
