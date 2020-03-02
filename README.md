# order_pipeline

Build all the services

docker-compose build


Run all the services

docker-compose up


Check the Dashboard

http://localhost:5005/index


Bring down services

docker-compose down

Redis - docker exec -it <redis> bash

Postgres - docker exec -it <redis> bash
  - psql -U postgres
  - \c orders
  - \dt
