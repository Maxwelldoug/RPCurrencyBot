-- v1 ---------------------------------------------------

CREATE TABLE RPCurBotKeys (
    KeyName varchar(32) NOT NULL,
    KeyValue varchar(32) NOT NULL,
    PRIMARY KEY (KeyName)
);

INSERT INTO RPCurBotKeys (KeyName, KeyValue) VALUES
('DBVersion', '1');

CREATE OR REPLACE PROCEDURE CheckDBVersion()
  BEGIN
    SELECT KeyValue FROM RPCurBotKeys
    WHERE KeyName = 'DBVersion';
  END;

CREATE OR REPLACE PROCEDURE SetDBVersion(IN newVersion int unsigned)
  BEGIN
    UPDATE RPCurBotKeys 
    SET KeyValue = CAST(newVersion as varchar(32))
    WHERE KeyName = 'DBVersion';
  END;

-- v2 ---------------------------------------------------

CREATE TABLE Characters (
  UserID varchar(32),
  CharacterName varchar(32),
  PRIMARY KEY (UserID, CharacterName)
);

CREATE TABLE Currencies (
  CurrencyName varchar(32),
  CurrencyDesc varchar(1024),
  PRIMARY KEY (CurrencyName)
);

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

CREATE TABLE Transactions (
  TransactionID int unsigned AUTO_INCREMENT,
  AccountID int,
  TransactionDesc varchar(64),
  Amount bigint,
  PRIMARY KEY (TransactionID),
  FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID)
);

CREATE OR REPLACE PROCEDURE AddAccount(IN UIDin varchar(32), IN CharName varchar(32), IN Currency varchar(32))
  BEGIN
    INSERT INTO Accounts (UserID, CharacterName, CurrencyName, Balance) VALUES
    (UIDin, CharName, Currency, 0);
  END;

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
  END;

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
  END;

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
  END;
