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
    try:
        sql = "CheckDBVersion"
        cursor.callproc(sql)
        result = cursor.fetchall()
        return int(result[0]['KeyValue'])
    except:
        return 0

def initialize():
    v = CheckDBVersion()
    if (v == 3):
        return [db,cursor]
    elif (v == 0):
        print('Detected First run. Double Checking for Existing data.')
        danger = False
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        exists = []
        for row in tables:
            exists.append(row['Tables_in_'.strip() + settings.DBDATABASE.strip()])
        if exists != []:
            print(bcolors.WARNING + 'The Database Tables ' + ','.strip().join(exists).strip() + ' Already exist, but the bot is not configured.' + bcolors.ENDC)
            print(bcolors.FAIL + 'If you continue, they will be dropped as an empty database is required.' + bcolors.ENDC)
            danger = True
        if danger:
            print(bcolors.FAIL + bcolors.UNDERLINE + bcolors.BOLD + 'The above Dangerous Circumstances have been detected. Significant Data Loss is possible.' + bcolors.ENDC)
            b = input('If you have read and understand the above warnings and wish to continue, type [Yes, do as I say!]:\n')
            if (b != 'Yes, do as I say!'):
                print('Exiting')
                sys.exit()
            print('Continuing')
            for table in exists:
                cursor.execute('DROP TABLE IF EXISTS ' + table.strip() + ';'.strip())
        else:
            print(bcolors.OKGREEN + 'No Danger here!' + bcolors.ENDC)
        # Below here is the actual initialization. it will be done automatically if no issues were found or after confirmation by user if they are.
    else:
        print("Updating DB from version" + str(v))

    print('Initializing')

    cursor.fetchall()
    
    if (v < 1):
        cursor.execute('''
CREATE TABLE RPCurBotKeys (
    KeyName varchar(32) NOT NULL,
    KeyValue varchar(32) NOT NULL,
    PRIMARY KEY (KeyName)
);
        ''')
        cursor.execute('''
INSERT INTO RPCurBotKeys (KeyName, KeyValue) VALUES
('DBVersion', '1');
        ''')
        cursor.execute('''
CREATE OR REPLACE PROCEDURE CheckDBVersion()
  BEGIN
    SELECT KeyValue FROM RPCurBotKeys
    WHERE KeyName = 'DBVersion';
  END
        ''')
        cursor.execute('''
CREATE OR REPLACE PROCEDURE SetDBVersion(IN newVersion int unsigned)
  BEGIN
    UPDATE RPCurBotKeys 
    SET KeyValue = CAST(newVersion as varchar(32))
    WHERE KeyName = 'DBVersion';
  END
        ''')
        cursor.fetchall()
        db.commit()
        v = 1

    if (v < 2):
        cursor.execute('''
CREATE TABLE Characters (
  UserID varchar(32),
  CharacterName varchar(32),
  PRIMARY KEY (UserID, CharacterName)
);
        ''')
        cursor.execute('''
CREATE TABLE Currencies (
  CurrencyName varchar(32),
  CurrencyDesc varchar(1024),
  PRIMARY KEY (CurrencyName)
);
        ''')
        cursor.execute('''
CREATE TABLE Accounts (
  AccountID int AUTO_INCREMENT,
  UserID varchar(32),
  CharacterName varchar(32),
  CurrencyName varchar(32),
  Balance bigint DEFAULT 0,
  PRIMARY KEY (AccountID),
  UNIQUE (UserID, CharacterName, CurrencyName),
  FOREIGN KEY (UserID, CharacterName) REFERENCES Characters(UserID, CharacterName),
  FOREIGN KEY (CurrencyName) REFERENCES Currencies(CurrencyName)
);
        ''')
        cursor.execute('''
CREATE TABLE Transactions (
  TransactionID int unsigned AUTO_INCREMENT,
  AccountID int,
  TransactionDesc varchar(64),
  Amount bigint,
  PRIMARY KEY (TransactionID),
  FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID)
);
        ''')
        cursor.execute('''
CREATE OR REPLACE PROCEDURE AddAccount(IN UIDin varchar(32), IN CharName varchar(32), IN Currency varchar(32))
  BEGIN
    INSERT INTO Accounts (UserID, CharacterName, CurrencyName, Balance) VALUES
    (UIDin, CharName, Currency, 0);
  END
        ''')
        cursor.execute('''
CREATE OR REPLACE PROCEDURE AddCharacter(IN CharName varchar(32), IN UIDin varchar(32))
  BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE current VARCHAR(32);
    DECLARE cur CURSOR FOR SELECT CurrencyName FROM Currencies;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Error handling: Check if Character already exists
    IF EXISTS (SELECT 1 FROM Characters WHERE UserID = UIDin AND CharacterName = CharName) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Character already exists for this user.';
    ELSE
        INSERT INTO Characters (UserID, CharacterName) 
        VALUES (UIDin, CharName);
    END IF;

    OPEN cur;

    lop: LOOP
        FETCH cur INTO current;
        IF done THEN 
            LEAVE lop;
        END IF;

        CALL AddAccount(UIDin, CharName, current);
    END LOOP lop;

    CLOSE cur;   
  END
        ''')
        cursor.execute('''
CREATE OR REPLACE PROCEDURE AddCurrency(IN CurrName varchar(32), IN CurrDesc varchar(1024))
  BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE current VARCHAR(32);
    DECLARE UIDin varchar(32);
    DECLARE cur CURSOR FOR SELECT UserID, CharacterName FROM Characters;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Error handling: Check if Currency already exists
    IF EXISTS (SELECT 1 FROM Currencies WHERE CurrencyName = CurrName) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Currency already exists.';
    ELSE
        INSERT INTO Currencies (CurrencyName, CurrencyDesc) VALUES
        (CurrName, CurrDesc);
    END IF;

    OPEN cur;

    lop: LOOP
      FETCH cur INTO UIDin, current;
      IF done THEN 
        LEAVE lop;
      END IF;

      CALL AddAccount(UIDin, current, CurrName);
    END LOOP lop;

    CLOSE cur; 
  END
        ''')
        cursor.execute('''
CREATE OR REPLACE PROCEDURE DoTransaction(IN UIDin varchar(32), IN CharName varchar(32), IN CurrName varchar(32), IN TransDesc varchar(64), IN Am int)
  BEGIN
    DECLARE acc int;
    SELECT AccountID INTO acc FROM Accounts
    WHERE UserID = UIDin AND CharacterName = CharName AND CurrencyName = CurrName;

    INSERT INTO Transactions (AccountID, TransactionDesc, Amount) VALUES
    (acc, TransDesc, Am);

    UPDATE Accounts
    SET Balance = Balance + Am
    WHERE AccountID = acc;
  END
        ''')

        cursor.fetchall()
        db.commit()
        v=2
        sql = "SetDBVersion"
        sqlargs = [2]
        cursor.callproc(sql, sqlargs)
        result = cursor.fetchall()
        db.commit()

    if (v < 3):
        cursor.execute('''
        CREATE OR REPLACE PROCEDURE DelCharacter(IN CharName varchar(32), IN UIDin varchar(32))
  BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE accID INT;
    DECLARE cur CURSOR FOR SELECT AccountID FROM Accounts WHERE UserID = UIDin AND CharacterName = CharName;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Open the cursor to get all AccountIDs related to the character
    OPEN cur;

    -- Loop through each account and delete associated transactions
    lop: LOOP
        FETCH cur INTO accID;
        IF done THEN 
            LEAVE lop;
        END IF;

        -- Delete all transactions related to the account
        DELETE FROM Transactions WHERE AccountID = accID;
    END LOOP lop;

    -- Close the cursor after processing
    CLOSE cur;

    -- Delete all accounts related to the character
    DELETE FROM Accounts WHERE UserID = UIDin AND CharacterName = CharName;

    -- Finally, delete the character itself
    DELETE FROM Characters WHERE UserID = UIDin AND CharacterName = CharName;
  END
        ''')
        cursor.execute('''
CREATE OR REPLACE PROCEDURE DelCurrency(IN CurrName varchar(32))
  BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE accID INT;
    DECLARE cur CURSOR FOR SELECT AccountID FROM Accounts WHERE CurrencyName = CurrName;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Open the cursor to get all AccountIDs related to the currency
    OPEN cur;

    -- Loop through each account and delete associated transactions
    lop: LOOP
        FETCH cur INTO accID;
        IF done THEN 
            LEAVE lop;
        END IF;

        -- Delete all transactions related to the account
        DELETE FROM Transactions WHERE AccountID = accID;
    END LOOP lop;

    -- Close the cursor after processing
    CLOSE cur;

    -- Delete all accounts related to the currency
    DELETE FROM Accounts WHERE CurrencyName = CurrName;

    -- Finally, delete the currency itself
    DELETE FROM Currencies WHERE CurrencyName = CurrName;
  END
        ''')
        cursor.execute('''
CREATE OR REPLACE PROCEDURE EditCurrency(IN CurrName varchar(32), IN CurrDesc varchar(1024))
  BEGIN
    -- Error handling: Check if the currency exists
    IF NOT EXISTS (SELECT 1 FROM Currencies WHERE CurrencyName = CurrName) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Currency does not exist.';
    ELSE
        -- Update the description of the existing currency
        UPDATE Currencies
        SET CurrencyDesc = CurrDesc
        WHERE CurrencyName = CurrName;
    END IF;
  END
        ''')
        cursor.execute('''
CREATE OR REPLACE PROCEDURE ZeroBal(IN CharName varchar(32), IN UIDin varchar(32))
  BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE accID INT;
    DECLARE cur CURSOR FOR SELECT AccountID FROM Accounts WHERE UserID = UIDin AND CharacterName = CharName;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Open the cursor to get all AccountIDs related to the character
    OPEN cur;

    -- Loop through each account
    lop: LOOP
        FETCH cur INTO accID;
        IF done THEN 
            LEAVE lop;
        END IF;

        -- Delete all transactions related to the account
        DELETE FROM Transactions WHERE AccountID = accID;

        -- Set the balance to 0 for the account
        UPDATE Accounts
        SET Balance = 0
        WHERE AccountID = accID;
    END LOOP lop;

    -- Close the cursor after processing
    CLOSE cur;
  END
        ''')

        cursor.fetchall()
        db.commit()
        v=2
        sql = "SetDBVersion"
        sqlargs = [3]
        cursor.callproc(sql, sqlargs)
        result = cursor.fetchall()
        db.commit()
        
    return [db,cursor]