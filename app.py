from flask import Flask
from flask_cors import CORS


app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Cấu hình cơ sở dữ liệu
app.config['DB_HOST'] = 'localhost'
app.config['DB_USER'] = 'root'
app.config['DB_PASSWORD'] = '123456'
app.config['DB_DATABASE'] = 'traffic_sign'

# Import các module sau khi cấu hình cơ sở dữ liệu
from services.traffic_sign_service import create_tables
from routes import api_routes

# @app.before_first_request
# def setup():
#     create_tables()

app.register_blueprint(api_routes)

if __name__ == '__main__':
    app.run(debug=False)
