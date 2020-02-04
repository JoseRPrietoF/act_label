import glob, os, copy, pickle
from xml.dom import minidom
import numpy as np

# construct the Sobel x-axis kernel
horizontal_kernel = np.array((
    [-1, -1, -1],
    [2, 2, 2],
    [-1, -1, -1]), dtype="int")
# horizontal_kernel = np.array((
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
#     [ 2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2],
#     [1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]), dtype="int")

# construct the Sobel y-axis kernel
vertical_kernel = np.array((
    [-1, 2, -1],
    [-1, 2, -1],
    [-1, 2, -1]), dtype="int")


THICKNESS = 10
THRESHOLD = 100 #nº pixels
BASELINES = True
BINARY = False
DPI = 600
TWO_DIM = False
SHOW_IMG = False
COLS = True
ROWS = True
TABLE_BOX = True

class PAGE():
    """
    Class for parse Tables from PAGE
    """

    def __init__(self, im_path, debug=False,
                 search_on=["TextLine"]):
        """
        Set filename of inf file
        example : AP-GT_Reg-LinHds-LinWrds.inf
        :param fname:
        """
        self.im_path = im_path
        self.DEBUG_ = debug
        self.search_on = search_on

        self.parse()



    def get_daddy(self, node, searching="TextRegion"):
        while node.parentNode:
            node = node.parentNode
            if node.nodeName.strip() == searching:
                return node

    def get_text(self, node, nodeName="Unicode"):
        TextEquiv = None
        for i in node.childNodes:
            if i.nodeName == 'TextEquiv':
                TextEquiv = i
                break
        if TextEquiv is None:
            # print("No se ha encontrado TextEquiv en una región")
            return None

        for i in TextEquiv.childNodes:
            if i.nodeName == nodeName:
                try:
                    words = i.firstChild.nodeValue
                except:
                    words = ""
                return words

        return None

    def get_TableRegion(self, ):
        """
        Return all the cells in a PAGE
        :return: [(coords, col, row)], dict, dict
        """
        cells = []
        for region in self.xmldoc.getElementsByTagName("TableRegion"):
            coords = self.get_coords(region)
            cells.append(coords)

        return cells

    def get_cells(self, ):
        """
        Return all the cells in a PAGE
        :return: [(coords, col, row)], dict, dict
        """
        cells = []
        cell_by_row = {}
        cell_by_col= {}
        for region in self.xmldoc.getElementsByTagName("TableCell"):
            #TODO different tables
            coords = self.get_coords(region)

            row = int(region.attributes["row"].value)
            col = int(region.attributes["col"].value)
            cells.append((coords, col, row))

            cols = cell_by_col.get(col, [])
            cols.append(coords)
            cell_by_col[col] = cols

            rows = cell_by_row.get(row, [])
            rows.append(coords)
            cell_by_row[row] = rows
        return cells, cell_by_col, cell_by_row

    def get_Baselines(self, ):
        """
        A partir de un elemento del DOM devuelve, para cada textLine, sus coordenadas y su contenido
        :param dom_element:
        :return: [(coords, words)]
        """
        text_lines = []
        for region in self.xmldoc.getElementsByTagName("Baseline"):
            coords = region.attributes["points"].value
            coords = coords.split()
            coords_to_append = []
            for c in coords:
                x, y = c.split(",")
                coords_to_append.append((int(x), int(y)))

            text_lines.append(coords_to_append)


        return text_lines

    def get_textLines(self, ):
        """
        A partir de un elemento del DOM devuelve, para cada textLine, sus coordenadas y su contenido
        :param dom_element:
        :return: [(coords, words)]
        """
        text_lines = []
        for region in self.xmldoc.getElementsByTagName("TextLine"):
            coords = self.get_coords(region)
            text = self.get_text(region)

            text_lines.append((coords, text))


        return text_lines

    def get_textRegions(self, ):
        """
        A partir de un elemento del DOM devuelve, para cada textregion, sus coordenadas y su id
        :param dom_element:
        :return: [(coords, id)]
        """
        text_lines = []
        for region in self.xmldoc.getElementsByTagName("TextRegion"):
            coords = self.get_coords(region)
            id = region.attributes["id"].value

            text_lines.append((coords, id))
        return text_lines

    def get_coords(self, dom_element):
        """
        Devuelve las coordenadas de un elemento. Coords
        :param dom_element:
        :return: ((pos), (pos2), (pos3), (pos4)) es un poligono. Sentido agujas del reloj
        """
        coords_element = None
        for i in dom_element.childNodes:
            if i.nodeName == 'Coords':
                coords_element = i
                break
        if coords_element is None:
            print("No se ha encontrado coordenadas en una región")
            return None

        coords = coords_element.attributes["points"].value
        coords = coords.split()
        coords_to_append = []
        for c in coords:
            x, y = c.split(",")
            coords_to_append.append((int(x), int(y)))
        return coords_to_append

    def parse(self):
        self.xmldoc = minidom.parse(self.im_path)

    def get_width(self):
        page = self.xmldoc.getElementsByTagName('Page')[0]
        return int(page.attributes["imageWidth"].value)

    def get_height(self):
        page = self.xmldoc.getElementsByTagName('Page')[0]
        return int(page.attributes["imageHeight"].value)

def get_all_xml(path, ext="xml"):
    file_names = glob.glob("{}*.{}".format(path,ext))
    return file_names
