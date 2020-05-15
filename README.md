# Stripe Billing charging for subscriptions

## Requirements

- Python 3
- [Configured .env file](../README.md)

## How to run

1. Create and activate a new virtual environment

```
python3 -m venv /path/to/new/virtual/environment
source /path/to/new/virtual/environment/venv/bin/activate
```

1. Create and activate a new virtual environment

```
python3 -m venv /path/to/new/virtual/environment
source /path/to/new/virtual/environment/venv/bin/activate
```

2. Configure .env and subscriptioon.db

```
rename .env_example to .env
rename subscriptioon_example.db to subscriptioon.db
```

4. Export and run the application

```
export FLASK_APP=server.py
python3 -m flask run --port=4242
```

5. Go to `localhost:4242` in your browser to see the demo
