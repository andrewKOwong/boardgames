import utils as u
import lxml.etree as etree

TEST_DATA_FILEPATH = 'test_data.xml'

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


def test_extractor_year_published(xml_data=xml_data):
    item = u.Extractor(xml_data[0])
    assert item.extract_year_published() == 1989
