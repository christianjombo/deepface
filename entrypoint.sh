# Example content
echo "Starting the application..."
exec "$@"

gunicorn -c gunicorn.conf.py --timeout=7200 --bind=0.0.0.0:5000 --log-level=debug --access-logformat='%(h)s - - [%(t)s] "%(r)s" %(s)s %(b)s %(L)s' --access-logfile=- "app:create_app()"
