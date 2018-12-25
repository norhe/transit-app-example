from flask import Flask, request
from datetime import datetime
import configparser
import json


import db_client

DATABASE = 'DATABASE'
dbc = None

app = Flask(__name__)

def read_config():
  conf = configparser.ConfigParser()
  with open('config.ini') as f:
    conf.read_file(f)
  return conf

@app.route('/customers', methods=['GET'])
def get_customers():
    global dbc
    customers = dbc.get_customer_records(10)
    print(customers)
    return json.dumps(customers)

@app.route('/customers', methods=['POST'])
def create_customer():
    global dbc
    print(dict(request.form))
    customer = {k:v[0] for (k,v) in dict(request.form).items()}
    print(customer)
    new_record = dbc.insert_customer_record(customer)
    print(new_record)
    return json.dumps(new_record)

if __name__ == '__main__':
  conf = read_config()
  dbc = db_client.DbClient(uri=conf['DATABASE']['Address'], prt=conf['DATABASE']['Port'], uname=conf['DATABASE']['User'], pw=conf['DATABASE']['Password'], db=conf['DATABASE']['Database'])

  app.run(host='0.0.0.0', port=5000)