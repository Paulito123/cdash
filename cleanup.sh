#!/bin/sh

echo "Removing sensitive files..."
rm -f .env.prod
rm -f .env.dev
rm -f .env.prod.db
rm -f ./services/web/manage.prod.py
echo "Sensitive files removed..."


