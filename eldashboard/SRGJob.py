import pandas as pd


class SRGJob:

    def __init__(self):
        self.samples = []
        self.fields = {}

    def add_sample(self, sample):
        self.samples.append(sample)

    def get_all_results(self, key_fields, test_name):
        """ Gets all the result values from each product and compiles it into
        a table. One column is the sample name and another column is the test
        value. Useful dataframe for doing statistical anaylsis

        Args:
            key_fields: the fields in the samples details to use to build the
                sample name. Used as the keys in the dictionary
            test_name: the name of the test to get the values for

        Returns:
            DataFrame: a dataframe with all the test result values for every sample
        """

        all_results = pd.DataFrame(columns=['sample', 'result'])

        for sample in self.samples:

            if test_name in sample.test_results_values:
                sample_name = sample.build_name(key_fields)

                for value in sample.test_results_values[test_name]:
                    all_results = all_results.append({'sample': sample_name,
                                                      'result': value}, ignore_index=True)

        # make sure the results are interpreted as numeric
        all_results['result'] = pd.to_numeric(all_results['result'])

        return all_results
