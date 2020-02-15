DROP TABLE IF EXISTS received_orders;
CREATE TABLE received_orders (
  id SERIAL PRIMARY KEY,
  name VARCHAR(512) NOT NULL,
  service VARCHAR(128),
  status VARCHAR(64),
  ordered_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

DROP TABLE IF EXISTS items;
CREATE TABLE items (
  id SERIAL PRIMARY KEY,
  order_id INTEGER REFERENCES received_orders(id),
  name VARCHAR(128) NOT NULL,
  quantity INTEGER NOT NULL,
  price_per_unit INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);