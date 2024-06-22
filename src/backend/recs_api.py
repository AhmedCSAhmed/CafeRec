# The backend of the CafeRecs application is implemented  using FastAPI, and follows REST design principles. 
# The main resource abstraction the server handles is Cafes, containing the name of a cafe, it's address, 
# and some keywords from it's top Google reviews representing its "vibe". This API encapsulates the overall 
# logic of the server in returning a list of Cafes to clients upon request.

from fastapi import FastAPI
import sqlalchemy
from sqlalchemy import *
import requests as requests
import hashlib as hashlib
import struct
app = FastAPI()
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut

# The schema for the database storing cafe data is defined by this simple Cafe class,
# where each cafe has a unique ID, a name, a zipcode location, a 0-5 star review, and a
# Vibe it is associated with.
class Cafe:
    cafe_id: str
    cafe_name: str
    zipcode: int
    stars: int
    vibe: str

# A Vibe is a predefined "feeling" that a certain cafe is associated with, based on 
# the Google reviews it recieved. For example, a cafe that reviews describe as "calm, 
# good for study, and peaceful" would most strongly match to the QUIET vibe.
class Vibe(Enum):
    QUIET=1,
    SOCIAL=2,
    ETHNIC=3,
    TASTE=4,
    AESTHETIC=5

# Helper function to convert the user's ZIP code to 
# their corresponding latitude and longitude coordinates.
# Used to conform with the Google Places API request format.
# Returns a tuple mapping the tuple of latitude and longitude to the zipcode.
def zip_to_coord(zip: int) -> tuple[tuple[float, float], int] | None:
    try:
        geolocator = Nominatim(user_agent="CafeApp")
        location = geolocator.geocode({"postalcode": str(zip), "country": "USA"})
        
        if location:
            return ((location.latitude, location.longitude), zip)
        else:
            print("Location not found.")
            return None
        
    except GeocoderTimedOut:
        print("Geocoding Timed Out")
        return None
    
    except GeocoderServiceError:
        print("Service Error")
        return None
        
# Given the exact latitude and longitude, return a unique Cafe ID string via hashing. 
# Example: Caribou Cafe's location maps to "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
def uniqueID(lat: float, long: float) -> str:
    # initialize hash function
    hash = hashlib.sha256()

    # generate hash function seed from location data
    location_buffer = struct.pack(str(lat + long))

    # perform hashing
    hash.update(location_buffer)
    key = hash.hexdigest()
    return key 

# Script to setup the database using SQLite (in memory for now)

# Create database engine and table schema
engine = sqlalchemy.create_engine("sqlite:///:memory:")
connection = engine.connect()
metadata = sqlalchemy.MetaData()
CafeTable = sqlalchemy.Table(
    "cafe",
    metadata,
    Column("cafe_id", String, primary_key=True),  # primary key for unique identifiers
    Column("cafe_name", String, nullable=False),
    Column("zipcode", Integer, nullable=False),  # zipcode of the cafe
    Column("stars", Integer, nullable=False),  
    Column("vibe", Vibe, nullable=False) # vibe that the cafe matches strongest to
)

metadata.create_all(engine)

# test database by inserting the made-up Caribou Coffee cafe
with engine.connect() as conn:
    ins = CafeTable.insert().values(
        cafe_name="Caribou Coffee",
        zipcode=12345,
        stars=5,
        vibe=Vibe.AESTHETIC
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

