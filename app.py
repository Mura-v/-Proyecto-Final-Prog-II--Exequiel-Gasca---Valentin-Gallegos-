from src import create_app,db
from src.models import Users,Post

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)