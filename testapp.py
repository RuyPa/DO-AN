import signal
import time
import os
from flask import Flask, jsonify
import threading

# Biến trạng thái để theo dõi quá trình dừng hoặc tiếp tục
is_paused = False

app = Flask(__name__)

# Hàm để xử lý khi nhận tín hiệu tạm dừng
def handle_pause(sig, frame):
    global is_paused
    if not is_paused:
        print("Process paused. Press Ctrl+Z to stop or send SIGCONT to resume.")
        is_paused = True
    while is_paused:
        time.sleep(1)  # Giữ trạng thái chờ khi đang tạm dừng

# Hàm để xử lý khi nhận tín hiệu tiếp tục
def handle_resume(sig, frame):
    global is_paused
    if is_paused:
        print("Process resumed.")
        is_paused = False

# Gán tín hiệu Ctrl+Z để tạm dừng
signal.signal(signal.SIGTSTP, handle_pause)
# Gán tín hiệu SIGCONT để tiếp tục
signal.signal(signal.SIGCONT, handle_resume)

# Tiến trình giả lập thực hiện một công việc dài
def long_running_process():
    print(f"Process PID: {os.getpid()}")
    for i in range(100):
        while is_paused:
            time.sleep(1)  # Giữ trạng thái chờ khi bị tạm dừng
        print(f"Working... Step {i}")
        time.sleep(2)  # Giả lập một công việc tốn thời gian

# Route để bắt đầu quá trình
@app.route('/start', methods=['GET'])
def start_process():
    thread = threading.Thread(target=long_running_process)
    thread.start()
    return jsonify({"message": "Long running process started", "pid": os.getpid()})

# Route để kiểm tra trạng thái server
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Server is running"})

if __name__ == '__main__':
    print(f"Server is running on PID: {os.getpid()}")
    app.run(debug=False)
