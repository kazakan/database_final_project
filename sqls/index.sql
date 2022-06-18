
create index mv_year_idx on movie(mv_year) ;
create index mv_net_rating on movie(netizen_rating) ;
create index mv_rating on movie(watched_rating_num) ;

create index wm_country_idx on where_made(country); 

CREATE INDEX actor_name on actor(ac_name); 

create index wa_ac_code on who_acted(ac_code);

create index genre_idx on genres(genre);

create index wg_grade_idx on what_grade(grade);