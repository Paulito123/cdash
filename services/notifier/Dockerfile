# pull official base image
FROM python:3.9.5-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y netcat libpq-dev gcc cron

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/

# Execute permissions
RUN chmod +x /usr/src/app/project/job_*.py
# RUN find . -type f -iname "*.py" -exec chmod +x {} \;
#     && \
#     find . -type f -iname "*.sh" -exec chmod +x {} \;

# Setup cron
COPY ./crontab.development /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob
RUN chmod 0600 /etc/cron.d/cronjob

# Run entrypoint
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]