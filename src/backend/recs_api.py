# The backend of the CafeRecs application is implemented  using FastAPI, and follows REST design principles. 
# The main resource abstraction the server handles is Cafes, containing the name of a cafe, it's address, 
# and some keywords from it's top Google reviews representing its "vibe". This API encapsulates the overall 
# logic of the server in returning a list of Cafes to clients upon request.

from fastapi import FastAPI
from pydantic import BaseModel
import requests as requests
import hashlib as hashlib
import struct
from enum import Enum

import sqlalchemy
from sqlalchemy import *

app = FastAPI()
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut

# The schema for the database storing cafe data is defined by this simple Cafe class,
# where each cafe has a unique ID, a name, a zipcode location, a 0-5 star review, and a
# Vibe it is associated with.


# A Vibe is a predefined "feeling" that a certain cafe is associated with, based on 
# the Google reviews it recieved. For example, a cafe that reviews describe as "calm, 
# good for study, and peaceful" would most strongly match to the QUIET vibe.
class Vibe(Enum):
    QUIET=1
    SOCIAL=2
    ETHNIC=3
    TASTE=4
    AESTHETIC=5


class Cafe(BaseModel):
    cafe_id: str
    cafe_name: str
    zipcode: str
    stars: int
    vibe: int
    



    
    
"""
Given a zipcode, return the latitude and longitude coordinates of that location.
If the location is not found, return None.
Example: zip_to_coord("55414") -> ((44.98, -93.24), 55414)
 
"""

def zip_to_coord(zipcode: str) -> tuple[tuple[float, float], int] | None:
    zipcode = int(zipcode) # Convert to integer for geopy
    try:
        geolocator = Nominatim(user_agent="CafeApp") # Initialize geolocator
        location = geolocator.geocode({"postalcode": str(zipcode), "country": "USA"}) # Get location from zipcode
        
        if location: # If location is found, return the latitude, longitude, and zipcode
            return ((location.latitude, location.longitude), str(zipcode)) 
        
        else: # If location is not found, return None
            print("Location not found.") 
            return None
        
    except GeocoderTimedOut: # If geocoding times out, return None
        print("Geocoding Timed Out")
        return None
    
    except GeocoderServiceError: # If geocoding service error, return None
        print("Service Error")
        return None
        
""" 
Given a latitude and longitude, return a unique identifier for that location.
The unique identifier is a hash of the latitude and longitude.
Example: uniqueID(44.98, -93.24) -> "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
"""
def uniqueID(lat: float, long: float) -> str: 
    # initialize hash function
    hash = hashlib.sha256()
    # pack the latitude and longitude into a byte string
    locatioBuffer = str(lat+long)
    encoded_str = locatioBuffer.encode('utf-8')
    hashObj = hashlib.sha256(encoded_str)
    return hashObj.hexdigest()

    
    
    
"""
    This function creates a database table for cafes, with columns for the cafe_id, cafe_name, zipcode, stars, and vibe.
    The cafe_id is a unique identifier for each cafe, and is a hash of the cafe's location.
    The cafe_name is the name of the cafe.
    The zipcode is the location of the cafe.
    The stars is the rating of the cafe.
    The vibe is the vibe that the cafe matches strongest to.
    The function creates the table in memory.
"""
def MakeDB():
    
    # we will need to move the database to it's own file later
    engine = sqlalchemy.create_engine("sqlite:///:memory:")
    if not engine:
        raise Exception("Could not create engine")
    engine.connect()
    metadata = sqlalchemy.MetaData()
    CafeTable = sqlalchemy.Table(
        "cafe",
        metadata,
        Column("cafe_id", String, primary_key=True),  # primary key for unique identifiers
        Column("cafe_name", String, nullable=False),
        Column("zipcode", Integer, nullable=False),  # zipcode of the cafe
        Column("stars", Integer, nullable=False),  
        Column("vibe", Integer, nullable=False) # vibe that the cafe matches strongest to
    )
     

    metadata.create_all(engine)
    return engine, CafeTable

try:
    engine, CafeTable = MakeDB()
    print("Database created successfully")
except RuntimeError as e:
    print(f"Error creating database: {e}")

"""
This function takes in a Cafe object and inserts it into the database.
The Cafe object is a representation of a cafe with a name, zipcode, star rating, and vibe.
The function inserts the cafe into the database table, with the cafe_id being a unique hash of the cafe's location.
"""
def putEntriesToDB(entry:Cafe) -> None:
    latLong, zipCode = zip_to_coord(entry.zipcode)
    uqID = uniqueID(latLong[0],latLong[1])
    if latLong is None:
        return False
    
    newCafe = CafeTable.insert().values(
        cafe_id = uqID,
        cafe_name = entry.cafe_name,
        zipcode = entry.zipcode,
        stars = entry.stars,
        vibe = entry.vibe
    )
    with engine.connect() as conn:
        conn.execute(newCafe)
    return True

        

# test database by inserting the made-up Caribou Coffee cafe
with engine.connect() as conn:
    ins = CafeTable.insert().values(
        cafe_name="Caribou Coffee",
        zipcode=12345,
        stars=5,
        vibe=Vibe.SOCIAL
    )

# API HTTP methods to interact with the server

# Entry method to server, use to start application
@app.get("/")
def read_root():
    pass
    

# Retrieve the top Cafes matching the requested vibe keywords 
@app.get("/cafes")
def get_cafes(num: str, zip_code: int, vibe_words: list[str], address: str | None = None):
    # TODO: Implement, likely using other python files for modularity
    pass




cafe = Cafe(cafe_id="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", cafe_name="Caribou Coffee", zipcode="12345", stars=5, vibe=Vibe.ETHNIC)
putEntriesToDB(cafe)
print("Cafe added to database")

def printCafe(cafe):
    print("Cafe ID:", cafe.cafe_id)
    print("Cafe Name:", cafe.cafe_name)
    print("Zipcode:", cafe.zipcode)
    print("Stars:", cafe.stars)
    print("Vibe:", cafe.vibe)
    print()  # Add a newline for better readability between entries
printCafe(cafe)