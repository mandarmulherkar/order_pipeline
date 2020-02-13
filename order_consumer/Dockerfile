FROM python:3.8.0-alpine
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ENV DATABASE_URL postgresql://postgres:postgres@db:5432/orders
ENV APP_SETTINGS config:DevelopmentConfig
RUN mkdir /code
WORKDIR /code
RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

CMD ["/bin/sh", "/code/start.sh"]

