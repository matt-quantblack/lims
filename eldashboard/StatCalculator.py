import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy import stats


def mean(list):
    if len(list) > 0:
        return sum(list) / len(list)

    return 0


def compare_anova(sample_results, comparison_sample_name, min_p=0.05):
    """ Run a anova analysis on the whole set of results and then compare
    the comparison_sample_name to each other product in the set. Creates 3 lists
    of samples that the comnparison sample is better than, no statistical difference
    to and where the sample is worse than the comparison sample

    Args:
        sample_results (DataFrame): A dataframe of the all the results, one column is
            sample name and another is result
        comparison_sample_name (str): the name of the sample to run the
            comparisons against
        min_p (float): minimum p value to be insignificant ie. 0.05 = 95% confidence level

    Returns:
        (str[], str[], str[]): Tuple of arrays, the first being the list of product names
            the comparison sample is better than, the second is the list of products
            that no statistical difference was found, the third is the list of products
            the comparison sample is worse than
    """

    mod = ols('result ~ sample', data=sample_results).fit()

    aov_table = sm.stats.anova_lm(mod, typ=2)

    anova_p = aov_table['PR(>F)'][0]

    if anova_p < min_p:
        # At least one of the sample means is statistically different

        # POST HOC Analysis - Bonferroni correction method

        # count how many samples there are which is k
        sample_names = sample_results['sample'].unique()
        k = len(sample_names)

        # calculate the bonferroni correction for alpha
        K = (k * (k - 1)) / 2
        bon_corr = min_p / K

        # data for comparison sample
        comparison_sample_data = sample_results['result'][sample_results['sample'] == comparison_sample_name]
        comparison_mean = mean(comparison_sample_data)

        better_than = []
        no_stat_diff = []
        worse_than = []

        # for each comparison run a t test to check the comparison with every other product
        for sample_name in sample_names:

            # no need to compare with itself
            if sample_name == comparison_sample_name:
                continue

            # data for this sample
            sample_data = sample_results['result'][sample_results['sample'] == sample_name]
            this_mean = mean(sample_data)

            # conduct the t-test
            res = stats.stats.ttest_ind(comparison_sample_data, sample_data)
            # this one is for paired t-test but need to setup an option in the data
            # sheet to select this instead of hardcoding
            # res = stats.stats.ttest_rel(comparison_sample_data,sample_data)
            p = res.pvalue

            # if p < bon_corr than it is stat different
            if p < bon_corr:
                if comparison_mean > this_mean:
                    better_than.append(sample_name)
                else:
                    worse_than.append(sample_name)
            else:
                no_stat_diff.append(sample_name)

        return (better_than, no_stat_diff, worse_than)

    else:
        # No statistical difference between all samples so tuple will have all
        # products in the no statistical difference array

        # get all product names that aren't the comparison product
        no_stat_diff = sample_results['sample'][sample_results['sample'] != comparison_sample_name].unique()

        # return the tupe with better than and worse than just as empty arrays
        return ([], no_stat_diff, [])

    pass