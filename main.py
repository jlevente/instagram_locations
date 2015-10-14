import params
from data_collector import insta_stuff
import os

if __name__ == "__main__":
    insta = insta_stuff()
    # Upload student polygons from a folder (assumed kmls are named as "student_id.kml" (e.g. 1.kml)
    #for kml in os.listdir(path):
    #    insta.upload_student_areas(path, kml)
    
    # Get all Instagram Locations for uploaded polygons:
    # Secify radius for search parameter (~ 1000 seems to be reasonably fast)
    #insta.get_locations(1000)
    
