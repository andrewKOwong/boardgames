import lxml.etree as etree
from pathlib import Path


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

    def extract_id(self) -> int:
        """Return boardgame id."""
        try:
            return int(self.item.attrib['id'])
        except KeyError:
            raise KeyError("Missing id attribute.")

    def extract_name(self) -> str:
        """Return boardgame name."""
        element = self.item.find("name")
        if element is None:
            raise TypeError("Missing tag 'name'.")
        return element.attrib['value']

    def extract_year_published(self) -> int:
        """Return boardgame year published."""
        element = self.item.find("yearpublished")
        if element is None:
            raise TypeError("Missing tag 'yearpublished'.")
        return int(element.attrib['value'])

    def extract_n_ratings(self) -> int:
        """Return number of ratings."""
        out = self.item.find("statistics")\
                       .find("ratings")\
                       .find("usersrated")\
                       .attrib['value']
        return int(out)

    def extract_ratings_mean(self) -> float:
        """Return mean average rating to 3 decimals."""
        out = self.item.find("statistics")\
                       .find("ratings")\
                       .find("average")\
                       .attrib['value']
        return round(float(out), 3)

    def extract_ratings_stddev(self) -> float:
        """Return rating standard deviation to 4 decimals."""
        out = self.item.find("statistics")\
                       .find("ratings")\
                       .find("stddev")\
                       .attrib['value']
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
