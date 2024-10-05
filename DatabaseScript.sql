CREATE TABLE Contests (
    ContestID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Date DATE NOT NULL,
    Division ENUM('Div.1', 'Div.2') NOT NULL,
    Participants INT
);

create table ProblemSets  (
	ProblemSetID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Time_limit INT NOT NULL,
    Memory_limit INT NOT NULL
    );
    
create table Users (
	UserID INT PRIMARY KEY AUTO_INCREMENT,
    ScreenName VARCHAR(255) UNIQUE NOT NULL,
    City VARCHAR(255),
    Country VARCHAR(255),
    Organization VARCHAR(255),
    num_friends INT,
    num_contributions INT,
    Reg_duration INT, 
    ProblemsSolved INT,
    DaysInRow INT 
);

CREATE TABLE Contest_ProblemSets (
    ContestID INT,
    ProblemSetID INT,
    PRIMARY KEY (ContestID, ProblemSetID),
    FOREIGN KEY (ContestID) REFERENCES Contests(ContestID),
    FOREIGN KEY (ProblemSetID) REFERENCES ProblemSets(ProblemSetID)
);

CREATE TABLE ContestStandings (
    ContestID INT,
    UserID INT,
    Ranking INT,  -- could not use "Rank"             
    Score INT,              
    PRIMARY KEY (ContestID, UserID),
    FOREIGN KEY (ContestID) REFERENCES Contests(ContestID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE Writers (
    WriterID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL
);

CREATE TABLE Tags (
    TagID INT PRIMARY KEY AUTO_INCREMENT,
    TagName VARCHAR(255) NOT NULL
);

CREATE TABLE ProblemSet_Tags (
    ProblemSetID INT,
    TagID INT,
    PRIMARY KEY (ProblemSetID, TagID),
    FOREIGN KEY (ProblemSetID) REFERENCES ProblemSets(ProblemSetID),
    FOREIGN KEY (TagID) REFERENCES Tags(TagID)
);

CREATE TABLE ContestWriters (
    ContestID INT,
    WriterID INT,
    PRIMARY KEY (ContestID, WriterID),
    FOREIGN KEY (ContestID) REFERENCES Contests(ContestID),
    FOREIGN KEY (WriterID) REFERENCES Writers(WriterID)
);

CREATE TABLE Attempts(
	AttemptID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    ProblemSetID INT,
    Verdict ENUM('Accepted', 'Wrong Answer', 'Runtime Error', 'Compilation Error', 'Time Limit Exceeded', 'Memory Limit Exceeded') NOT NULL, -- still trying to figure out all verdicts
	Date_Time DATETIME NOT NULL,
    Language VARCHAR(255) NOT NULL,
    Duration INT,
    MemoryUsage INT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (ProblemSetID) REFERENCES ProblemSets(ProblemSetID)        
);

