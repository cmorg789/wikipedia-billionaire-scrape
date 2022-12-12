import csv
import requests
from html.parser import HTMLParser


# Very Kindly Stolen and Modified from https://github.com/schmijos/html-table-parser-python3 by Josua Schmid
class HTMLTableParser(HTMLParser):
    """ This class serves as a html table parser. It is able to parse multiple
    tables which you feed in. You can access the result per .tables field.
    """

    def __init__(
            self,
            decode_html_entities: bool = False,
            data_separator: str = ' ',
    ) -> None:

        HTMLParser.__init__(self, convert_charrefs=decode_html_entities)

        self._data_separator = data_separator

        self._in_td = False
        self._in_th = False
        self._in_h3 = False
        self._current_table = []
        self._current_row = []
        self._current_cell = []
        self.tables = []
        self.named_tables = {}
        self.name = ""
        self.years = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        """ We need to remember the opening point for the content of interest.
        The other tags (<table>, <tr>) are only handled at the closing point.
        """
        if tag == "table":
            name = [a[1] for a in attrs if a[0] == "id"]
            if len(name) > 0:
                self.name = name[0]
        if tag == 'td':
            self._in_td = True
        if tag == 'th':
            self._in_th = True
        if tag == 'h3':
            self._in_h3 = True

    def handle_data(self, data: str) -> None:
        """ This is where we save content to a cell """
        if self._in_td or self._in_th:
            self._current_cell.append(data.strip())
        if self._in_h3:
            year = data.strip()
            if year.isnumeric():
                self.years.append(year)

    def handle_endtag(self, tag: str) -> None:
        """ Here we exit the tags. If the closing tag is </tr>, we know that we
        can save our currently parsed cells to the current table as a row and
        prepare for a new row. If the closing tag is </table>, we save the
        current table and prepare for a new one.
        """
        if tag == 'td':
            self._in_td = False
        elif tag == 'th':
            self._in_th = False

        if tag in ['td', 'th']:
            final_cell = self._data_separator.join(self._current_cell).strip()
            self._current_row.append(final_cell)
            self._current_cell = []
        elif tag == 'tr':
            self._current_table.append(self._current_row)
            self._current_row = []
        elif tag == 'table':
            self.tables.append(self._current_table)
            if len(self.name) > 0:
                self.named_tables[self.name] = self._current_table
            self._current_table = []
            self.name = ""

        if tag == 'h3':
            self._in_h3 = False


list_page = 'https://en.wikipedia.org/wiki/The_World%27s_Billionaires'

session = requests.session()
response = session.get(list_page)

parser = HTMLTableParser()
parser.feed(response.text)

del parser.tables[0:2]
del parser.tables[-8:]


if len(parser.tables) is not len(parser.years):
    raise Exception("Number of Years Does Not Match number of Tables!")

with open('output.csv', 'w', encoding='utf-8-sig') as csvfile:
    w = csv.writer(csvfile)
    w.writerow(['Year', *parser.tables[0][0]])
    for x in range(len(parser.tables)):
        for row in parser.tables[x][1:]:
            w.writerow([parser.years[x], *row])
