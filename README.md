# tinydesk-data

Data pipeline to power [Tiny Desk Insights](https://tinydesk-insights.netlify.app/)

It requests data from the Youtube API, stores them in postgres tables, then aggregates the data and persists the results as JSON stored on S3.

## Components

The app consists of:

- Airflow
    - Web UI is on port `8080`
- Postgres
- pgadmin
    - Web UI is on port `80`

## Deploy

The app uses docker compose to deploy.

- Set environment varibles under `.env`
    - See `docker-compoes.yaml` for the list of env variables that need to be set
- Run `docker-compose build`
- Run `docker-compose up`

The `setup.sh` script is intended to be run as a setup script on a EC2 container.
