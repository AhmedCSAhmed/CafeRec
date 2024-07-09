# The backend of the CafeRecs application is implemented  using FastAPI, and follows REST design principles.
# The main resource abstraction the server handles is Cafes, containing the name of a cafe, it's address,
# and some keywords from it's top Google reviews representing its "vibe". This API encapsulates the overall
# logic of the server in returning a list of Cafes to clients upon request.

import hashlib
import struct
from enum import Enum

import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel
import requests as requests
import hashlib as hashlib
import struct
from enum import Enum

import sqlalchemy
from sqlalchemy import Column, Integer, String, desc

app = FastAPI()
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut

class Cafe(BaseModel):
    """
    The schema for the database storing cafe data is defined by this simple Cafe class,
    where each cafe has a unique ID, a name, a zipcode location, a 0-5 star review, and a
    Vibe it is associated with.
    """

    cafe_id: str
    cafe_name: str
    zipcode: int
    stars: int
    vibe: str


class Vibe(Enum):
    """
    A Vibe is a predefined "feeling" that a certain cafe is associated with, based on
    the Google reviews it recieved. For example, a cafe that reviews describe as "calm,
    good for study, and peaceful" would most strongly match to the QUIET vibe.
    """

    QUIET = 1
    SOCIAL = 2
    ETHNIC = 3
    TASTE = 4
    AESTHETIC = 5


def zip_to_coord(zipcode: int) -> tuple[float, float] | None:
    """
    Given a ZIP code, return the corresponding latitude and longitude coordinates.
    Used to conform with the Google Places API request format. Assumes USA only.
    Returns a tuple mapping the tuple of latitude and longitude to the zipcode.
    """
    try:
        geolocator = Nominatim(user_agent="CafeApp")
        location = geolocator.geocode({"postalcode": str(zipcode), "country": "USA"})

        if location:
            return (location.latitude, location.longitude)
        else:
            print("Location not found.")
            return None

    except GeocoderTimedOut:
        print("Geocoding Timed Out")
        return None

    except GeocoderServiceError:
        print("Geocoder Service Error")
        return None
        
# Given the exact latitude and longitude, return a unique Cafe ID string via hashing. 
# Example: Caribou Cafe's location maps to "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
def uniqueID(lat: float, long: float) -> str:

    # generate hash function seed from location data
    location_buffer = str(lat + long)
    encoded_str = location_buffer.encode("utf-8")
    # perform hashing
    hash = hashlib.sha256()
    key = hash.hexdigest()
    return key 


def MakeDB():
    """
    This function creates a database table for cafes, with columns for the cafe_id, cafe_name, zipcode, stars, and vibe.
    cafe_id: a unique identifier for each cafe, created by hashing it's location
    cafe_name: name of the cafe
    zipcode: zipcode location of the cafe
    stars: Google Reviews rating of the cafe
    vibe: the Vibe enum that the cafe matches strongest to
    
    This function creates the table in memory for now.
    """

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

# Create the database
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
    coordinates = zip_to_coord(entry.zipcode)
    if coordinates is None:
        # Error, handle here
        raise Exception("unable to convert to coordinates")
    
    latitude, longitude = coordinates

    uqID = uniqueID(latitude, longitude)
    
    newCafe = CafeTable.insert().values(
        cafe_id = uqID,
        cafe_name = entry.cafe_name,
        zipcode = entry.zipcode,
        stars = entry.stars,
        vibe = entry.vibe
    )
    with engine.connect() as conn:
        conn.execute(newCafe)

        

# test database by inserting the made-up Caribou Coffee cafe
with engine.connect() as conn:
    ins = CafeTable.insert().values(
        cafe_name="Caribou Coffee",
        zipcode=12345,
        stars=5,
        vibe=Vibe.SOCIAL
    )
    conn.execute(ins)




def get_top_five_cafes(zip : int, vibe : Vibe):
    '''
    Given a location and specific vibe, return the 5 highest rated coffee spots that match that vibe and locoation
    Returns 5 Coffee spots from the database
    '''
    #Gets the 5 highest rated coffee spots from the database, checks for same vibe and location
    query = CafeTable.select().where(
        CafeTable.c.zipcode == zip, CafeTable.c.vibe == vibe).order_by(desc(
            CafeTable.c.stars)).limit(5) #gives a limit of 5
    
    with engine.connect() as conn:
        result = conn.execute(query)
    
    return result.fetchall() # return top 5 

# FastAPI Server definition
app = FastAPI()

# Entry method to server, use to start application


@app.get("/")
def read_root():
    pass


#Retrieve the top Cafes matching the requested vibe keywords
@app.get("/cafes")
def get_cafes(num: str, zip_code: int, vibes: list[Vibe]):
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