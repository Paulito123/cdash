#!/bin/sh

echo "Removing sensitive files..."
rm -f .env.prod
rm -f .env.dev
rm -f .env.prod.db
echo "Sensitive files removed..."


