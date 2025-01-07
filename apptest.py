from flask import Flask

apptest = Flask(__name__)

@apptest.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    # Chạy ứng dụng trên 0.0.0.0 (cho phép truy cập từ mọi địa chỉ IP) và cổng 5000
    apptest.run(host='0.0.0.0', port=5000)
