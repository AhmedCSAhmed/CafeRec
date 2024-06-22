# The backend of the CafeRecs application is implemented  using FastAPI, and follows REST design principles. 
# The main resource abstraction the server handles is Cafes, containing the name of a cafe, it's address, 
# and some keywords from it's top Google reviews representing its "vibe". This API encapsulates the overall 
# logic of the server in returning a list of Cafes to clients upon request.

from fastapi import FastAPI
import sqlalchemy as sa
from sqlalchemy import *
import requests as re
import hashlib as hs
app = FastAPI()
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut







# Create a Nominatim object

"""
Converts the user's ZIP code to 
their corresponding latitude and longitude coordinates.
"""

def zip_Converter(zipCode:int):
    try:
        geolocator = Nominatim(user_agent="CafeApp")
        location = geolocator.geocode({"postalcode": str(zipCode), "country": "USA"})
        
        if location: # if 
            return [(location.latitude, location.longitude), zipCode]
        else:
            print("Location not found.")
            return None
    except GeocoderTimedOut:
        print("Geocoding Timed Out")
        return None
    except GeocoderServiceError:
        print("Service Error")
        return None
        
 
print(zip_Converter(55124))



"""
Given the exact Lat and Longitude 
return a Unique Cafe ID 
Caribou Cafe --> "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
"""
def uniqueID(lat:float, long:float):
    h = hs.sha256()
    loc = lat + long
    h.update(loc)
    key = h.hexdigest()
    return key 


    

# Print the coordinates
# print(location.latitude, location.longitude) 




# Cafe informatio

class Cafe:
    cafe_id: int # Key make unique hashFucntion
    cafe_name: str
    zipcode: int
    stars: int
    vibe: str
    
    
class Vibe(Enum):
    QUIET=1,
    SOCIAL=2,
    ETHNIC=3,
    TASTE=4,

    
    

'''
Setting up the DB as an in-memory database using sqlite

1. Create the in memory table -->  check
2. Set up the connection to that in-memory database 
'''
engine = sa.create_engine("sqlite:///:memory:")
connection = engine.connect()
metadata = sa.MetaData()
CafeTable = sa.Table(
    "cafe",
    metadata,
    Column("cafe_id", Integer, primary_key=True),  # Primary key for unique identifiers
    Column("cafe_name", String, nullable=False),
    Column("zipcode", Integer, nullable=False),  # Zipcode of the cafe
    Column("stars", Integer, nullable=False),  
    Column("reviews", String, nullable=False) # Number of reviews
)  # the database that wills store Probs will need to put it into a new file

metadata.create_all(engine)

with engine.connect() as conn:
    ins = CafeTable.insert().values(
        cafe_name="Caribou Coffee",
        zipcode=12345,
        stars=5,
        reviews="Great coffee, friendly staff, and a nice place to study."
    ) # sample data that we play around with 


        

# Entry method to server, use to start application
@app.get("/")
def read_root():
    pass
    

# Retrieve the top Cafes matching the requested vibe keywords 
@app.get("/cafes")
def get_cafes(num: str, zip_code: int, vibe_words: list[str], address: str | None = None):
    # TODO: Implement, likely using other python files for modularity
    pass

