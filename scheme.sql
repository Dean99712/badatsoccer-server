CREATE TABLE team_selection
(
    player_id int not null identity(1,1),
    player_name varchar(255) not null,
    team       varchar(255),
    stamina            int not null,
    technique          int not null,
    ball_leader        int not null,
    aggression         int not null,
    tournament varchar(255),
    version            varchar(50),
    tournament_to_pick varchar(255),
    team_to_pick       varchar(255),
    field_auto nvarchar(50),
    date       varchar(50),
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
    entered_date varchar(50),
    entered_time varchar(50),
    field nvarchar(255) not null,
    primary key(score_id)
);