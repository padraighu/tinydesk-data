FROM puckel/docker-airflow:latest

WORKDIR /usr/local/airflow

# install additional Python packages
COPY requirements.txt /usr/local/airflow

RUN pip install --no-cache-dir -r /usr/local/airflow/requirements.txt
