from flask import Flask
import configparser



app = Flask(__name__)

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8080)