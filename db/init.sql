DROP TABLE IF EXISTS high_stress_users;

CREATE TABLE high_stress_users  (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  stress_score FLOAT NOT NULL,
  "timestamp" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

