#!/bin/sh

echo "Removing shizzle before deployment..."
rm -f .env.dev
rm -f .env.dev.db
rm -f .env.dev.notifier
rm -f .gitignore
rm -f LICENSE
rm -f README.md

rm -f ./services/crawler/project/database/test.sql

rm -f ./services/notifier/Dockerfile
rm -f ./services/notifier/crontab.development
rm -f ./services/notifier/project/database/test.sql

rm -f ./services/web/Dockerfile
rm -f ./services/web/entrypoint.sh
rm -f ./services/web/secrets_dev.py
rm -f ./services/web/project/test.sql

rm -rf .git
rm -rf .idea

rm -f cleanup.sh

echo "Ready to deploy..."


