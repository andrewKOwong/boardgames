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

    def extract_id(self):
        try:
            return int(self.item.attrib['id'])
        except KeyError:
            raise KeyError("Missing id attribute.")

    def extract_year_published(self):
        element = self.item.find("yearpublished")
        if element is None:
            raise TypeError("Missing tag 'yearpublished'.")
        return int(element.attrib['value'])
