#app.py
from flask import Flask
from flasgger import Swagger
from models.database import db
import time
import random
from raft import RAFTFactory
from models.electro_scooter import ElectroScooter
# Defining the service credentials.
service_info = {
    "host" : "127.0.0.1",
    "port" : 8001,
    "leader" : None
}

# Stopping the start up of the service for a couple of seconds to chose a candidate.
time.sleep(random.randint(1,3))
# Creating the CRUD functionalities.
crud = RAFTFactory(service_info).create_server()

def create_app():
    app = Flask(__name__)

    # Configure Swagger
    app.config['SWAGGER'] = {
        'title': 'Your API Title',
        'description': 'Your API Description',
    }


    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/db_scooters2'

    db.init_app(app)
    Swagger(app, template_file='swagger.yml')
    return app

if __name__ == '__main__':
    app = create_app()
    import routes
    app.run(host = service_info["host"],
            port = service_info["port"])