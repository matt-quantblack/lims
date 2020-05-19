import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import six


class ResultTable:
    """ A table class that hold calcualted result information """

    def __init__(self):
        """ Init function for the Results Table

        Attributes:
            title (str): A title for the table
            table (Pandas.DataFrame): the table that holds all the results
            column_widths (str[]): an array of widths to use for the columns

        """
        self.title = None
        self.table = pd.DataFrame()
        self.column_widths = None

    def transpose(self):
        """ Changes the orientation of the table from vertical to horizontal """

        if len(self.table.columns) > 1:
            self.table.index = self.table.index + 1
            self.table.loc[0] = self.table.columns
            self.table = self.table.sort_index()
            t = self.table.transpose()
            t = t.reset_index(drop=True)
            t.columns = t.iloc[0]
            t = t.iloc[1:]
            t = t.reset_index(drop=True)

            self.table = t

    def set_columns(self, column_names):
        """ Sets the names of the columns

        Args:
            column_names (str): The array of names for the columns

        """

        for name in column_names:
            self.table[name] = pd.Series()

    def add_row(self, row):
        """ Adds a new row of data to the table

        Args:
            row (str[]): An array of strings for each column

        """

        new_row = pd.DataFrame(data=[row], columns=self.table.columns)
        self.table = self.table.append(new_row, ignore_index=True)

    def render_mpl_table(self, col_width=5.0, row_height=0.625, font_size=12,
                         header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='#4d4d4d',
                         bbox=[0, 0, 1, 1], header_columns=0,
                         ax=None, **kwargs):
        """ Draws the table as a rendered image

        Args:
            col_width (double): The width of the columns
            row_width (double): The height of the rows
            font_size (int): The size of the font
            header_color (str): The hex colour for the header
            row_color (str[]): The hex colour for the alternating rows
            edge_color (str): The hex colour for the border
            bbox (int[]): The bounding box
            header_columns (int), number of head columns

        Returns:
            fig: The created image


        """

        data = self.table

        if ax is None:
            size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
            fig, ax = plt.subplots(figsize=size)
            ax.axis('off')

        mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

        mpl_table.auto_set_font_size(False)
        mpl_table.set_fontsize(font_size)

        for k, cell in six.iteritems(mpl_table._cells):
            cell.set_edgecolor(edge_color)
            if k[0] == 0 or k[1] < header_columns:
                cell.set_text_props(weight='bold', color='w')
                cell.set_facecolor(header_color)
            else:
                cell.set_facecolor(row_colors[k[0] % len(row_colors)])
        return fig

