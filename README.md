Example service broker in python3
===

Goal: serve as a starting point to build your own service broker, as simple as humanly possible. See `app.py` and `example.py` to see just how simple the entire thing is.

This runs as a Cloud Foundry app, using gunicorn (gevent for concurrency) as http server. You can push this app to CF right away, you only need to configure two environment variables: `BROKER_USER` and `BROKER_PASSWORD`.

Uses https://github.com/eruvanos/openbrokerapi.
