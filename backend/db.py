import mysql.connector
from mysql.connector import errorcode

TABLES = {}

customer_table = '''
CREATE TABLE IF NOT EXISTS `customers` (
    `cust_no` int(11) NOT NULL AUTO_INCREMENT,
    `birth_date` date NOT NULL,
    `first_name` varchar(32) NOT NULL,
    `last_name` varchar(32) NOT NULL,
    `create_date` date NOT NULL,
    `social_security_number` varchar(16) NOT NULL,
    `address` varchar(255) NOT NULL,
    `salary` varchar(16) NOT NULL,
    PRIMARY KEY (`cust_no`)
) ENGINE=InnoDB;'''

def init_db(uri, prt, uname, pw, db):
    conn = connect_db(uri, prt, uname, pw)
    cursor = conn.cursor()
    print("Preparing database {}...".format(db))
    cursor.execute('CREATE DATABASE IF NOT EXISTS `{}`'.format(db))
    cursor.execute('USE `{}`'.format(db))
    print("Preparing customer table...")
    cursor.execute(customer_table)

def connect_db(uri, prt, uname, pw):
    print('Connecting to {} with username {} and password {}'.format(uri, uname, pw))
    try:
        conn = mysql.connector.connect(user=uname, password=pw, host=uri, port=prt)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
