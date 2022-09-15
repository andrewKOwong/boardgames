import core.etl as etl
import lxml.etree as etree
from pathlib import Path
from html import unescape

# Test data contains two items, a boardgame
# as the first item, and additional items for error handling testing.
# Path is as if `python -m pytest` is being run in the root folder.
TEST_DATA_FILEPATH = 'test/test_data.xml'
# Just a single item and its data values it should have
TEST_DATA_SINGLE_FILEPATH = 'test/test_data_single.xml'
# The raw text is double escaped.
# Not totally sure how, but lxml.etree parsers unescapes it once automatically,
# With ItemExtractor unescaping it a second time.
# Hence for test, will need to unescape it twice here.
TEST_DATA_SINGLE_DESC = unescape(unescape(
    "1812 Caspara is a generic wargame at the time of the Napoleonic Wars. Two"
    " armies land on a small island and fight for it. The rules are based on "
    "those of &amp;quot;1812: Les Arapiles&amp;quot; published in a previous "
    "issue of Casus Belli.&amp;#10;&amp;#10;Published in Casus Belli #49. You "
    "need Casus Belli #41 for the Standard Rules.&amp;#10;&amp;#10;"
))

TEST_DATA_SINGLE_VALUES = {'id': 28192,
                           'type': 'boardgame',
                           'name': '1812: Caspara',
                           'description': TEST_DATA_SINGLE_DESC,
                           'year_published': 1989,
                           'players_min': 2,
                           'players_max': 2,
                           'playtime': 120,
                           'playtime_min': 120,
                           'playtime_max': 120,
                           'age_min': 12,
                           'ratings_n': 7,
                           'ratings_mean': 5.5,
                           'ratings_bayes_average': 0,
                           'ratings_stddev': 1.6690,
                           'ratings_median': 0,
                           'ratings_owned': 36,
                           'ratings_trading': 0,
                           'ratings_wanting': 1,
                           'ratings_wishing': 4,
                           'ratings_comments_n': 5,
                           'ratings_weights_n': 1,
                           'ratings_weights_average': 2}


def test_read_xml_file(file_path=TEST_DATA_FILEPATH):
    root = etl._read_xml_file(file_path)
    assert root.tag == 'items'
    assert root.attrib.keys()[0] == 'termsofuse'


def test_item_extractor():
    """Given a single item from an xml file, test field extraction."""
    # Single item
    item = etree.fromstring(Path(TEST_DATA_SINGLE_FILEPATH).read_bytes())[0]
    # Load extractor
    ex = etl.ItemExtractor(item)
    # Check each value
    out = ex.extract_general_data()
    for key in TEST_DATA_SINGLE_VALUES.keys():
        assert out[key] == TEST_DATA_SINGLE_VALUES[key]
