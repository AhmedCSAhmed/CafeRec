# The backend of the CafeRecs application is implemented  using FastAPI, and follows REST design principles. 
# The main resource abstraction the server handles is Cafes, containing the name of a cafe, it's address, 
# and some keywords from it's top Google reviews representing its "vibe". This API encapsulates the overall 
# logic of the server in returning a list of Cafes to clients upon request.

from fastapi import FastAPI

app: FastAPI = FastAPI()

# Cafe information
class Cafe:
    name: str
    address: str
    zip_code: int
    vibe_keywords: list[str]

# Entry method to server, use to start application
@app.get("/")
def read_root():
    ## TODO: Implement
    return

# Retrieve the top Cafes matching the requested vibe keywords 
@app.get("/cafes")
def get_cafes(num: str, zip_code: int, vibe_words: list[str], address: str | None = None):
    # TODO: Implement, likely using other python files for modularity
    return

