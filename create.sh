rm app.db
rm -r migrations
python create.py
python manage.py db init
