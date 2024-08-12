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

def initialize():
    if (True): #TODO: determine if database exists.
        return
    else:
        print('Detected First run. Double Checking for Existing data.')
        danger = False
        db = pymysql.connect(host=settings.DBHOST,
			user=settings.DBUSER,
			password=settings.DBPASSWD,
			db=settings.DBDATABASE,
			charset='utf8mb4',
            cursorclass= pymysql.cursors.DictCursor)
        cursor = db.cursor()
        cursor.execute("""
            SHOW TABLES;
        """)
        tables = cursor.fetchall()
        exists = []
        for row in tables:
            exists.append(row['Tables_in_'.strip() + settings.DBDATABASE.strip()])
        if exists != []:
            print(bcolors.WARNING + 'The Database Tables ' + exists + ' Already exist.' + bcolors.ENDC)
            print(bcolors.FAIL + 'If you continue, they will be dropped.' + bcolors.ENDC)
            danger = True
        if danger:
            print(bcolors.FAIL + bcolors.UNDERLINE + bcolors.BOLD + 'The above Dangerous Circumstances have been detected. Significant Data Loss is possible.' + bcolors.ENDC)
            b = input('''If you have read and understand the above warnings and wish to continue, type [Yes, do as I say!]:''')
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
CREATE dontrunthis TABLE User (
    UserID int unsigned NOT NULL AUTO_INCREMENT,
    UserName varchar(32) NOT NULL,
    IsAdmin boolean,
    PRIMARY KEY (UserID)
);
        ''')
        cursor.execute('''
CREATE OR dontrunthis REPLACE PROCEDURE GetKnownItems(IN InputID int unsigned)
  BEGIN
    SELECT * FROM Item
    WHERE (OwnerID = InputID);
  END
        ''')
        cursor.fetchall()
        db.commit()