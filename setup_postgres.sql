CREATE TABLE student_areas (
	id integer,
	poly_id integer);
SELECT AddGeometryColumn('student_areas','geom',4326,'POLYGON',2);
SELECT AddGeometryColumn('student_areas','bbox',4326,'POLYGON',2);

CREATE TABLE instagram_locations (
	id int,
	name varchar,
	lat float,
	lng float);
SELECT AddGeometryColumn('instagram_locations','geom',4326,'POINT',2);

CREATE OR REPLACE FUNCTION makegrid(geometry, integer)
RETURNS SETOF x float, y float AS
'SELECT ST_X(ST_Transform(ST_SetSRID(ST_MakePoint(x,y),3786),4326)), ST_Y(ST_Transform(ST_SetSRID(ST_MakePoint(x,y),3786),4326))FROM 
generate_series(floor(st_xmin(ST_Transform($1,3786)))::int, ceiling(st_xmax(ST_Transform($1,3786)))::int, $2) as x
,generate_series(floor(st_ymin(ST_Transform($1,3786)))::int, ceiling(st_ymax(ST_Transform($1,3786)))::int,$2) as y 
where st_intersects(ST_Transform($1,3786),ST_SetSRID(ST_POINT(x,y),3786))
'
LANGUAGE sql

CREATE OR REPLACE FUNCTION makegrid_visual(geometry, integer)
RETURNS geometry AS
'SELECT ST_Collect(ST_Transform(ST_SetSRID(ST_MakePoint(x,y),3786),4326)) FROM 
generate_series(floor(st_xmin(ST_Transform($1,3786)))::int, ceiling(st_xmax(ST_Transform($1,3786)))::int, $2) as x
,generate_series(floor(st_ymin(ST_Transform($1,3786)))::int, ceiling(st_ymax(ST_Transform($1,3786)))::int,$2) as y 
where st_intersects(ST_Transform($1,3786),ST_SetSRID(ST_POINT(x,y),3786))
'
LANGUAGE sql