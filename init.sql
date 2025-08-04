-- Таблица пользователей
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Таблица фильмов
CREATE TABLE movies (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL
);

-- Таблица лайков фильмов
CREATE TABLE likes (
    user_id UUID NOT NULL,
    movie_id UUID NOT NULL,
    rating INTEGER CHECK (rating >= 0 AND rating <= 10),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
);

-- Таблица отзывов
CREATE TABLE reviews (
    id UUID PRIMARY KEY,
    movie_id UUID NOT NULL,
    user_id UUID NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Таблица лайков отзывов
CREATE TABLE review_likes (
    user_id UUID NOT NULL,
    review_id UUID NOT NULL,
    rating INTEGER CHECK (rating >= 0 AND rating <= 10),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, review_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
);

CREATE TABLE review_stats (
    review_id UUID PRIMARY KEY,
    total_likes INTEGER DEFAULT 0,
    total_dislikes INTEGER DEFAULT 0,
    avg_rating DOUBLE PRECISION,
    total_ratings INTEGER DEFAULT 0,
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
);

-- Таблица закладок
CREATE TABLE bookmarks (
    user_id UUID NOT NULL,
    movie_id UUID NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
);

-- Таблица статистики фильмов (для кэширования агрегированных данных)
CREATE TABLE movie_stats (
    movie_id UUID PRIMARY KEY,
    total_likes INTEGER DEFAULT 0,
    total_dislikes INTEGER DEFAULT 0,
    avg_rating DOUBLE PRECISION,
    total_reviews INTEGER DEFAULT 0,
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
);

-- Индексы для оптимизации запросов
CREATE INDEX idx_likes_user_id ON likes(user_id);
CREATE INDEX idx_likes_movie_id ON likes(movie_id);
CREATE INDEX idx_reviews_movie_id ON reviews(movie_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_review_likes_review_id ON review_likes(review_id);
CREATE INDEX idx_bookmarks_user_id ON bookmarks(user_id);
CREATE INDEX idx_bookmarks_movie_id ON bookmarks(movie_id);