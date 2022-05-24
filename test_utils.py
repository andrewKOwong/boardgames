import utils as u
import lxml.etree as etree

# Use bytes as etree.fromstring only allows encoding declaration
# when it is bytes.
with open('test_data.xml', 'rb') as f:
    xml_data = etree.fromstring(f.read())


# These test the Extractor class
def test_extractor_id(xml_data=xml_data):
    item = u.Extractor(xml_data[0])
    assert item.extract_id() == 28192


def test_extractor_year_published(xml_data=xml_data):
    item = u.Extractor(xml_data[0])
    assert item.extract_year_published() == 1989
