# Branch status
## (main)

[![Pull Request Tests](https://github.com/jprendiville/python-fpl/actions/workflows/pull-request-tests.yml/badge.svg?branch=main)](https://github.com/jprendiville/python-fpl/actions/workflows/pull-request-tests.yml)
## (develop)

[![Pull Request Tests](https://github.com/jprendiville/python-fpl/actions/workflows/pull-request-tests.yml/badge.svg?branch=develop)](https://github.com/jprendiville/python-fpl/actions/workflows/pull-request-tests.yml)

# Installing
pip install -r requirements.txt

# Configuring in IntelliJ
Set the Project SDK

Import module
 - Source pointing to the root

In Facets
 - Specify the manage.py

Add a run configuration
 - Django Server
 - Environment variable	PYTHONUNBUFFERED=1;DJANGO_SETTINGS_MODULE=fpl.settings

Run the migrations
 - python manage.py migrate
 - python manage.py makemigrations
 - python manage.py migrate

# Running the server
python .\manage.py runserver --settings=fpl.settings

# Migrating models to the database
Create a migration file to track any changes made to the model/class and update the db
- python .\manage.py makemigrations

This gets created in the migrations folder

Now run the migration to create/update the db
- python .\manage.py migrate

# Creating an admin super user
python .\manage.py createsuperuser
http://127.0.0.1:8000/admin/

# Regenerate requirements.txt
- pip install pipreqs
- pipreqs /path/to/project

# Tweeting
- Rename the twitter_config.env.example to twitter_config.env and populate:
  - API_KEY = <your_api_key>
  - API_SECRET = <your_api_secret>
  - ACCESS_TOKEN = <your_access_token>
  - ACCESS_TOKEN_SECRET = <your_access_token_secret> 


# Other notes
django-admin startproject fpl

create urls/views

create templates

# Install scripts
Scripts to run pre or post migrations can be added to the install-scripts folder.
They need to be named in the format "pre-install*" or "post-install*". They will be run in order and archived to the archive folder after.
Examples are:
```
echo "Running pre-install script 001..."
psql -U <user> -d <database> -c "update <table> set <field> = <something>;"
echo "Pre-install script 001 completed."
```

```
echo "Running post-install script 001..."
rm -f /path/to/unwanted/file
echo "Post-install script 001 completed."
```

# Gitflow
## Creating a feature branch
This creates a branch, adds a new file (ie changes), commits it and pushes to github.
The "finish" does a fast forward merge and deletes the local branch.
---
- git checkout develop
- git push --set-upstream origin develop (only need to do once)
- git flow feature start feature_branch
- git branch -a
- make changes, and stage the changes 
  - git add -u (adds staged, but not tracked)
- git commit -m 'feature complete'
- git flow feature finish feature_branch
- git push origin

## Creating a release branch
- git flow release start '0.1.0'
- git branch -a
- git push --set-upstream origin release/0.1.0 (only need to do once)

If you need to make changes to release after finding something while testing, otherwise just go to Finish the Release:
touch release.html
- git add -u (adds staged, but not tracked)
- git commit -m 'release fix'
- git push origin

## Finish the release
- git flow release finish '0.1.0'
- vi/editor will pop up for message to merge to main.
- vi/editor will pop up. Asks for tag, so give it one, same a release version.
- vi/editor will pop up for message to merge to develop.

## Update main
- git checkout main
- git push origin
- git push origin --tags

Now the push to production will happen.