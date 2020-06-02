import unittest
from .MSExcelDataParser import MSExcelDataParser
from .MicrosoftDocxParser import MicrosoftDocxParser
from .ResultsTableBuilder import ResultsTableBuilder

class ReportBuilderTests(unittest.TestCase):

    def setUp(self):
        self.data_doc = "D:/Downloads/Test (2).xlsx"
        self.template_doc = "D:/Downloads/Test (2).docx"
        self.save_doc = "./eldashboard/temp_report_docs/Test.docx"

    def test_parse_excel(self):

        xldp = MSExcelDataParser(self.data_doc)
        job = xldp.parse_document()

        self.assertEqual(len(job.samples), 11)
        self.assertEqual(job.fields['ShareWith'], 'matt@enzymelabs.com.au')
        self.assertEqual(job.samples[3].test_results["Coffee (CS51)"][3], '0.4771134984')

    def test_get_table_commands(self):

        template_doc = ""

        # create the MicrosofDocxParser to parse the template document
        doc_parser = MicrosoftDocxParser()

        # get the table commands so we can build the required tables from the data
        table_commands = doc_parser.extract_table_commands(self.template_doc)

        self.assertEqual(table_commands[77], 'StatCompareTable;Sample Name+Sample Batch;Sample Abrev.; Blood/Milk/Ink (C05)')


    def test_build_tables(self):

        #create a job from and excel data file
        xldp = MSExcelDataParser(self.data_doc)
        job = xldp.parse_document()

        # create the MicrosofDocxParser to parse the template document
        doc_parser = MicrosoftDocxParser()

        # get the table commands so we can build the required tables from the data
        table_commands = doc_parser.extract_table_commands(self.template_doc)

        # build the tables
        table_builder = ResultsTableBuilder()
        tables = table_builder.create_tables(table_commands, job)

        self.assertEqual(tables['StatCompareTable;Sample Name+Sample Batch;Sample Abrev.; Blood/Milk/Ink (C05)'][10].table.iloc[0,1], 'Omo Dual Caps, Gain, Omo Capsules, 988B3-191213')

    def test_full_report(self):
        # create a job from and excel data file
        xldp = MSExcelDataParser(self.data_doc)
        job = xldp.parse_document()

        # create the MicrosofDocxParser to parse the template document
        doc_parser = MicrosoftDocxParser()

        # get the table commands so we can build the required tables from the data
        table_commands = doc_parser.extract_table_commands(self.template_doc)

        # build the tables
        table_builder = ResultsTableBuilder()
        tables = table_builder.create_tables(table_commands, job)

        #generate and save reports
        doc_parser.generate_report(self.template_doc, self.save_doc, job.fields, tables)

        self.assertEqual(1,1)

if __name__ == '__main__':
    unittest.main()
