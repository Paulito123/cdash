#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# Start cron
echo "Wait for data: 10m"
sleep 10m
echo "Copying variables..."
printenv | grep 'DATABASE_URL\|BOT_TOKEN\|CHAT_ID\|ENABLE_TELEGRAM\|ERROR_NOTIF_DELAY'  > /etc/environment
echo "Starting cron..."
cron -f
