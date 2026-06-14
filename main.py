from flask import Flask
import multiprocessing
import stream, chat_handler

app = Flask(__name__)

@app.route('/')
def home():
    return "INFINITY GEN 🚫💸"

if __name__ == "__main__":
    multiprocessing.Process(target=stream.run_stream).start()
    multiprocessing.Process(target=chat_handler.start_chat_loop).start()
    app.run(host='0.0.0.0', port=10000)