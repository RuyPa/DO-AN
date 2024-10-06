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
from routes.routes import api_routes
from routes.sample_route import sample_bp
from routes.label_route import label_bp
from routes.model_sample_route import model_sample_bp

# @app.before_first_request
# def setup():
#     create_tables()

app.register_blueprint(api_routes)
app.register_blueprint(sample_bp)
app.register_blueprint(label_bp)
app.register_blueprint(model_sample_bp)


if __name__ == '__main__':
    app.run(debug=False)
