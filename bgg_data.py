import requests
import time
import random
import xml.etree.ElementTree as ET


def generate_game_uri(ids=[], filter_basegame=True, filter_expansion=False, stats=True):
    """Construct a URI to get one or more games based on their id.

    Parameters
    ----------
    ids : list, optional
        list of numerical ids of the board games, by default []
    filter_basegame : boolean, optional
        filter for base board games, by default True.
    filter_expansion : boolean, optional
        filter for board game expansions, by default False.
    stats : boolean, optional
        include statistics i.e. "stats=1" in the query.

    Returns
    -------
    str URI
        URI accessing board games with specified ids.
    """

    # Board Game Geek XML API2 endpoint for retrieving "thing" objects
    BASE_API_ENDPOINT = "https://boardgamegeek.com/xmlapi2/thing?"
    # Thing types
    # Non-expansion games
    BASE_GAME_TYPE = "boardgame"
    # Expansions
    EXPANSION_TYPE = "boardgameexpansion"

    # Set up the output
    uri = BASE_API_ENDPOINT

    # Add type filters
    uri += "type="
    if filter_basegame:
        uri += BASE_GAME_TYPE + ','
    if filter_expansion:
        uri += EXPANSION_TYPE + ','
    uri += '&'

    # Add stats query
    if stats:
        uri += "stats=1&"

    # Add ids
    uri += "id="
    # i.e. [1,2] -> '1,2'
    uri += ','.join([str(i) for i in ids])

    return uri


def retrieve_bgg_data(uri):
    """Make a request for board game geek data

    Parameters
    ----------
    uri : str
        String URI for accessing the API.

    Returns
    -------
    Response object
        The resulting response from the HTTP request.
    """
    t1 = time.time()
    r = requests.get(uri)
    t2 = time.time()
    print(f"Request took {t2-t1} seconds ({(t2-t1)/60} minutes).")
    return r


def sample_random_ids(k=100, max_id=362383, random_state=None, **kwargs):
    """Sample random boardgame ids and retrieve the data.

    Parameters
    ----------
    k : int, optional
        Number of samples, by default 100.
        Inadvisable to do large queries due to server penalties.
        Probably max ~1000.
    max_id : int, optional
        The approximate highest used id on BGG.
        By default 362383.
    random_state : int, optional
        By default None. Set an int for reproducibility.
    **kwargs
        Remaining kwargs are fed into generate_game_uri.
        Use e.g. filter_basegame = False.

    Returns
    -------
    A Response object.
    """
    # Generate list of random ids
    random.seed(random_state)
    ids = random.sample(range(1, max_id+1), k)
    # Generate a URI
    uri = generate_game_uri(ids, **kwargs)
    # Make the request and return the Response
    return retrieve_bgg_data(uri)


def write_response(response, out_path):
    """Write the content of a response to a file.

    Parameters
    ----------
    response : Response object
    out_path : str
        File path to write to.
    """
    with open(out_path, 'wb') as f:
        f.write(response.content)


def count_items(response):
    """Counts the number of items in a requested XML.

    Assumes that the number of items is
    the number of child elements, as it counts the
    len(root_element).

    Parameters
    ----------
    response : requests.Response

    Returns
    -------
    int
        Count of the length of the root XML element.
        This should correspond to the number of 
        items (e.g. boardgames).
    """
    root = ET.fromstring(response.text)
    return len(root)
