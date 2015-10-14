import psycopg2
from datetime import datetime, timedelta
from instagram.client import InstagramAPI
from osgeo import ogr
from math import ceil, sqrt
import params

class insta_stuff(object):
    def __init__(self):
        # Connect to Instagram API
        self.api = InstagramAPI(access_token=params.access_token, client_secret=params.client_secret)
        
        # Init OGR driver
        self.drv = ogr.GetDriverByName('KML')
        
        # Connect to Postgres
        self.conn = psycopg2.connect(host=params.pg_host, port=params.pg_port, user=params.pg_user, password=params.pg_pass, dbname=params.pg_db)
        self.cursor = self.conn.cursor()
        self.conn2 = psycopg2.connect(host=params.pg_host, port=params.pg_port, user=params.pg_user, password=params.pg_pass, dbname=params.pg_db)
        self.cursor2 = self.conn2.cursor()
        self.conn3 = psycopg2.connect(host=params.pg_host, port=params.pg_port, user=params.pg_user, password=params.pg_pass, dbname=params.pg_db)
        self.upload_cursor = self.conn3.cursor()

    def test(self):
        user_id = 5006616
        recent_media, next_ = self.api.user_recent_media(user_id=user_id, count=10)
        for media in recent_media:
            print media.caption.text
    
    def upload_student_areas(self, path, kml):
        sql = 'INSERT INTO student_areas (id, poly_id, geom, bbox) VALUES (%s, %s, ST_SetSRID(ST_GeomFromText(%s),4326), ST_Envelope(ST_SetSRID(ST_GeomFromText(%s),4326)))'
        student_id = kml.split('.')[0]
        file = self.drv.Open(path + kml)
        for layer in file:
            for feature in layer:
                feature.geometry().FlattenTo2D()
                geom = feature.geometry().ExportToWkt()
                self.cursor.execute(sql, (str(student_id), str(i), geom, geom))
                self.conn.commit()

    # Generate a grid in PostgreSQL and calls Location/search API method for all grid points
    # If the response hits the limit, refines grid locally to get all Locations
    ### DEBUG duplicates due to overlaps in query circles!!!!
    def get_locations(self, radius):
        # Get a grid within a polygon to draw circles
        # GRID SPACING: x
        # radius: (sqrt(2) * x) / 2 -> no holes
        # Start with reasonably big radius, only decrease it when the response hits the limit
        
        spacing = int(radius * 2 / sqrt(2))
        
        # Generate grid to query Locations
        sql = 'SELECT makegrid(geom, %s) FROM student_areas'
        self.cursor.execute(sql, (spacing, ))
        
        for rec in self.cursor:
            tmp = eval(rec[0])
            lng, lat =tmp[0], tmp[1]
            # Query Locations on current grid point
            locations = self.api.location_search(lat=lat, lng=lng, distance=radius, count=100)
            print(len(locations))
            # If response hits the limit
            # Draw a circle with current radius on the current grid point and do a finer search
            if len(locations) == 33:
                print "FINER GRIDDD"
                self.get_finer(lat, lng, radius)
            else:
                self.upload_locations(locations)
    
    def get_finer(self, lat, lng, radius):
        sql = 'SELECT makegrid(ST_Buffer(ST_Transform(ST_SetSRID(ST_MakePoint(%s,%s),4326),3786),%s),%s)'
        self.cursor2.execute(sql, (lng, lat, radius, radius/2))
        for rec in self.cursor2:
            tmp = eval(rec[0])
            lng, lat = tmp[0], tmp[1]
            locations = self.api.location_search(lat=lat, lng=lng, distance=radius, count=100)
            # Recursively refine grid if neccessary
            if len(locations) == 33:
                self.get_finer(lat, lng, radius/2)
            else:
                self.upload_locations(locations)
        
    def upload_locations(self, locations):
        sql = 'INSERT INTO instagram_locations (id, name, lat, lng, geom) VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s),4326))'
        for loc in locations:
            self.upload_cursor.execute(sql, (loc.id, loc.name, loc.point.latitude, loc.point.longitude, loc.point.longitude, loc.point.latitude))
        self.conn3.commit()
