# movie-rater-backend
An API application allowing to retrieve film information (thanks to [The Movie DB](https://www.themoviedb.org/)) and establish your own rating

Built using [Python FastAPI](https://fastapi.tiangolo.com)

Deployed on Heroku at: [https://bagaze-movie-rater-backend.herokuapp.com/](https://bagaze-movie-rater-backend.herokuapp.com/)

## Prerequisites

[Docker](https://www.docker.com/get-started)

## Setup

Create your configuration file based on the sample:

`cp ./env-sample ./local-env`

Build the docker image

`docker build -t baptistegaze/movie-rater-back-img .`

Run the database migration using alembic

`alembic upgrade head`

## Run

`docker run -d --name movie-rater -p 9090:9090 baptistegaze/movie-rater-back-img`

You can access:
- [OpenAPI documentation](http://localhost:9090/docs)
- [Redoc](http://localhost:9090/redoc)

## Create a super admin

Run the following command in your deployed environment

`poetry run create_admin email username password`

## API Endpoints

Once the application is running, the API is available at [http://localhost:9090](http://localhost:9090)

Main endpoints are:

- `/movies`
- `/weekly_movies`
- `/ratings`