from flask import Flask
import configparser
import db_client

DATABASE = 'DATABASE'

app = Flask(__name__)

def read_config():
  conf = configparser.ConfigParser()
  with open('config.ini') as f:
    conf.read_file(f)
  return conf

if __name__ == '__main__':
  conf = read_config()
  db_client = db_client.DbClient(uri=conf['DATABASE']['Address'], prt=conf['DATABASE']['Port'], uname=conf['DATABASE']['User'], pw=conf['DATABASE']['Password'], db=conf['DATABASE']['Database'])

  app.run(host='0.0.0.0', port=5000)