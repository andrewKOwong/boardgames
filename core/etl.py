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
        # Uncertain if tags/data will change in future, but this 
        # should decouple data keys from xml data, and let each 
        # extraction of each tag be independent of each other.
        out = {}
        out['id'] = self._extract_id(raise_missing_id=raise_missing_id)
        out['name'] = self._extract_name()
        out['description'] = self._extract_description()
        out['year_published'] = self._extract_year_published()
        out['players_min'] = self._extract_min_players()
        out['players_max'] = self._extract_max_players()
        out['playtime'] = self._extract_playing_time()
        out['playtime_min'] = self._extract_min_playtime()
        out['playtime_max'] = self._extract_max_playtime()
        out['age_min'] = self._extract_min_age()
        out['ratings_n'] = self._extract_users_rated()
        out['ratings_mean'] = self._extract_ratings_average()
        out['ratings_bayes_average'] = self._extract_bayes_average()
        out['ratings_stddev'] = self._extract_ratings_stddev()
        out['ratings_median'] = self._extract_ratings_median()
        out['ratings_owned'] = self._extract_ratings_owned()
        out['ratings_trading'] = self._extract_ratings_trading()
        out['ratings_wanting'] = self._extract_ratings_wanting()
        out['ratings_wishing'] = self._extract_ratings_wishing()
        out['ratings_comments_n'] = self._extract_ratings_num_comments()
        out['ratings_weights_n'] = self._extract_ratings_num_weights()
        out['ratings_weights_average'] = self._extract_ratings_average_weight()
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

    def _extract_min_players(self) -> int | None:
        """Return minimum number of players."""
        tag = self.item.find("minplayers")
        return None if tag is None else int(tag.attrib['value'])

    def _extract_max_players(self) -> int | None:
        """Return maximum number of players"""
        tag = self.item.find("maxplayers")
        return None if tag is None else int(tag.attrib['value'])

    def _extract_playing_time(self) -> int | None:
        """Return playing time."""
        tag = self.item.find("playingtime")
        return None if tag is None else int(tag.attrib['value'])

    def _extract_min_playtime(self) -> int | None:
        """Return minimum playing time."""
        tag = self.item.find("minplaytime")
        return None if tag is None else int(tag.attrib['value'])

    def _extract_max_playtime(self) -> int | None:
        """Return maximum playing time."""
        tag = self.item.find("maxplaytime")
        return None if tag is None else int(tag.attrib['value'])

    def _extract_min_age(self) -> int | None:
        """Return minimum recommended age."""
        tag = self.item.find("minage")
        return None if tag is None else int(tag.attrib['value'])

    def _extract_ratings_subtag_helper(
            self,
            subtag: str,
            attrib: str = 'value') -> str | None:
        """Helper func to get values for subtags under "statistics -> ratings".

        Args:
            subtag (str): Subtag name.
            attrib (str, optional): Subtag attribute to retrieve.
                Defaults to 'value'.

        Returns:
            str | None: Value of the subtag, otherwise None if it's missing.
        """
        # if statistics or ratings tag doesn't exist, .find() return None,
        # so further .find() or .attrib() should raise AttributeError
        try:
            return self.item.find("statistics")\
                            .find("ratings")\
                            .find(subtag)\
                            .attrib[attrib]
        except AttributeError:
            return

    def _extract_users_rated(self) -> int | None:
        """Return the number of user ratings."""
        out = self._extract_ratings_subtag_helper("usersrated")
        return None if out is None else int(out)

    def _extract_ratings_average(self) -> float | None:
        """Return mean average rating to 3 decimals."""
        out = self._extract_ratings_subtag_helper("average")
        return None if out is None else round(float(out), 3)

    def _extract_bayes_average(self) -> float | None:
        """Return bayes average rating to 3 decimals."""
        out = self._extract_ratings_subtag_helper("bayesaverage")
        return None if out is None else round(float(out), 3)

    def _extract_ratings_stddev(self) -> float | None:
        """Return rating standard deviation to 4 decimals."""
        out = self._extract_ratings_subtag_helper("stddev")
        return None if out is None else round(float(out), 4)

    def _extract_ratings_median(self) -> float | None:
        """Return rating median to 1 decimal."""
        out = self._extract_ratings_subtag_helper("median")
        return None if out is None else round(float(out), 1)

    def _extract_ratings_owned(self) -> int | None:
        """Return number of times this item is owned."""
        out = self._extract_ratings_subtag_helper("owned")
        return None if out is None else int(out)

    def _extract_ratings_trading(self) -> int | None:
        """Return number of times this item is up for trade."""
        out = self._extract_ratings_subtag_helper("trading")
        return None if out is None else int(out)

    def _extract_ratings_wanting(self) -> int | None:
        """Return number of times this item is wanted."""
        out = self._extract_ratings_subtag_helper("wanted")
        return None if out is None else int(out)

    def _extract_ratings_wishing(self) -> int | None:
        """Return number of times this item is wishlisted."""
        out = self._extract_ratings_subtag_helper("wishing")
        return None if out is None else int(out)

    def _extract_ratings_num_comments(self) -> int | None:
        """Return number of comments."""
        out = self._extract_ratings_subtag_helper("numcomments")
        return None if out is None else int(out)

    def _extract_ratings_num_weights(self) -> int | None:
        """Return number of weight (complexity) ratings this item has."""
        out = self._extract_ratings_subtag_helper("numweights")
        return None if out is None else int(out)

    def _extract_ratings_average_weight(self) -> float | None:
        """Return mean average weight of this item to 3 decimals."""
        out = self._extract_ratings_subtag_helper("averageweight")
        return None if out is None else round(float(out), 3)
