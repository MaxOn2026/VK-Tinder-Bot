CREATE TABLE locations(
	id SERIAL PRIMARY KEY,
	LOCATION VARCHAR(256),
	longitude DECIMAL(9,6) DEFAULT NULL,
	latitude DECIMAL(9,6) DEFAULT NULL
);

CREATE TABLE users(
	id SERIAL PRIMARY KEY,
	name VARCHAR(256) NOT NULL,
	surname VARCHAR(256) NOT NULL,
	birthdate DATE,
	location_id INT REFERENCES locations(id),
	vk_id BIGINT UNIQUE NOT NULL,
	created_at TIMESTAMP DEFAULT NOW(),
	gender SMALLINT,
	looking_for SMALLINT,
	age_min SMALLINT DEFAULT 18,
	age_max SMALLINT DEFAULT 99,
	max_distance INT DEFAULT 50
);

CREATE TABLE interests(
	id SERIAL PRIMARY KEY,
	title VARCHAR(256)
);

CREATE TABLE users_interests(
	user_id INT REFERENCES users(id),
	interest_id INT REFERENCES interests(id),
	PRIMARY KEY(user_id, interest_id)
);

CREATE TABLE views_history(
	id SERIAL PRIMARY KEY,
	user_id INT REFERENCES users(id),
	viewed_user_id INT REFERENCES users(id)
);

CREATE TABLE blocked_users(
	id SERIAL PRIMARY KEY,
	user_id INT REFERENCES users(id),
	blocked_user_id INT REFERENCES users(id)
);

CREATE TABLE likes(
	id SERIAL PRIMARY KEY,
	user_id INT REFERENCES users(id),
	liked_user_id INT REFERENCES users(id),
	like_or_dislike BOOLEAN NOT NULL,
	created_at TIMESTAMP DEFAULT NOW(),
	UNIQUE(user_id, liked_user_id)
)

CREATE TABLE matches(
	id SERIAL PRIMARY KEY,
	user_id_1 INT REFERENCES users(id),
	user_id_2 INT REFERENCES users(id),
	created_at TIMESTAMP DEFAULT NOW(),
	UNIQUE(user_id_1, user_id_2),
	CHECK(user_id_1 < user_id_2)
)