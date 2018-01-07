rm app.db
python -c 'from models import db; db.create_all()'
