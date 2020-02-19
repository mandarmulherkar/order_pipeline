DROP TABLE IF EXISTS received_order;
CREATE TABLE received_order (
  id SERIAL PRIMARY KEY,
  name VARCHAR(512) NOT NULL,
  service VARCHAR(128),
  status VARCHAR(64),
  ordered_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

DROP TABLE IF EXISTS menu_item;
CREATE TABLE menu_item (
  id SERIAL PRIMARY KEY,
  order_id INTEGER REFERENCES received_order(id),
  name VARCHAR(128) NOT NULL,
  quantity INTEGER NOT NULL,
  price_per_unit INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);