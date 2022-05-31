import lxml.etree as etree
from pathlib import Path
from IPython.core.display import display, HTML


def read_xml_file(file_path: str) -> etree.Element:
    """Read an xml file using lxml and get the root element.

    Parameters
    ----------
    file_path : str
        Location of the xml file.

    Returns
    -------
    etree.Element
        The root element of the xml file.
    """
    # Read xml data
    # etree raises error for read_text
    xml_data = Path(file_path).read_bytes()
    # return root element
    return etree.fromstring(xml_data)


class Extractor():
    """
    Handles extracting various XML attributes and values
    in a bespoke manner for each value from BGG data.
    """

    def __init__(self, item):
        """Initalize with an item (i.e. a boardgame).

        Parameters
        ----------
        item : lxml.etree Element
            An element tagged item, corresponding to a board game entry.
        """
        self.item = item

    def extract_id(self):
        try:
            return int(self.item.attrib['id'])
        except KeyError:
            raise KeyError("Missing id attribute.")

    def extract_name(self):
        element = self.item.find("name")
        if element is None:
            raise TypeError("Missing tag 'name'.")
        return element.attrib['value']

    def extract_year_published(self):
        element = self.item.find("yearpublished")
        if element is None:
            raise TypeError("Missing tag 'yearpublished'.")
        return int(element.attrib['value'])

    def extract_n_ratings(self):
        "Return number of ratings."
        out = self.item.find("statistics")\
                       .find("ratings")\
                       .find("usersrated")\
                       .attrib['value']
        return int(out)

    def extract_ratings_mean(self):
        """Return mean average rating to 3 decimals."""
        out = self.item.find("statistics")\
                       .find("ratings")\
                       .find("average")\
                       .attrib['value']
        return round(float(out), 3)

    def extract_ratings_stddev(self):
        """Return rating standard deviation to 4 decimals."""
        out = self.item.find("statistics")\
                       .find("ratings")\
                       .find("stddev")\
                       .attrib['value']
        # Banker's rounding (round half to even)
        return round(float(out), 4)


def extract_xml(file_path: str,
                id: bool = True,
                year_published: bool = False) -> dict:
    # Initialize empty lists for each data type of interest
    out = {}
    if id:
        out['id'] = []
    if year_published:
        out['year_published'] = []

    # Get the root <items> item for an xml file
    root = read_xml_file(file_path)
    # Load up data from each item
    for item in root:
        e = Extractor(item)
        if id:
            out['id'].append(e.extract_id())
        if year_published:
            out['year_published'].append(e.extract_year_published())

    return out


def display_id_link(id: int) -> None:
    """Display a clickable link in a Jupyter notebook to a boardgame with stated id.

    Parameters
    ----------
    id : int
        The game id of interest.
    """
    BASE_URL = "https://boardgamegeek.com/boardgame/"
    display(HTML(f"<a href={BASE_URL + str(id)}>ID: {id}</a>"))
