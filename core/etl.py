import lxml.etree as etree
from pathlib import Path
import pandas as pd
from html import unescape
from typing import Literal

KEY_GENERAL_DATA = 'general_data'
KEY_LINK_DATA = 'link_data'
KEY_POLL_DATA = 'poll_data'


def flatten_xml_folder_to_dataframe(
        dir_path: str,
        get_general_data: bool = True,
        get_link_data: bool = True,
        get_poll_data: bool = True
        ) -> dict[pd.DataFrame]:
    """Given a folder of xml files, return its data in pandas dataframes.

    Args:
        dir_path (str): Location of the folder of xml files.
        get_general_data (bool, optional): Return general data.
            Defaults to True.
        get_link_data (bool, optional): Return data relating boardgames to
            other types of items.
            Defaults to True.
        get_poll_data (bool, optional): Return poll data for each boardgame.
            Defaults to True.

    Raises:
        NotADirectoryError: if the directory doesn't exist or isn't a
            directory.

    Returns:
        dict[pd.DataFrame]: Contains the requested dataframes.
    """
    # Get all the xml files in the dir.
    p = Path(dir_path)
    if not p.is_dir():
        raise NotADirectoryError(f"{dir_path} is not a directory.")
    xml_paths = list(p.glob('*.xml'))
    # Convert each xml file to a DataFrame, then concatenate together
    out = {}
    if get_general_data:
        out[KEY_GENERAL_DATA] = []
    if get_link_data:
        out[KEY_LINK_DATA] = []
    if get_poll_data:
        out[KEY_POLL_DATA] = []

    total_len = len(xml_paths)
    for i, xml_path in enumerate(xml_paths):
        print(f"Extracting file {i+1} of {total_len}")
        dfs_dict = flatten_xml_file_to_dataframes(
                       xml_path,
                       get_general_data=get_general_data,
                       get_link_data=get_link_data,
                       get_poll_data=get_poll_data)
        out[KEY_GENERAL_DATA].append(dfs_dict[KEY_GENERAL_DATA])
        out[KEY_LINK_DATA].append(dfs_dict[KEY_LINK_DATA])
        out[KEY_POLL_DATA].append(dfs_dict[KEY_POLL_DATA])
    if get_general_data:
        print("Concatenating general data...")
        out[KEY_GENERAL_DATA] = pd.concat(out[KEY_GENERAL_DATA],
                                          ignore_index=True)
    if get_link_data:
        print("Concatenating link data...")
        out[KEY_LINK_DATA] = pd.concat(out[KEY_LINK_DATA], ignore_index=True)
    if get_poll_data:
        print("Concatenating poll data...")
        out[KEY_POLL_DATA] = pd.concat(out[KEY_POLL_DATA], ignore_index=True)

    return out


def flatten_xml_file_to_dataframes(
        file_path: str,
        get_general_data: bool = True,
        get_link_data: bool = True,
        get_poll_data: bool = True
        ) -> dict[pd.DataFrame]:
    """Given a single xml file, return its data in pandas DataFrames.

    Args:
        file_path (str): Location of the input xml file.
        get_general_data (bool, optional): Return general data.
            Defaults to True.
        get_link_data (bool, optional): Return data relating boardgames to
            other types of items.
            Defaults to True.
        get_poll_data (bool, optional): Return poll data for each boardgame.
            Defaults to True.

    Returns:
        dict[pd.DataFrame]: Contains the requested dataframes.
    """
    # Initialize
    out = {}
    if get_general_data:
        out[KEY_GENERAL_DATA] = []
    if get_link_data:
        out[KEY_LINK_DATA] = []
    if get_poll_data:
        out[KEY_POLL_DATA] = []

    # Extract data.
    # Link and poll data are lists of dicts themselves,
    # hence extend not append.
    root = _read_xml_file(file_path)
    for item in root:
        extractor = ItemExtractor(item)
        if get_general_data:
            out[KEY_GENERAL_DATA].append(extractor.extract_general_data())
        if get_link_data:
            out[KEY_LINK_DATA].extend(extractor.extract_link_data())
        if get_poll_data:
            out[KEY_POLL_DATA].extend(extractor.extract_poll_data())

    # Convert to pandas DataFrames
    out[KEY_GENERAL_DATA] = pd.DataFrame(out[KEY_GENERAL_DATA])
    out[KEY_LINK_DATA] = pd.DataFrame(out[KEY_LINK_DATA])
    out[KEY_POLL_DATA] = pd.DataFrame(out[KEY_POLL_DATA])

    return out


def write_dataframes_to_csv(
        dict_of_dataframes: dict[pd.DataFrame],
        save_dir_path: str,
        save_file_prefix: str,
        compress_csv: bool = True
        ) -> None:
    """Write a dict of pandas dataframes to csv files.

    Args:
        dict_of_dataframes (dict[pd.DataFrame]): Dict of dataframes, as
            returned from e.g. `flatten_xml_folder_to_dataframe".
        save_dir_path (str): Folder where files will be written.
        save_file_prefix (str): Prefix for the file paths.
        compress_csv (bool, optional): CSV files will be compressed with
            gunzip.
            Defaults to True.
    """
    _write_dataframes(
        dict_of_dataframes=dict_of_dataframes,
        save_dir_path=save_dir_path,
        save_file_prefix=save_file_prefix,
        compress_csv=compress_csv,
        output_format='csv'
    )


def write_dataframes_to_parquet(
        dict_of_dataframes: dict[pd.DataFrame],
        save_dir_path: str,
        save_file_prefix: str,
        ) -> None:
    """Write a dict of pandas dataframes to parquet files.

    Args:
        dict_of_dataframes (dict[pd.DataFrame]): Dict of dataframes, as
            returned from e.g. `flatten_xml_folder_to_dataframe".
        save_dir_path (str): Folder where files will be written.
        save_file_prefix (str): Prefix for the file paths.
    """
    _write_dataframes(
        dict_of_dataframes=dict_of_dataframes,
        save_dir_path=save_dir_path,
        save_file_prefix=save_file_prefix,
        output_format='parquet'
    )


def _write_dataframes(
        dict_of_dataframes: dict[pd.DataFrame],
        save_dir_path: str,
        save_file_prefix: str,
        output_format: Literal['parquet', 'csv'],
        compress_csv: bool = True
        ) -> None:
    """Write a dict of pandas dataframes to parquet or csv files.

    Wrap this func for more convenient client-facing func names.

    Args:
        dict_of_dataframes (dict[pd.DataFrame]): Dict of dataframes, as
            returned from e.g. `flatten_xml_folder_to_dataframe`".
        save_dir_path (str): Folder where files will be written.
        save_file_prefix (str): Folder where files will be written.
        output_format (str of 'parquet'|'csv'): Output files can be parquet or
            csv format. Parquet is recommended if data does not have to be
            human readable, as it is smaller and faster to read.
        compress_csv (bool, optional): CSV files will be compressed with
            gunzip.
            Defaults to True.

    Raises:
        ValueError: If output format is not accepted.
        NotADirectoryError: If the save directory doesn't exist or isn't a
            directory.
    """
    PARQUET_SUFFIX = ".parquet"
    CSV_SUFFIX = ".csv"
    GZ_SUFFIX = '.gz'

    # Check output_format
    output_format_vals = ['parquet', 'csv']
    if output_format not in output_format_vals:
        raise ValueError(f"output_format param not in {output_format_vals}.")

    p = Path(save_dir_path)
    # Check that save dir is in fact a directory
    if not p.is_dir():
        raise NotADirectoryError(f"{save_dir_path} is not a directory.")

    for key, df in dict_of_dataframes.items():
        # Construct the save file path
        match output_format:
            case 'parquet':
                suffix = PARQUET_SUFFIX
                fp = p / f"{save_file_prefix}_{key}{suffix}"
                df.to_parquet(fp, index=False)
            case 'csv':
                suffix = CSV_SUFFIX
                if compress_csv:
                    suffix += GZ_SUFFIX
                fp = p / f"{save_file_prefix}_{key}{suffix}"
                df.to_csv(fp, index=False)


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

    def extract_general_data(
            self,
            raise_missing_id: bool = True,
            id_key: str = 'id',
            type_key: str = 'type',
            name_key: str = 'name',
            description_key: str = 'description',
            yearpublished_key: str = 'year_published',
            minplayers_key: str = 'players_min',
            maxplayers_key: str = 'players_max',
            playingtime_key: str = 'playtime',
            minplaytime_key: str = 'playtime_min',
            maxplaytime_key: str = 'playtime_max',
            minage_key: str = 'age_min',
            usersrated_key: str = 'ratings_n',
            average_key: str = 'ratings_mean',
            bayesaverage_key: str = 'ratings_bayes_average',
            stddev_key: str = 'ratings_stddev',
            median_key: str = 'ratings_median',
            owned_key: str = 'ratings_owned',
            trading_key: str = 'ratings_trading',
            wanting_key: str = 'ratings_wanting',
            wishing_key: str = 'ratings_wishing',
            numcomments_key: str = 'ratings_comments_n',
            numweights_key: str = 'ratings_weights_n',
            averageweight_key: str = 'ratings_weights_average') -> dict:
        """Extract data from an xml item, excluding 'poll' and 'link' tags.

        Args:
            raise_missing_id (bool, optional): Raise on missing id instead of
                setting to None. Defaults to True.

            The following args correspond to what the key should be in the
            returned dictionary for each data field. The names of the args
            correspond to the original xml tags. Default key names do some
            tidying and categorizing of the field names.

            id (str, optional): Id should be present for all boardgames.
                Defaults to 'id'.
            type (str, optional): For distinguishing between boardgames,
                expansions, and accessories.
                Defaults to 'type'.
            name (str, optional): Name of the boardgame.
                Defaults to 'name'.
            description (str, optional): Text description of the game.
                Defaults to 'description'.
            yearpublished (str, optional): Year game was published.
                Defaults to 'year_published'.
            minplayers (str, optional): Minimum number of players.
                Defaults to 'players_min'.
            maxplayers (str, optional): Maximum number of players.
                Defaults to 'players_max'.
            playingtime (str, optional): Playing time.
                Defaults to 'playtime'.
            minplaytime (str, optional): Minimum playing time.
                Defaults to 'playtime_min'.
            maxplaytime (str, optional): Maximum playing time.
                Defaults to 'playtime_max'.
            minage (str, optional): Minimum recommended age.
                Defaults to 'age_min'.
            usersrated (str, optional): Number of user ratings.
                Defaults to 'ratings_n'.
            average (str, optional): Rating average.
                Defaults to 'ratings_mean'.
            bayesaverage (str, optional): Obfuscated rating average use for
                rankings.
                Defaults to 'ratings_bayes_average'.
            stddev (str, optional): Rating standard deviation.
                Defaults to 'ratings_stddev'.
            median (str, optional): Median average.
                Defaults to 'ratings_median'.
            owned (str, optional): Number of users owning this game.
                Defaults to 'ratings_owned'.
            trading (str, optional): Number of users looking to trade the game.
                Defaults to 'ratings_trading'.
            wanting (str, optional): Number of users that want to trade for
                this game.
                Defaults to 'ratings_wanting'.
            wishing (str, optional): Number of users with this game in their
                wishlist.
                Defaults to 'ratings_wishing'.
            numcomments (str, optional): Number of comments on this game.
                Defaults to 'ratings_comments_n'.
            numweights (str, optional): Number of weight ratings. Weights are
                estimate of the complexity of the game.
                Defaults to 'ratings_weights_n'.
            averageweight (str, optional): Average of weight ratings.
                Defaults to 'ratings_weights_average'.

        Returns:
            dict: containing above keys, with their values coerced to an
            appropriate type or None if the value is missing.
        """
        # Uncertain if tags/data will change in future, but this
        # should decouple data keys from xml data, and let each
        # extraction of each tag be independent of each other.
        out = {}
        out[id_key] = self._extract_id(raise_missing_id=raise_missing_id)
        out[type_key] = self._extract_type()
        out[name_key] = self._extract_name()
        out[description_key] = self._extract_description()
        out[yearpublished_key] = self._extract_year_published()
        out[minplayers_key] = self._extract_min_players()
        out[maxplayers_key] = self._extract_max_players()
        out[playingtime_key] = self._extract_playing_time()
        out[minplaytime_key] = self._extract_min_playtime()
        out[maxplaytime_key] = self._extract_max_playtime()
        out[minage_key] = self._extract_min_age()
        out[usersrated_key] = self._extract_users_rated()
        out[average_key] = self._extract_ratings_average()
        out[bayesaverage_key] = self._extract_bayes_average()
        out[stddev_key] = self._extract_ratings_stddev()
        out[median_key] = self._extract_ratings_median()
        out[owned_key] = self._extract_ratings_owned()
        out[trading_key] = self._extract_ratings_trading()
        out[wanting_key] = self._extract_ratings_wanting()
        out[wishing_key] = self._extract_ratings_wishing()
        out[numcomments_key] = self._extract_ratings_num_comments()
        out[numweights_key] = self._extract_ratings_num_weights()
        out[averageweight_key] = self._extract_ratings_average_weight()
        return out

    def extract_poll_data(
            self,
            boardgame_id_key: str = 'boardgame_id'
            ) -> list[dict]:
        """Extract poll tags for the xml item.

         Poll data is in nested xml tags of <poll> -> <results> -> <result>,
         with each poll not necessarily having the same attributes or number of
         result/s etc. This extractor flattens out the data into a "tall" data
         table, wherein each innermost <result> tag corresponds to a
         row/element that includes attributes from the tag's parent <results>
         and <poll> tag.

         The originating boardgame id is included, which its value as an int.
         All other values are str's.

        Args:
            boardgame_id_key (str, optional): Output key for boardgame id.
                Defaults to 'boardgame_id'.

        Returns:
            list[dict]: Each dict corresponding to a <result> tag. Keys for
            <result> tag attributes are prefixed with 'result_', and the keys
            for the parent <results> and <poll> tag attributes are prefixed
            with 'results_' and 'poll_', respectively.
        """
        polls = self.item.findall('poll')
        boardgame_id = self._extract_id()
        out = []
        for poll in polls:
            # Convert to dict to avoid unexpected behaviour
            poll_attributes = dict(poll.attrib)
            # Prefix keys
            poll_attributes = {
                f'poll_{k}': v for k, v in poll_attributes.items()
                }
            # Each poll may have multiple <results> tags
            # with nested <result> tags.
            results_tags = poll.findall('results')
            for results_tag in results_tags:
                results_attributes = dict(results_tag.attrib)
                results_attributes = {
                    f'results_{k}': v for k, v in results_attributes.items()
                    }
                inner_result_tags = results_tag.findall('result')
                for inner_result_tag in inner_result_tags:
                    inner_result_attributes = dict(inner_result_tag.attrib)
                    inner_result_attributes = {
                        f'result_{k}': v
                        for k, v in inner_result_attributes.items()
                        }
                    # Collapse all attributes using Py3.9+ notation
                    out.append(
                        {boardgame_id_key: boardgame_id} |
                        poll_attributes |
                        results_attributes |
                        inner_result_attributes)
        return out

    def extract_link_data(
            self,
            boardgame_id_key: str = 'boardgame_id',
            link_id_key: str = 'link_id') -> list[dict]:
        """Extract all link tags for the item.

        Args:
            boardgame_id_key (str, optional): Output key for boardgame id.
                Defaults to 'boardgame_id'.
            link_id_key (str, optional): Output key for the id associated with
                the link. Defaults to 'link_id'.

        Returns:
            list[dict]: Each dict containing the originating board game, the
                type of link, the link id, and the value of the link.
        """
        links = self.item.findall('link')
        # For binding the boardgame id to the links
        boardgame_id = self._extract_id()
        out = []
        for link in links:
            # .attrib is not quite an actual dict, has unexpected behaviour
            # when int-ing and assigning value
            link = dict(link.attrib)
            # Rename the 'id' key from the <link> tag, and int the value
            link[link_id_key] = int(link.pop('id'))
            # Put 'boardgame_id_key' in the front as client code will
            # probably want that in the first column of a pandas DataFrame.
            # Note: Python 3.7+ should have dict orders preserved.
            link = dict([(boardgame_id_key, boardgame_id), *link.items()])
            out.append(link)
        return out

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

    def _extract_type(self) -> str | None:
        """Return 'thing' type e.g. boardgame."""
        try:
            return self.item.attrib['type']
        except KeyError:
            return

    def _extract_name(self) -> str | None:
        """Return boardgame name."""
        # Return None if can't find the name tag.
        tag = self.item.find("name")
        return None if tag is None else tag.attrib['value']

    def _extract_description(self) -> str | None:
        """Return boardgame description."""
        tag = self.item.find("description")
        # Note: input text is actually doubly escaped
        # e.g. '&amp;quot;' for '"'
        # the xml parser handles one of the unescapes automatically,
        # but need to unescape a second time here.
        # Note 2: it's possible for the tag to exist, but not the text.
        # unescape() can't handle when tag.text is None.
        return None if (tag is None) or (tag.text) is None \
            else unescape(tag.text)

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
        out = self._extract_ratings_subtag_helper("wanting")
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
