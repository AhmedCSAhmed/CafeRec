# The backend of the CafeRecs application is implemented  using FastAPI, and follows REST design principles.
# The main resource abstraction the server handles is Cafes, containing the name of a cafe, it's address,
# and some keywords from it's top Google reviews representing its "vibe". This API encapsulates the overall
# logic of the server in returning a list of Cafes to clients upon request.

import hashlib
import struct
from enum import Enum

import sqlalchemy
from fastapi import FastAPI
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim
from nltk.corpus import wordnet
from sqlalchemy import Column, Integer, String


class Cafe:
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

    QUIET = (1,)
    TALKATIVE = (2,)
    ETHNIC = (3,)
    TASTY = (4,)
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


def unique_id(lat: float, long: float) -> str:
    """
    Given the exact latitude and longitude, return a unique Cafe ID string via hashing.
    Returns the hash ID as a string.
    """
    # initialize hash function
    hash_func = hashlib.sha256()

    # generate hash function seed from location data
    location_buffer = struct.pack(str(lat + long))

    # perform hashing
    hash_func.update(location_buffer)
    key = hash_func.hexdigest()
    return key


def parse_vibes(reviews: list[str]) -> dict[Vibe, int]:
    """
    Given a list of review strings for a cafe, match the cafe to each Vibe and
    assign an integer score communicating how strongly the cafe matches to the Vibe.
    Higher scores mean stronger matches, and the minimum score is 0.
    """

    # Match vibes to the cafe by counting the synonyms of the vibe that appear in the reviews
    vibe_counts: dict[Vibe, int] = {}

    for vibe in Vibe:
        vibe_counts[vibe] = 0
        synonyms: list[str] = []

        for synset in wordnet.synsets(vibe.name):  # gather all adjective of the vibe
            for lemma in synset.lemmas():
                synonyms.append(lemma.name())

        # search for the synonyms' appearances in the reviews
        for review in reviews:
            for synonym in synonyms:
                vibe_counts[vibe] += review.count(synonym)

    return vibe_counts


# Script to setup the database using SQLite (in memory for now)

# Create database engine and table schema
engine = sqlalchemy.create_engine("sqlite:///:memory:")
connection = engine.connect()
metadata = sqlalchemy.MetaData()
CafeTable = sqlalchemy.Table(
    "cafe",
    metadata,
    # primary key for unique identifiers
    Column("cafe_id", String, primary_key=True),
    Column("cafe_name", String, nullable=False),
    Column("zipcode", Integer, nullable=False),  # zipcode of the cafe
    Column("stars", Integer, nullable=False),
    # vibe that the cafe matches strongest to
    Column("vibe", sqlalchemy.Enum, nullable=False),
)

metadata.create_all(engine)

# test database by inserting the made-up Caribou Coffee cafe
with engine.connect() as conn:
    ins = CafeTable.insert().values(
        cafe_name="Caribou Coffee", zipcode=12345, stars=5, vibe=Vibe.AESTHETIC
    )

# FastAPI Server definition
app = FastAPI()

# Entry method to server, use to start application


@app.get("/")
def read_root():
    pass


# Retrieve the top Cafes matching the requested vibe keywords
@app.get("/cafes")
def get_cafes(num: str, zip_code: int, vibes: list[Vibe]):
    # TODO: Implement, likely using other python files for modularity
    pass
