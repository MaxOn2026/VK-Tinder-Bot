from database.models.db_manager import DBManager

def setup_tables():
    db_manager = DBManager()
    
    locations = """
    CREATE TABLE locations(
	id SERIAL PRIMARY KEY,
	LOCATION VARCHAR(256),
	longitude DECIMAL(9,6) DEFAULT NULL,
	latitude DECIMAL(9,6) DEFAULT NULL
);
    """
    db_manager.execute_query(locations)
    
    users = """
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
    """
    db_manager.execute_query(users)
    
    interests = """
    CREATE TABLE interests(
	id SERIAL PRIMARY KEY,
	title VARCHAR(256)
);
    """
    db_manager.execute_query(interests)
    
    users_interests = """
    CREATE TABLE users_interests(
	user_id INT REFERENCES users(id),
	interest_id INT REFERENCES interests(id),
	PRIMARY KEY(user_id, interest_id)
);

    """
    db_manager.execute_query(users_interests)
    
    likes = """
    CREATE TABLE likes(
	id SERIAL PRIMARY KEY,
	user_id INT REFERENCES users(id),
	liked_user_id INT REFERENCES users(id),
	action VARCHAR(20),CHECK(action IN ('like', 'dislike', 'block', 'view'))
	created_at TIMESTAMP DEFAULT NOW(),
	UNIQUE(user_id, liked_user_id)
);
    """
    db_manager.execute_query(likes)
    
    matches = """
    CREATE TABLE matches(
	id SERIAL PRIMARY KEY,
	user_id_1 INT REFERENCES users(id),
	user_id_2 INT REFERENCES users(id),
	created_at TIMESTAMP DEFAULT NOW(),
	UNIQUE(user_id_1, user_id_2),
	CHECK(user_id_1 < user_id_2)
)
    """
    db_manager.execute_query(matches)
    
def setup_indexes():
    """ Создание индексов для оптимизации запросов """
    pass