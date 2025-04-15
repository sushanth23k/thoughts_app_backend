# THOUGHTS PROJECT

## Commands for Project Setup

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Process to set environment into workspace in VSCode
Cmd + Shift + P

Python: Select Interpreter

./venv/bin/python

# Install dependencies
pip install -r requirements.txt

# Run the development server
python manage.py runserver

# Create Django project
django-admin startproject thoughts_project

# Create a new Django app
python manage.py startapp thoughts

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver

# Run local Redis Server
redis-server

redis-server --port 6379 --dbfilename dump.rdb --dir /tmp

# Command to Delete all the .DS_Store files
find . -name "._*" -type f -delete

# Git commit and push command
git add . && git commit -a -m "commit" && git push

## Articles for Reference

[Backend Frameworks for AI Development in 2024](https://medium.com/@cubode/whats-the-best-backend-framework-for-ai-development-in-2024-django-fastapi-or-flask-d52c165ea20c)

[Cheap Solutions for Databases](https://medium.com/@soumitsr/a-broke-b-chs-guide-to-tech-start-up-choosing-vector-database-cloud-serverless-prices-3c1ad4c29ce7)
