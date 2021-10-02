
--Δημιουργία του πίνακα των σκαφών.
create table Vessels(
	mmsi int not null unique,
	imo int,
	name varchar(24),
	flag varchar(17),
	type varchar(37),
	primary key(mmsi)
);

--Εισαγωγή των δεδομένων στον πίνακα.
copy Vessels from 'C:\Users\stefa\Desktop\GIS DATA\static_ais_vessel_id.csv' DELIMITER ';' CSV HEADER;
copy Vessels from 'C:\Users\stefa\Desktop\GIS DATA\final_dataset.csv' DELIMITER ';' CSV HEADER;
select * from Vessels

--Δημιουργία του πίνακα κινηματικών δεδομένων
create table Unipi_Kinematic_AIS(
	ts double precision,	
	type integer,            
	mmsi integer,           
	status integer,          	
	lon double precision,  
	lat double precision, 	
	heading integer,      		
	turn double precision,  
	speed double precision, 	
	course 	double precision,
	foreign key (mmsi) references Vessels(mmsi)
);

--Εισαγωγή δεδομένων στον πίνακα
copy Unipi_Kinematic_AIS from 'C:\Users\stefa\Desktop\GIS DATA\unipi_kinematic_AIS_jun2018.csv' DELIMITER ';' CSV HEADER;
copy Unipi_Kinematic_AIS from 'C:\Users\stefa\Desktop\GIS DATA\unipi_kinematic_AIS_jul2018.csv' DELIMITER ';' CSV HEADER;
select * from Unipi_Kinematic_AIS

--Δημιουργία στηλών γεωμετρία στους πίνακες
ALTER TABLE Unipi_Kinematic_AIS ADD COLUMN geom geometry(Point, 4326);
UPDATE Unipi_Kinematic_AIS SET geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326);

ALTER TABLE public."Ports" ADD COLUMN geom geometry(Point, 4326);
UPDATE public."Ports" SET geom = ST_SetSRID(ST_MakePoint(public."Ports".longitude, public."Ports".latitude), 4326);

--Εμφάνιση λιμανιών που βρίσκονται εντός Ελλάδας
SELECT * FROM public."Ports" where public."Ports".country = 'GR'
SELECT * FROM public."Fishing Ports" where public."Fishing Ports".country = 'Greece'
select * from public."Ports" where public."Ports".longitude = public."Fishing Ports".longitude;

--Καθαρισμός των πινάκων των λιμανιών από λιμάνια τα οποία δεν βρίσκονται στην Ελλάδα
SELECT      public."Ports".longitude,
            public."Ports".latitude ,
			public."Ports".country
FROM        public."Ports" 
INNER JOIN  public."Fishing Ports" o ON public."Ports".longitude = o.id
INNER JOIN  public."Fishing Ports" d ON public."Ports".longitude = d.id

--Διαγραφή λιμανιών που δεν βρίσκονται εντός Ελλάδας από τους πίνακες.
DELETE FROM Public."Ports"
WHERE public."Ports".country != 'GR';

DELETE FROM Public."Fishing Ports"
WHERE public."Fishing Ports".country != 'Greece';


--Διαγραφή θορύβου στον πίνακα κινηματικών δεδομένων
--Διαγραφή στιγμάτων εκτός εμβέλειας AIS κεραίας
DELETE FROM Unipi_Kinematic_AIS
WHERE ST_CONTAINS(ST_GEOMFROMTEXT('polygon((23.580 37.365, 23.312 37.511,
23.100 37.617, 23.078 37.778, 22.976 37.836, 22.983 37.930, 23.298 38.007, 23.590 38.064,
24.183 37.531, 23.580 37.365))',4326),geom)=false;


--Δημιουργία ενός νέου προσωρινού table Unipi_Kinematic_AIS_2 όπου θα γίνει ο καθαρισμός
create table Unipi_Kinematic_AIS_2(
	ts double precision,	
	type integer,            
	mmsi integer,           
	status integer,          	
	lon double precision,  
	lat double precision, 	
	heading double precision,      		
	turn double precision,  
	speed double precision, 	
	course 	double precision,
	velocity double precision,
	bearing double precision,
	acceleration double precision,
	distance_from_prev double precision,
	time_from_prev double precision
);

copy Unipi_Kinematic_AIS_2 from 'G:\GIS\cleaned_data4.000' DELIMITER ',' CSV HEADER;
copy Unipi_Kinematic_AIS_2 from 'G:\GIS\cleaned_data4.001' DELIMITER ',' CSV HEADER;
copy Unipi_Kinematic_AIS_2 from 'G:\GIS\cleaned_data4.002' DELIMITER ',' CSV HEADER;

ALTER TABLE Unipi_Kinematic_AIS_2 ADD COLUMN geom geometry(Point, 4326);
UPDATE Unipi_Kinematic_AIS_2 SET geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326);

--Καθαρισμός στιγμάτων όπου η υπολογισμένη ταχύτητα velocity ξεπερνάει το threshold
DELETE FROM Unipi_Kinematic_AIS_2 where velocity > 40
--Διαγραφή θορύβου / ακραίων ταχυτήτων
DELETE FROM Unipi_Kinematic_AIS_2 where distance_from_prev > (40 * 0.514444 * time_from_prev);

--Επαναδημιουργία του αρχικού πίνακα Unipi_Kinematic_AIS με τα καθαρισμένα δεδομένα
ALTER TABLE Unipi_Kinematic_AIS_2 
   ALTER COLUMN heading TYPE integer;
CREATE TABLE Unipi_Kinematic_AIS AS
SELECT ts,type,mmsi,status,lon,lat,heading,turn,speed,course FROM Unipi_Kinematic_AIS_2;
SELECT * FROM Unipi_Kinematic_AIS
ALTER TABLE Unipi_Kinematic_AIS 
   ADD CONSTRAINT fk_mmsi
   FOREIGN KEY (mmsi) 
   REFERENCES Vessels(mmsi);
ALTER TABLE Unipi_Kinematic_AIS ADD COLUMN geom geometry(Point, 4326);
UPDATE Unipi_Kinematic_AIS SET geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326);

--Δημιουργία ευρετηρίων	
CREATE INDEX ship_pos_indx ON Unipi_Kinematic_AIS USING GIST (geom);
SET enable_seqscan=OFF;

--Ερωτήματα που χρησιμοποιούν το ευρετήριο
SELECT * 
FROM Unipi_Kinematic_AIS
WHERE ST_DWithin(geom::geometry, ST_SetSRID(ST_MakePoint(23.652610605175298::double precision, 37.94230905033819::double precision), 4326)::geometry, 5);

SELECT * 
FROM Unipi_Kinematic_AIS
  WHERE ST_Intersects(geom::geometry,ST_SetSRID(ST_MakePoint(23.652610605175298::double precision, 37.94230905033819::double precision), 4326)::geometry)

--Ερωτήματα που δεν χρησιμοποιούν το ευρετήριο
select * from Unipi_Kinematic_AIS where geom < ST_MakePoint(23.652610605175298::double precision, 37.94230905033819::double precision)
select * from Unipi_Kinematic_AIS where geom like ST_MakePoint(23.64922::double precision, 37.9464066666667::double precision)
SELECT * FROM Unipi_Kinematic_AIS WHERE geom BETWEEN ST_MakePoint(23.64922::double precision, 37.9464066666667::double precision) AND ST_MakePoint(23.6479566666667::double precision, 37.9316366666667::double precision);
SELECT *
FROM Unipi_Kinematic_AIS
WHERE ST_DistanceSphere(geom::geometry, ST_SetSRID(ST_MakePoint(23.6479566666667::double precision, 37.9316366666667::double precision), 4326)::geometry) <= 15 * 1609.34

--Ερώτημα 3.1 
--Πίνακας που περιέχει τα στίγματα του vessel με mmsi=240033700
create table Vessel_240033700(
	ts double precision,	  
	ts lon,
	ts lat,
	mmsi integer,           
	geom geometry,
	label integer
);

copy Vessel_240033700 from 'G:\GIS\vessel_240033700.csv' DELIMITER ';' CSV HEADER;
--Υπολογισμός της γραμμής των τροχιών του vessel 240033700 για κάθε τροχιά
SELECT label, ST_SetSRID(ST_MAKELINE (geom ORDER BY ts),4326) FROM Vessel_240033700 GROUP BY label;

--Εισαγωγή των trajectory που προέκυψαν από όλο το dataset
create table Vessel_Traj(
	ts double precision,
	mmsi integer,     
	lon double precision,
	lat double precision,      
	geom geometry,
	label integer
);

ALTER TABLE Vessel_Traj ADD COLUMN geom geometry(Point, 4326);
UPDATE Vessel_Traj SET geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326);

copy Vessel_Traj from 'G:\GIS\vessels_traj.000' DELIMITER ',' CSV HEADER;
copy Vessel_Traj from 'G:\GIS\vessels_traj.001' DELIMITER ',' CSV HEADER;
copy Vessel_Traj from 'G:\GIS\vessels_traj.002' DELIMITER ',' CSV HEADER;
--Υπολογισμός της γραμμής των τροχιών του dataset
SELECT label, ST_SetSRID(ST_MAKELINE (geom ORDER BY ts),4326) FROM Vessel_Traj GROUP BY label;

--Ερώτημα 3.2
--Query το οποίο ελέγχει πόσα trajectory ξεκινάνε από ένα λιμάνι και καταλήγουν σε ένα άλλο
--στο συγκεκριμένο ερώτημα ελέγχει από το λιμάνι του Περάματος στην Ελευσίνα
SELECT * 
FROM (SELECT * FROM ((SELECT DISTINCT ON (label)
       ts,mmsi,lon,lat,geom as geom_first,label
FROM   Vessel_Traj
ORDER  BY label, ts DESC, ts) table1
INNER JOIN
(SELECT DISTINCT ON (label)
       ts,mmsi,lon,lat,geom as geom_last,label
FROM   Vessel_Traj
ORDER  BY label, ts ASC, ts) table2 ON table1.label=table2.label) T1) T12
WHERE ST_DWithin(geom_first::geometry, ST_SetSRID(ST_MakePoint(23.566667::double precision, 37.966667::double precision), 4326)::geometry, 0.015) AND ST_DWithin(geom_last::geometry, ST_SetSRID(ST_MakePoint(23.55::double precision, 38.033333::double precision), 4326)::geometry, 0.015);

--Δημιουργία της γραμμής του trajectory με label 659268
SELECT label, ST_SetSRID(ST_MAKELINE (geom ORDER BY ts),4326) FROM Vessel_Traj where label=659268 GROUP BY label;

--Εύρεση των στιγμάτων πλοίων για μια συγκεκριμένη μέρα μετατρέπωντας το timestamp σε ημέρα.
SELECT * FROM
(SELECT mmsi, date_trunc('day', to_timestamp(ts::numeric/1000)) as date , lon , lat
FROM Vessel_traj ORDER BY  mmsi ASC, ts ASC) T1 WHERE T1.date = '2018-06-09 00:00:00+03';

--Εισαγωγή των δεδομένων μετά το temporal alignment σε νέο πίνακα
create table Vessel_Traj_Aligned(
	mmsi integer,     
	lat double precision,
	lon double precision,      
	label integer,
	ts double precision
);
copy Vessel_Traj_Aligned from 'G:\GIS\aligned_traj.csv' DELIMITER ',' CSV HEADER;
ALTER TABLE Vessel_Traj_Aligned ADD COLUMN geom geometry(Point, 4326);
UPDATE Vessel_Traj_Aligned SET geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326);
SELECT label, ST_SetSRID(ST_MAKELINE (geom ORDER BY ts),4326) FROM Vessel_Traj_Aligned GROUP BY label;
select * from  Vessel_Traj_Aligned ORDER BY LABEL




