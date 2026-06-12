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
	birth_year SMALLINT NOT NULL,
	location_id INT REFERENCES locations(id),
	vk_id BIGINT UNIQUE NOT NULL,
	created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
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

CREATE TABLE likes(
	id SERIAL PRIMARY KEY,
	user_id INT REFERENCES users(id),
	liked_user_id INT REFERENCES users(id),
	action VARCHAR(20),CHECK(action IN ('like', 'dislike', 'block', 'view'))
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

-- Поиск по возрасту
CREATE INDEX idx_users_birthdate ON users(birthdate);

-- Поиск по полу и предпочтениям
CREATE INDEX idx_users_gender_looking ON users(gender, looking_for);

-- Геопоиск (потребуется PostGIS или отдельный индекс)
CREATE INDEX idx_locations_coords ON locations(longitude, latitude);

-- Частые JOIN
CREATE INDEX idx_users_location ON users(location_id);
CREATE INDEX idx_users_interests_user ON users_interests(user_id);