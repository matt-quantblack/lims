"""
    NOTE on google sheets format:

    The microsoft Excel document must have the following:
    Columns A and B from cell 2 down are all the sample details
    Column A is the name of the detail and Column B is the value of the detail
    Columns B and onwards can be anything but there must be three speicifc columns
    Replicate, Test Name, Result
    Each row in these columns is counted as a test result and are grouped together
    by test name, replicate
    All rows must have a unique TestName-Replicate combination or an error is shown

"""
from .SampleData import SampleData
from .SRGJob import SRGJob
import datetime
import math
import pandas as pd


class MSExcelDataParser:
    """ Opens a google sheets document and parses the contents into a job class """

    def __init__(self, filepath):
        self.filepath = filepath

    def parse_document(self):
        """ The main function that opens the document, parses the data into a jobs
        object and returns the resulting job with all the calculated values

        Args:
            filepath (str): path of excel file

        Returns:
            job (SRGJob): the job object containing all the job information
                and calculated results from the data

        """
        # Get the Excel file
        xl = pd.ExcelFile(self.filepath)

        # The job object will hold the list of samples and their data
        job = SRGJob()

        # go through each sheet in the spreadsheets and process into a SampleData object
        for title in xl.sheet_names:

            #get sheet as a data frame
            df = xl.parse(title, parse_dates=False)

            # special Details tab is used to extract the details required for the reports
            if title == "Details":
                self.parse_details(job, df)
            else:
                self.parse_sample(job, df, title)

        # return None if no samples were added to this job
        if len(job.samples) > 0:
            return job
        else:
            return None

    def parse_details(self, job, df):
        """ Parses the details tab which has information about the reports

        Args:
            job (SRGJob): the pointer to the job object to hold all the results
            df (pandas.dataframe): excel sheet as a data frame

        """

        # fields columns, first column is name of field and second
        # column is the value for the field
        for index, row in df.iterrows():
            if len(row) == 2 and row[0] != '':
                if isinstance(row[1], datetime.date):
                    row[1] = row[1].strftime("%d/%m/ %Y")
                job.fields[row[0]] = row[1]

    def parse_sample(self, job, df, title):
        """ Parses each tab in the sheet as a separate sample.

        Args:
            job (SRGJob): the pointer to the job object to hold all the results
            df (pandas.dataframe): excel sheet as a data frame

        """
        # create a sample data object to store all the extracted data
        sample_data = SampleData()


        # Sample details columns, first column is name of detail and second
        # column is the value for the detail
        for index, row in df.iterrows():
            if pd.notnull(row[0]) and pd.notnull(row[1]):
                sample_data.add_detail(row[0], str(row[1]))

        # names of all the columns in the spreadsheet. Need to get the index
        # of the Test Name and Result columns, these are the data columns that
        # need to be extracted from the sheet
        if "Test Name" not in df.columns:
            raise ValueError("Test Name column missing from data.")
        if "Result" not in df.columns:
            raise ValueError("Result missing from data.")

        # make sure the columns are strings - some results are strings
        df["Result"] = df["Result"].astype(str)

        # go through each row in the extracted data and get the value for
        # Test Name and Result
        for index, row in df.iterrows():
            if pd.notnull(row["Test Name"]) and pd.notnull(row["Result"]):
            # Add the Result for this Test Name to the sample_data test result array
                format = ""
                if "Format" in row:
                 if  isinstance(row["Format"], float):
                     if math.isnan(row["Format"]) is False:
                         format = row["Format"]
                     else:
                         format = ""
                 else:
                    format = row["Format"]
                sample_data.add_result(row["Test Name"], row["Result"], format)

                # if this sample had some useable data then add it to the job object
        if len(sample_data.details) > 0 and len(sample_data.test_results) > 0:
            job.add_sample(sample_data)

