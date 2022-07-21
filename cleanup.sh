#!/bin/sh

echo "Removing shizzle before deployment..."
rm -f .env.dev
rm -f .env.dev.db
rm -f .env.dev.notifier
rm -f .gitignore
rm -f LICENSE
rm -f README.md

rm -rf .git
rm -rf .idea

echo "Ready to deploy..."


