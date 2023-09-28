CREATE TABLE player
(
    player_id int not null identity(1,1),
    player_name varchar(255) not null,
    team varchar(255),
    team_score int not null,
    average_player_score int not null,
    player_score int not null,
    stamina int not null,
    technique int not null,
    ball_leader int not null,
    aggression int not null,
    tournament varchar(255),
    version int not null,
    primary key (player_id)
);

CREATE TABLE team_selection
(
    player_id int not null identity(1,1),
    player_name varchar(255) not null,
    team varchar(255),
    tournament varchar(255),
    field nvarchar(255) not null,
    primary key (player_id)
);

CREATE TABLE scores
(
    score_id int not null identity(1,1),
    team_a varchar(255),
    score_a int not null,
    team_b varchar(255),
    score_b int not null,
    entered_by varchar(255),
    entered_date varchar(255),
    entered_time varchar(255),
    field nvarchar(255) not null,
    primary key(score_id)
);
