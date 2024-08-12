CREATE TABLE RPCurBotKeys (
    KeyName varchar(32) NOT NULL,
    KeyValue varchar(32) NOT NULL,
    PRIMARY KEY (KeyName)
);

INSERT INTO RPCurBotKeys (KeyName, KeyValue) VALUES
('DBVersion', '1');

CREATE OR REPLACE PROCEDURE CheckDBVersion()
  BEGIN
    SELECT * FROM RPCurBotKeys
    WHERE (KeyValue = 'DBVersion');
  END

-- ---------------------------------------------------

