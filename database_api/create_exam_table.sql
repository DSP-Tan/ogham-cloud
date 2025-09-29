-- ['year', 'page', 'text', 'x0', 'y0', 'x1', 'y1', 'common_font', 'mode_font', 'font_size', 'category', 'cluster']

DROP TABLE IF EXISTS english_hl;
CREATE TABLE IF NOT EXISTS english_hl(
      id          INTEGER
    , year        INTEGER
    , page        INTEGER
    , text        VARCHAR
    , x0          FLOAT 
    , y0          FLOAT
    , x1          FLOAT
    , y1          FLOAT
    , common_font VARCHAR(30)
    , mode_font   VARCHAR(30)
    , font_size   FLOAT
    , category    VARCHAR(20)
    , cluster     INTEGER
);

\copy english_hl FROM 'english_p1_al_exams.csv' DELIMITER ',' CSV HEADER;
