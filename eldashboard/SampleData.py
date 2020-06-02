import re
import statistics


class SampleData:
    """Object that stores all the sample details and test results.
    Can also get average and standard deviations of the test results.
    """

    def __init__(self):
        """ Init function for the data of the sample

        Attributes:
            details (dict): A dictionary of fields and the values used for
                inserting into the doc template
            test_results (dict): A dictionary of results with the test name as
                the key and the value as a string representation of the result
            test_results_values (dict): A dictionary of results with the test name as
                the key and the value as a double representation of the result
            test_units (dict): A dictionary of test units with the test name as
                the key and the test unit as the value
        """
        self.details = {}
        self.test_results = {}
        self.test_results_values = {}
        self.test_units = {}

    def get_max_replicates(self, tests=None):
        """Gets the maximum number of replicates across all tests. Used
        for determing the number of columns used for displaying results

        Returns:
            int: The maximum replicates
        """

        if tests == None:
            tests = list(self.test_results.keys())

        curr_max = 0
        # get all the results for each test
        for test in tests:
            test = test.strip()
            # count how may results in this test
            count = len(self.test_results[test])
            # update the max replicates
            if count > curr_max:
                curr_max = count

        return curr_max

    def build_name(self, fields):
        """Compiles a decriptive sample string based on fields from the sample
        details

        Args:
            fields (string[]): a list of fields to find in the sample details

        Returns:
            string: The compiled name string
        """

        name = ""

        for field in fields:

            field = field.strip()

            if field in self.details:
                # add a space between fields
                if len(name) > 0:
                    name += " "

                # add the sample detail to the name string
                name += self.details[field]

        return name

    def add_result(self, test_name, result):
        """Adds a result to the test_results array and if the result is a number
        it will also be added to the test_results_values array.
        Both arrays make it useful to deal with numbers and strings as results
        eg. a result might be Agree, Neither, Disagree or it might be 23.5%

        Args:
            test_name (str): The name of the test
            result (str): the results value, numbers are passed as strings
        """

        # if testname starts with a % then remove this from the string as this just indcates formatting of results
        if test_name[0] == '%':
            test_name = test_name[1:]
            self.test_units[test_name] = '%'

        # if the test already exists add it to the values array otherwise
        # create a new array under that test name
        if test_name not in self.test_results:
            self.test_results[test_name] = []

        self.test_results[test_name].append(result)

        # check if this is a number and if so store it in the values dict

        # if results are expressed as a % then remove this from the string
        if '%' in result:
            result = result.replace('%', '')
            self.test_units[test_name] = '%'

        # check string for regular expression matching a int or float
        if re.match("(\d+(?:\.\d+)?)", result) is not None:
            val = float(result)

            # add the key if it doesn't already exist
            if test_name not in self.test_results_values:
                self.test_results_values[test_name] = []

            self.test_results_values[test_name].append(val)

    def add_detail(self, name, value):
        """Adds a single sample detail

        Args:
            name (str): The name of the field
            value (str): the value
        """
        self.details[name] = value

    def result_average(self, test_name):
        """Averages the results of a single test

        Args:
            test_name (str): The name of the test

        Returns:
            double: The average result
        """
        if test_name in self.test_results_values:
            if len(self.test_results_values[test_name]) > 0:
                return statistics.mean(self.test_results_values[test_name])

        # return zero by default
        return 0

    def result_average_ordinal(self, test_name, factor_values):
        """Averages the results of a ordinal result

        Args:
            test_name (str): The name of the test
            factor_values (dict): A dictionary with the test name as the key
                and another dict as the value that has result text as key
                and the result as an integer

        Returns:
            int: The average result to the nearest int, corresponds to the factor index
        """
        if test_name in self.test_results:
            if len(self.test_results[test_name]) > 0:

                tally = 0
                for result in self.test_results[test_name]:

                    if result in factor_values[test_name]:
                        tally += factor_values[test_name].index(result)

                # round to the nearest factor
                return round(tally / len(self.test_results[test_name]))

        # return zero by default
        return 0

    def result_std(self, test_name):
        """Calculates the standard deviation of a single test

        Args:
            test_name (str): The name of the test

        Returns:
            double: The standard deviation
        """
        if test_name in self.test_results_values:
            if len(self.test_results_values[test_name]) > 1:
                return statistics.stdev(self.test_results_values[test_name])

                # return zero by default
        return 0



