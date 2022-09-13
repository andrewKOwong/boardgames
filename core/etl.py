import lxml.etree as etree
from pathlib import Path
import pandas as pd
from html import unescape


def flatten_xml_folder_to_dataframe(dir_path: str) -> pd.DataFrame:
    # TODO Call `flatten_xmlfile_to_dataframe` in a loop basically
    pass


def flatten_xml_file_to_dataframe(
        file_path: str,
        id: bool = True,
        name: bool = True,
        year_published: bool = True,
        ratings_n: bool = True,
        ratings_mean: bool = True,
        ratings_stddev: bool = True,
        boardgame_designer: bool = True,
        boardgame_publisher: bool = True,
        ) -> pd.DataFrame:
    # TODO Essentially a loop to
    # 1) Read the xml file to get a list of items
    # 2) Run a loop so that for each item you feed it into an
    # ItemExtractor object, which various extraction options.
    # You then extract a small dataframe.
    # Include some sort of option to warn/raise of missing data, or return NA
    # if a child tag doesn't exist.
    # Concatenate the dataframes either during the loop (how to concantenate
    # to an empty df?) or after. Memory may or may not be a concern.
    # Return the final dataframe.

    root = _read_xml_file(file_path)
    for child in root:
        extractor = ItemExtractor(child)


    pass


def write_dataframe_to_csv(save_path: str) -> None:
    # Convenience func.
    pass


# TODO convenience func to handle the reading before extraction
def _read_xml_file(file_path: str) -> etree.Element:
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


class ItemExtractor():
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

    def extract_general_data(self, raise_missing_id=True) -> dict:
        out = {}
        out['id'] = self._extract_id(raise_missing_id=raise_missing_id)
        out['name'] = self._extract_name()
        out['description'] = self._extract_description()
        out['year_published'] = self._extract_year_published()
        return out

    def extract_poll_data(self) -> dict:
        pass

    def extract_link_data(self) -> list[dict]:
        """Extract all link tags for the item."""
        return [link.attrib for link in self.item.findall('link')]

    def _extract_id(self, raise_missing_id=True) -> int | None:
        """Return board game id

        Args:
            raise_missing_id (bool, optional): raises if the item has no id
                attrib. Otherwise, ignore it and return None. Defaults to True.

        Raises:
            KeyError: If 'id' is not found in the items attributes.

        Returns:
            int | None: id | None if ignoring missing ids
        """
        try:
            # Access the attrib dict
            return int(self.item.attrib['id'])
        except KeyError:
            if raise_missing_id:
                raise KeyError("Missing id attribute.")
            else:
                return None

    def _extract_name(self) -> str | None:
        """Return boardgame name."""
        # Return None if can't find the name tag.
        tag = self.item.find("name")
        return None if tag is None else tag.attrib['value']

    def _extract_description(self) -> str | None:
        """Return boardgame description."""
        tag = self.item.find("description")
        return None if tag is None else unescape(tag.text)

    def _extract_year_published(self) -> int | None:
        """Return boardgame year published."""
        tag = self.item.find("yearpublished")
        return None if tag is None else int(tag.attrib['value'])

    def _extract_n_ratings(self) -> int:
        """Return number of ratings."""
        out = self.item.find("statistics")\
                       .find("ratings")\
                       .find("usersrated")\
                       .attrib['value']
        return int(out)

    def _extract_ratings_mean(self) -> float:
        """Return mean average rating to 3 decimals."""
        out = self.item.find("statistics")\
                       .find("ratings")\
                       .find("average")\
                       .attrib['value']
        return round(float(out), 3)

    def _extract_ratings_stddev(self) -> float:
        """Return rating standard deviation to 4 decimals."""
        out = self.item.find("statistics")\
                       .find("ratings")\
                       .find("stddev")\
                       .attrib['value']
        return round(float(out), 4)


# TODO Remove
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
    root = _read_xml_file(file_path)
    # Load up data from each item
    for item in root:
        e = ItemExtractor(item)
        if id:
            out['id'].append(e._extract_id())
        if year_published:
            out['year_published'].append(e._extract_year_published())

    return out
