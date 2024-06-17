source venv/bin/activate
isort src
flake8 src --max-line-length 99
coverage run --source='src/landing' src/manage.py test landing