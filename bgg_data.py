import requests
import time
import os
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
    print(f"Request took {round(t2-t1,4)} seconds.")
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


def sample_random_ids_by_chunk(dir_path: str,
                               file_prefix: str = 'sample_',
                               file_suffix: str = '.xml',
                               k: int = 10,
                               chunk_size: int = 1,
                               max_id: int = 362383,
                               cooldown_time: int = 300,
                               raise_if_fail: bool = True,
                               random_state: int = None,
                               **kwargs) -> None:
    """Sample random boardgame ids in chunks and retrieve the data.

    Best used for collecting large number of ids.

    Parameters
    ----------
    dir_path : str
        Output folder for xml output files.
    file_prefix : str, optional
        Output file prefix, by default 'sample_'
    file_suffix : str, optional
        Output file suffix, by default '.xml'
    k : int, optional
        Number of total samples, by default 10.
    chunk_size : int, optional
        Number of ids per server request, by default 1.
        Inadvisable to do very large chunks due to server penalties.
        Probably max ~1000.
    max_id : int, optional
        The approximate highest used id on BGG.
        By default 362383.
    cooldown_time : int, optional
        Time (in seconds) to wait between requests.
        By default 300.
    raise_if_fail : bool, optional
        By default True.
        Will raise an error via response.raise_for_status().
    random_state : int, optional
        _description_, by default None

    Returns
    -------
    None


    Raises
    ------
    FileNotFoundError
        The output directory doesn't exist.
    FileNotFoundError
        The output directory isn't a directory.
    HTTPError
        If raise_if_fail == True, if the response
        status isn't 200, an error will be raised.
        This is prevents continual requests if 
        the server has started denying the requests.
    """
    # Add ending directory slash if not exists
    if dir_path[-1] != '/':
        dir_path += '/'

    # Check directory is ok.
    if not os.path.exists(dir_path):
        raise FileNotFoundError(
            f"'{dir_path}' does not exist. "
            f"Please create it first.")
    if not os.path.isdir(dir_path):
        raise FileNotFoundError(
            f"'{dir_path}' is not a directory. "
            f"Please provide another folder path."
        )

    # Timing
    t_1 = time.time()

    # Generate list of random ids and break into chunks
    random.seed(random_state)
    ids = random.sample(range(1, max_id+1), k)
    ids = [ids[i:i + chunk_size]
           for i in range(0, len(ids), chunk_size)]
    # Each chunk of ids get a uri, get the response,
    # raise if something goes wrong (e.g. blocked by server),
    # and a file written for that chunk.
    # Then a cooldown to not hammer the server.
    total_chunks = len(ids)
    for i, ids_chunk in enumerate(ids):
        print("---")
        print(f"Request {i+1} of {total_chunks}")
        uri = generate_game_uri(ids_chunk, **kwargs)
        response = retrieve_bgg_data(uri)
        if raise_if_fail:
            response.raise_for_status()
        write_response(response,
                       f"{dir_path}"
                       f"{file_prefix}{i+1}{file_suffix}")
        print(f"Elapsed time: {round((time.time() - t_1)/60)} minutes.")
        time.sleep(cooldown_time)

    # Total elapsed time
    t_2 = time.time()
    print(f"Total time elapsed: {round((t_2 - t_1)/60)} seconds.")


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
