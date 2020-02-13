DROP TABLE test_table;

DROP TABLE received_orders;
CREATE TABLE received_orders (
  id SERIAL PRIMARY_KEY,
  name VARCHAR(512) NOT NULL,
  service VARCHAR(128),
  status VARCHAR(64),
  ordered_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

DROP TABLE items;
CREATE TABLE items (
  id SERIAL PRIMARY_KEY,
  order_id INTEGER REFERENCES received_orders(id),
  name NOT NULL VARCHAR(128),
  quantity INTEGER NOT NULL,
  price_per_unit INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);