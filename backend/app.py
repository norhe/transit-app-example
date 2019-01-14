from flask import Flask, request, render_template

from datetime import datetime
import configparser
import json
import logging
import logging.config

import db_client

dbc = None
vclient = None

log_level = {
  'CRITICAL' : 50,
  'ERROR'	   : 40,
  'WARN'  	 : 30,
  'INFO'	   : 20,
  'DEBUG'	   : 10
}

logger = logging.getLogger('app')

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

def read_config():
  conf = configparser.ConfigParser()
  with open('config.ini') as f:
    conf.read_file(f)
  return conf

@app.route('/customers', methods=['GET'])
def get_customers():
    global dbc
    customers = dbc.get_customer_records()
    logger.debug('Customers: {}'.format(customers))
    return json.dumps(customers)

@app.route('/customers', methods=['POST'])
def create_customer():
    global dbc
    logging.debug("Form Data: {}".format(dict(request.form)))
    customer = {k:v for (k,v) in dict(request.form).items()}
    logging.debug('Customer: {}'.format(customer))
    if 'create_date' not in customer.keys():
      customer['create_date'] = datetime.now().isoformat()
    new_record = dbc.insert_customer_record(customer)
    logging.debug('New Record: {}'.format(new_record))
    return json.dumps(new_record)

@app.route('/customers', methods=['PUT'])
def update_customer():
    global dbc
    logging.debug('Form Data: {}'.format(dict(request.form)))
    customer = {k:v for (k,v) in dict(request.form).items()}
    logging.debug('Customer: {}'.format(customer))
    new_record = dbc.update_customer_record(customer)
    logging.debug('New Record: {}'.format(new_record))
    return json.dumps(new_record)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/records', methods=['GET'])
def records():
    records = json.loads(get_customers())
    return render_template('records.html', results = records)

@app.route('/dbview', methods=['GET'])
def dbview():
    global dbc
    records = dbc.get_customer_records(raw = True)
    return render_template('dbview.html', results = records)

@app.route('/add', methods=['GET'])
def add():
    return render_template('add.html')

@app.route('/add', methods=['POST'])
def add_submit():
    records = create_customer()
    return render_template('records.html', results = json.loads(records), record_added = True)

@app.route('/update', methods=['GET'])
def update():
    return render_template('update.html')

@app.route('/update', methods=['POST'])
def update_submit():
    records = update_customer()
    return render_template('records.html', results = json.loads(records), record_updated = True)

if __name__ == '__main__':
  conf = read_config()
  
  logging.basicConfig(
    level=log_level[conf['DEFAULT']['LogLevel']],
    format='%(asctime)s - %(levelname)8s - %(name)9s - %(funcName)15s - %(message)s'
  )

  try:
    dbc = db_client.DbClient()

    if conf.has_section('VAULT'):
      if conf['VAULT']['Enabled'].lower() == 'true':
        dbc.init_vault(addr=conf['VAULT']['Address'], token=conf['VAULT']['Token'], path=conf['VAULT']['KeyPath'], key_name=conf['VAULT']['KeyName'])
        if conf['VAULT']['DynamicDBCreds'].lower() == 'true':
          logger.debug('db_auth')
          dbc.vault_db_auth(conf['VAULT']['DynamicDBCredsPath'])
          dbc.init_db(uri=conf['DATABASE']['Address'], 
          prt=conf['DATABASE']['Port'], 
          uname=dbc.username, 
          pw=dbc.password, 
          db=conf['DATABASE']['Database']
          )
      else:
        dbc.init_db(
          uri=conf['DATABASE']['Address'], 
          prt=conf['DATABASE']['Port'], 
          uname=conf['DATABASE']['User'], 
          pw=conf['DATABASE']['Password'], 
          db=conf['DATABASE']['Database']
        )
    logger.debug(dbc)          
    logger.info('Starting Flask server on {} listening on port {}'.format('0.0.0.0', '5000'))
    app.run(host='0.0.0.0', port=5000)

  except Exception as e:
    logging.error("There was an error starting the server: {}".format(e))
  