FROM python:3.8-slim

WORKDIR /

RUN apt-get update && apt-get -y install cron

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY run_tests.py .
COPY tests/ ./tests/
COPY Input/*.csv ./Input/ 

RUN echo "0 * * * * cd /app && python run_tests.py >> /var/log/cron.log 2>&1" > /etc/cron.d/api-cron-tests
RUN chmod 0644 /etc/cron.d/api-cron-tests
RUN crontab /etc/cron.d/api-cron-tests

RUN touch /var/log/cron.log
RUN chmod 0666 /var/log/cron.log

CMD cron && tail -f /var/log/cron.log