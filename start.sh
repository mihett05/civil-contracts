#/!bin/bash

cd src

python3 -m pipenv run python manage.py migrate
python3 -m pipenv run python manage.py initadmin

python3 -m pipenv run python manage.py runserver 0.0.0.0:8001
