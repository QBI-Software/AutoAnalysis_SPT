# -*- coding: utf-8 -*-
"""
MSD Analysis script: ratioStats
Compares ratios from compiled files
1. NOSTIM_ratios.csv and STIM_ratios.csv
2. Runs paired t-test 2 tailed (p<0.05)
3. Output ratio_stats.csv


Created on Tue Sep 5 2017

@author: Liz Cooper-Williams, QBI
"""

import argparse
from os import R_OK, access
from os.path import join

import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from os.path import join, expanduser, basename
from configobj import ConfigObj
from scipy import stats


class RatioStats():
    def __init__(self, ratio1, ratio2, prefix1=None, prefix2=None):
        """
        Load initial data
        :param ratio1: Full Filename of ratios.csv
        :param ratio2: Full Filename of ratios.csv
        :param prefix1: Prefix of file 1 - if none will try and get from underscore
        :param prefix2: Prefix of file 2 - if none will try and get from underscore
        """
        if prefix1 is not None and prefix2 is not None:
            prefixes=[prefix1,prefix2]
        else:
            prefixes = []
            for r in [ratio1,ratio2]:
                base = basename(r)
                parts = base.split('_')
                prefixes.append(parts[0])
        #Load from csv and merge
        try:
            if access(ratio1, R_OK) and access(ratio2, R_OK):
                self.data = pd.read_csv(ratio1)
                ratio2 = pd.read_csv(ratio2)
                self.data = self.data.merge(ratio2,how='outer', left_on='Cell', right_on='Cell', suffixes=prefixes)
            else:
                self.data = None

        except IOError as e:
            print('Error: Unable to read files:', e)
            raise e

    def runStats(self):
        """
         T-test on TWO RELATED samples of scores, a and b.
         This is a two-sided test for the null hypothesis that 2 related or repeated samples have identical average (expected) values.
        :return: p-value
        """
        if self.data is not None:
            print("Running t-test")
            (dstats, p) = stats.ttest_rel(self.data['RatioNOSTIM'], self.data['RatioSTIM'], nan_policy='omit')
            print("T-test\t\t\tp-value\t\t\tsignificance\n", dstats,"\t",p,'\t', p < 0.05)

############################################################################################
if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
            Generates frequency histogram from datafile to output directory

             ''')
    parser.add_argument('--file1', action='store', help='File1 with ratios', default="NOSTIM_ratios.csv")
    parser.add_argument('--file2', action='store', help='File2 with ratios', default="STIM_ratios.csv")
    parser.add_argument('--outputdir', action='store', help='Output directory (must exist)', default="data")
    args = parser.parse_args()

    try:
        rs = RatioStats(args.file1, args.file2)
        rs.runStats()
    except ValueError as e:
        print("Error: ", e)
        exit(0)