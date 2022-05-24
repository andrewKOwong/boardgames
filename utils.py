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
        return int(self.item.attrib['id'])

    def extract_year_published(self):
        return int(self.item.find("yearpublished").attrib['value'])
