from .ResultTable import ResultTable
from .StatCalculator import compare_anova


class ResultsTableBuilder:
    """ Builds the table objects from the table commands and sample data"""

    def __init__(self):
        pass

    def create_tables(self, table_commands, job):
        """ Builds an array of tables, one for each table command.
        A table command consists of the format TableType;field1:field1Value,field2:field2Value ect..

        Args:
            table_commands (str[]): an array of strings from the template, each string corresponding
            to a table command (requested table required for the reports)
            job (SRGJob): job object that contains all the producst and their data

        Returns:
            ResultTable[]: an array of result tables with all the calcualted data
        """

        # create a dictionary to hold each table object (table is a 2d array)
        # the key is the command and the value is the table
        tables = {}

        # loop through each command
        for command in table_commands:
            command_split = command.split(';')

            # must have at least 2 parts, the table type (index 0) and the fields (index 1)
            if len(command_split) >= 2:
                table_type = command_split[0]

                # build a table based on the table type
                table = None

                # Samples table will build a table with a row for each sample
                # along with the required details in each column
                if table_type == 'SamplesTable':
                    # part 3 = widths of columns
                    widths = None
                    if len(command_split) == 3:
                        widths = command_split[2]
                    table = self.build_sample_table(command_split[1], widths, job)

                    # summary table will list all samples and the avergae result
                # for each test
                if table_type == "SummaryTable" and len(command_split) > 4:

                    # part 2 = sample name, part 3 = test names,
                    # part 4 = number precision, part 5 is orientation
                    # part 6 = widths of columns
                    widths = None
                    if len(command_split) == 6:
                        widths = command_split[5]
                    table = self.build_summary_table(command_split[1],
                                                     command_split[2],
                                                     command_split[3],
                                                     command_split[4],
                                                     widths,
                                                     job)

                    # SampleResultsTable provides a separate table for each sample
                # with the result for each replicate of each test, std and average
                if table_type == "SampleResultsTable" and len(command_split) > 4:

                    # part 2 = sample name, part 3 = test names,
                    # part 4 = number precision, part 5 is orientation
                    # part 6 = widths of columns
                    widths = None
                    if len(command_split) == 6:
                        widths = command_split[5]
                    table = self.build_sample_results_table(command_split[1],
                                                            command_split[2],
                                                            command_split[3],
                                                            command_split[4],
                                                            widths,
                                                            job)
                    # StatCompareTable provides a separate table for each sample
                # with the result of a statistical comparison with every other sample in the set
                # table will show which samples are statistically better tha,
                # no stat difference to and worse than.
                if table_type == "StatCompareTable" and len(command_split) == 4:

                    # part 2 = sample name,
                    # part 3 = comparing samples name (might be better to abreviate names here)
                    # part 4 = the name of the test to run the comparisons on
                    # part 5 = widths of columns
                    widths = None
                    if len(command_split) == 5:
                        widths = command_split[4]
                    table = self.build_stat_compare_table(command_split[1],
                                                          command_split[2],
                                                          command_split[3],
                                                          widths,
                                                          job)

                if table is not None:
                    tables[command] = table

        return tables

    def build_sample_table(self, fields_string, widths, job):
        """ This is a simple table based on fields from the details columns
        The details columns are the first two columns in the google sheets doc
        Any field can be used from the details columns. The table lists all
        samples along with the selected fields

        Args:
            fields_string (str): the list of fields to include in the table
            widths (str): the widths string that specifies the column widths
            job (SRGJob): the job object that contains all the samples and thier data

        Returns:
            ResultTable: table object containing the
            data for the table
        """

        # The fields are separated by a comma
        fields = fields_string.split(',')

        # declare a 2d array for the table
        table = ResultTable()
        if widths is not None:
            table.column_widths = widths.split(',')

        # header fields on first row
        header_row = []
        for field in fields:
            header_row.append(field)
        table.set_columns(header_row)

        # go through each sample and add extract the correct data for each cell
        for sample in job.samples:

            # a single row contains the info from a single sample
            row = []

            # go through each of the requested fields and fill in the data from the
            # sample.
            for field in fields:
                if field in sample.details:
                    row.append(sample.details[field])
                else:  # blank cell if data is missing
                    row.append("")

            # append to the table
            table.add_row(row)

        # return the final table
        return table

    def build_summary_table(self, sample_name, tests, precision, orientation, widths, job):
        """ The summary table lists each sample on a new line and the average
        result for each test that is specified.

        Args:
            sample_name (str): the title of the table - full name of sample
            tests (str): Comma seperated list of tests to include
            precision (str): An integer, as a string, for the number of decimal places
                to reports
            orientation (str): Vertical-lists samples vertically, Horizontal-lists
                samples horizontally
            widths (str): the widths string that specifies the column widths
            job (SRGJob): the job object that contains all the samples and thier data

        Returns:
            ResultTable: table object containing the  data for the table
        """

        # The fields are separated by a comma
        tests = tests.split(',')

        # check if any tests are ordinal and get the values of the categories
        tests, factor_values = self.test_factors(tests)

        # sample string can have a number of sample details included with each
        # detail separated by a +
        name_fields = sample_name.split('+')

        # get the reporting precision as a number
        try:
            report_precision = int(precision)
        except ValueError:  # set a default as zero if invalid argument
            report_precision = 0

        # declare a Table object to hold the data
        table = ResultTable()
        if widths is not None:
            table.column_widths = widths.split(',')

        # header fields on first row
        header_row = ["Sample"]
        for test_name in tests:
            test_name = test_name.strip()
            header_row.append(test_name)
        table.set_columns(header_row)

        # go through each sample and add extract the correct data for each cell
        for sample in job.samples:

            # a single row contains the info from a single sample, initialised
            # with the descriptive name of the sample
            row = [sample.build_name(name_fields)]

            # go through each of the requested tests and fill in the data from the
            # sample.
            for test in tests:

                test = test.strip()

                if test in sample.test_results:

                    # get the average result of all the tests
                    if test in factor_values:  # ordinal values
                        result = sample.result_average_ordinal(test, factor_values)
                        val = factor_values[test][result]

                    else:  # numerical
                        result = sample.result_average(test)
                        # format this as a string to the correct precision
                        val = "{0}".format(round(result, report_precision))
                        # check if this is a percentage and add the percent sign
                        if test in sample.test_units:
                            val += sample.test_units[test]

                    # add the cell
                    row.append(val)

                else:  # blank cell if data is missing
                    row.append("")

            # append to the table
            table.add_row(row)

        # default is vertical so flip if orientation is horizontal
        if orientation == "Horizontal":
            table.transpose()

        # return the final table
        return table

    def build_sample_results_table(self, sample_name, tests, precision, orientation, widths, job):
        """ The summary table lists each sample on a new line and the average
        result for each test that is specified.

        Args:
            title (str): the title of the table
            tests (str): Comma seperated list of tests to include
            precision (str): An integer, as a string, for the number of decimal places
                to reports
            orientation (str): Vertical-lists tests vertically, Horizontal-lists
                tests horizontally
            widths (str): the widths string that specifies the column widths
            job (SRGJob): the job object that contains all the samples and thier data

        Returns:
            ResultTable[]: an array of table objects containing the
            data for the table. there is a table object for each sample
        """

        # this will return an array of tables, one for each sample
        tables = []

        # The fields are separated by a comma
        tests = tests.split(',')

        # check if any tests are ordinal and get the values of the categories
        tests, factor_values = self.test_factors(tests)

        # sample string can have a number of sample details included with each
        # detail separated by a +
        name_fields = sample_name.split('+')

        # get the reporting precision as a number
        try:
            report_precision = int(precision)
        except ValueError:  # set a default as zero if invalid argument
            report_precision = 0

        # go through each sample and add extract the correct data for each cell
        for sample in job.samples:

            # declare a table object to hold the data
            table = ResultTable()
            if widths is not None:
                table.column_widths = widths.split(',')

            table.title = sample.build_name(name_fields)

            # header fields on first row
            header_row = ["Test"]
            # Add a Result i column for each possible replicate
            # sample.get_max_replicates() is used to count how many columns are needed
            max_reps = sample.get_max_replicates(tests)
            for i in range(max_reps):
                header_row.append("Result {0}".format(i + 1))
            header_row.append("")  # blank column
            header_row.append("Average")
            header_row.append("Std. Dev.")
            table.set_columns(header_row)

            # go through each of the requested tests and fill in the data from the
            # sample.
            for test in tests:

                test = test.strip()

                # create the row starting with the test name
                row = [test]

                if test in sample.test_results:
                    # add a cell for each of the test replicates
                    for rep in sample.test_results[test]:
                        form_val = rep
                        if test in sample.test_results_values: #numeric
                            form_val = float(rep)
                            if report_precision == 0:
                                form_val = "{0}".format(int(round(form_val, report_precision)))
                            else:
                                form_val = "{0}".format(round(form_val, report_precision))
                        if test in sample.test_units:
                            form_val += sample.test_units[test]

                        row.append(form_val)

                    # add in blank cells if the replicates are not equal to the max
                    for i in range(max_reps - len(sample.test_results[test])):
                        row.append("")

                    # add the blank column, makes it easier to read table
                    row.append("")

                    # get the average result of all the tests
                    if test in factor_values:  # ordinal values
                        result = sample.result_average_ordinal(test, factor_values)
                        std_val = ""  # no standard deviation for these tests
                        result_val = "{0}".format(round(result, report_precision))
                    # non numerical results without factors won't have an everage or std
                    elif test not in sample.test_results_values:
                        result_val = "N/A"
                        std_val = "N/A"
                    else:  # numerical
                        result = sample.result_average(test)
                        std = sample.result_std(test)
                        # format this as a string to the correct precision
                        if report_precision == 0:
                            std_val = "{0}".format(int(round(std, report_precision)))
                            result_val = "{0}".format(int(round(result, report_precision)))
                        else:
                            std_val = "{0}".format(round(std, report_precision))
                            result_val = "{0}".format(round(result, report_precision))


                    # check if this is a percentage and add the percent sign
                    if test in sample.test_units:
                        result_val += sample.test_units[test]
                        std_val += sample.test_units[test]

                    # add the average and std cells
                    row.append(result_val)
                    row.append(std_val)

                else:  # blank cell if data is missing
                    for i in range(max_reps + 3):
                        row.append("")

                # append to the table
                table.add_row(row)

            # default is vertical so flip if orientation is horizontal
            if orientation == "Horizontal":
                table.transpose()

            tables.append(table)

        # return the final array of samples tables
        return tables

    def build_stat_compare_table(self, sample_name, comparing_sample_name, test, widths, job):
        """ The summary table lists each sample on a new line and the average
        result for each test that is specified.

        Args:
            sample_name (str): the title of the table - full sample name
            comparing_sample_name (str): Sample details field with the sample name
                of the comparing sample, ideally use an abreviated name here
            test: The name of the test to run the comparisons on
            widths (str): the widths string that specifies the column widths
            job (SRGJob): the job object that contains all the samples and thier data

        Returns:
            ResultTable[]: an array of table objects containing the
            data for the table. There is a table object for each sample
        """
        test = test.strip()

        requires_flip = '(FLIP)' in test.upper()
        test = test.replace('(flip)', '')
        test = test.replace('(FLIP)', '')
        test = test.replace('(Flip)', '')

        # this will return an array of tables, one for each sample
        tables = []

        # sample string can have a number of sample details included with each
        # detail separated by a +
        name_fields = sample_name.split('+')
        compare_name_fields = comparing_sample_name.split('+')

        # go through each sample and add extract the correct data for each cell
        for sample in job.samples:

            # declare a table object to hold the data
            table = ResultTable()
            if widths is not None:
                table.column_widths = widths.split(',')

            table.title = test + ": " + sample.build_name(name_fields)

            # header fields on first row
            header_row = ["Statistically Better Than:",
                          "No Statistical Difference",
                          "Statistically Worse Than:"]
            table.set_columns(header_row)

            # calculate the statistical comparisons of this product compared
            # to each other product in the set
            all_results = job.get_all_results(compare_name_fields, test)

            try:
                better_than, no_diff, worse_than = compare_anova(all_results, sample.build_name(compare_name_fields))
                if requires_flip:
                    worse_than, better_than = better_than, worse_than
            except ValueError:
                raise ValueError("{0} for {1} error in values for ANOVA tables!".format(test, sample.build_name(
                    compare_name_fields)))

            # create a row to hold the string list of all the items
            row = ["", "", ""]

            for item in better_than:
                if len(row[0]) > 0:
                    row[0] += ", "
                row[0] += item

            for item in no_diff:
                if len(row[1]) > 0:
                    row[1] += ", "
                row[1] += item

            for item in worse_than:
                if len(row[2]) > 0:
                    row[2] += ", "
                row[2] += item

            table.add_row(row)
            """
            #work out how many table rows are needed
            max_rows = max(len(better_than), len(no_diff), len(worse_than))

            #loop through the number of rows and fill the cells with the 
            #products that are better than, no stat diff and worse than 
            #the current product
            index = 0
            while index < max_rows:

                row = []

                if index < len(better_than):
                    row.append(better_than[index])
                else:
                    row.append("")

                if index < len(no_diff):
                    row.append(no_diff[index])
                else:
                    row.append("")

                if index < len(worse_than):
                    row.append(worse_than[index])
                else:
                    row.append("")

                #append to the table
                table.add_row(row)

                index += 1
            """

            tables.append(table)

        # return the final array of samples tables
        return tables

    def test_factors(self, tests):
        """ Ordinal results need to get values for average calculations
        This function extracts the possible factors out of the table command and assigns
        the factors a numerical value.
        A test name, if ordinal, should have the factors listed after in the form
        test_name|Low value, medium value, high value

        Args:
            tests: The array of tests

        Returns:
            str[]: an array of the test names with the factors removed
            dict(str, int): a dict with the factor name as key and numerical value

        """

        test_factors = {}
        mod_tests = []

        # loop through all tests and look for a | which indicates test has ordinal values
        for test in tests:

            # this test has ordinal values
            if '|' in test:

                # strip the test name as the first part
                t_f = test.split('|')

                # add to the test name array
                test_name = t_f[0]

                test_name = test_name.strip()

                mod_tests.append(test_name)

                if len(t_f) > 1:

                    # strip the possible categorical values separated by :
                    factors = t_f[1].split(':')

                    # remove white space
                    for factor in factors:
                        factor = factor.strip()

                    # assign these values to a dict with the test name as key
                    test_factors[test_name] = factors
            else:
                # normal numerical values so just add the test name
                mod_tests.append(test)

        return mod_tests, test_factors






