from flask import Flask
from views import blueprint

def create_app():
    my_app = Flask(__name__)
    my_app.register_blueprint(blueprint)
    return my_app


app = create_app()


if __name__ == '__main__':
    app.run()
