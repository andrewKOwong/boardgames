import utils as u
import lxml.etree as etree
import pytest

# Test data contains two items, a boardgame
# as the first item, and additional items for error handling testing.
# Path is as if `python -m pytest` is being run in the root folder.
TEST_DATA_FILEPATH = 'test/test_data.xml'

# Use bytes as etree.fromstring only allows encoding declaration
# when it is bytes.
with open(TEST_DATA_FILEPATH, 'rb') as f:
    xml_data = etree.fromstring(f.read())


def test_read_xml_file(file_path=TEST_DATA_FILEPATH):
    root = u.read_xml_file(file_path)
    assert root.tag == 'items'
    assert root.attrib.keys()[0] == 'termsofuse'


# extractor_* test the Extractor class
def test_extractor_id(xml_data=xml_data):
    item = u.Extractor(xml_data[0])
    assert item.extract_id() == 28192
    # Test missing id attribute
    item = u.Extractor(xml_data[1])
    with pytest.raises(KeyError):
        item.extract_id()


def test_extractor_year_published(xml_data=xml_data):
    item = u.Extractor(xml_data[0])
    assert item.extract_year_published() == 1989
    # Test missing yearpublished tag
    item = u.Extractor(xml_data[1])
    with pytest.raises(TypeError):
        item.extract_year_published()
