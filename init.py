import pymysql.cursors
import settings

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

db = pymysql.connect(host=settings.DBHOST,
            port=settings.DBPORT,
			user=settings.DBUSER,
			password=settings.DBPASSWD,
			db=settings.DBDATABASE,
			charset='utf8mb4',
            cursorclass= pymysql.cursors.DictCursor)
cursor = db.cursor()

def CheckDBVersion():
    sql = "CheckDBVersion"
    cursor.callproc(sql)
    result = cursor.fetchall()
    return int(result[0]['KeyValue'])

def initialize():
    if (CheckDBVersion == 1):
        return
    else:
        print('Detected First run. Double Checking for Existing data.')
        danger = False
        cursor.execute("""
            SHOW TABLES;
        """)
        tables = cursor.fetchall()
        exists = []
        for row in tables:
            exists.append(row['Tables_in_'.strip() + settings.DBDATABASE.strip()])
        if exists != []:
            print(bcolors.WARNING + 'The Database Tables ' + ','.strip().join(exists).strip() + ' Already exist.' + bcolors.ENDC)
            print(bcolors.FAIL + 'If you continue, they will be dropped.' + bcolors.ENDC)
            danger = True
        if danger:
            print(bcolors.FAIL + bcolors.UNDERLINE + bcolors.BOLD + 'The above Dangerous Circumstances have been detected. Significant Data Loss is possible.' + bcolors.ENDC)
            b = input('''If you have read and understand the above warnings and wish to continue, type [Yes, do as I say!]:\n''')
            if (b != 'Yes, do as I say!'):
                print('Exiting')
                sys.exit()
            print('Continuing')
        else:
            print(bcolors.OKGREEN + 'No Danger here!' + bcolors.ENDC)
        # Below here is the actual initialization. it will be done automatically if no issues were found or after confirmation by user if they are.
        print('Initializing')

        for table in exists:
            cursor.execute('DROP TABLE IF EXISTS ' + table.strip() + ';'.strip())
        cursor.fetchall()
        cursor.execute('''
CREATE TABLE RPCurBotKeys (
    KeyName varchar(32) NOT NULL,
    KeyValue varchar(32) NOT NULL,
    PRIMARY KEY (KeyName)
);
        ''')
        cursor.execute('''
INSERT INTO RPCurBotKeys (KeyName, KeyValue) VALUES
('DBVersion', '1')
        ''')
        cursor.execute('''
CREATE OR REPLACE PROCEDURE CheckDBVersion()
  BEGIN
    SELECT KeyValue FROM RPCurBotKeys
    WHERE (KeyName = 'DBVersion');
  END
        ''')
        cursor.fetchall()
        db.commit()