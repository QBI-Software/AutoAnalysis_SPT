# -*- coding: utf-8 -*-
"""
MSD Analysis script: batchHistogramStats
Compiles histogram data from directories - expects input format:

STIM OR NOSTIM
 | -- cell1                                         <-- uses this name as column header
        | -- celldata
                 | -- Histogram_log10D.csv files    <-- this name must match (generated from histogramLogD)

and compiles to top level as STIM_AllHistogram_log10D.csv and NOSTIM_AllHistogram_log10D.csv

Analysis:
      1. Total, Mean, STD, SEM, Count per bin - appended to compiled file
      2. ?Diffs from mean per cell
Plots:
    1. Overlaid graph of each cell
    2. ?Box plots with SEM for STIM and NOSTIM

NB: SEMs not recommended - http://sportsci.org/resource/stats/meansd.html
SEM gives you an idea of the accuracy of the mean, and the SD gives you an idea of the variability of single observations
SEM = SD/(square root of sample size).
Created on Sep 8 2017

@author: Liz Cooper-Williams, QBI
"""

import argparse
from os import R_OK, access, walk, sep
from os.path import join
from glob import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class HistoStats():
    def __init__(self, inputdir, outputdir,datafile, prefix=''):
        self.inputdir = inputdir
        self.outputdir = outputdir
        if len(prefix) > 0:
            prefix = prefix + "_"
        self.compiledfile = join(outputdir,prefix + datafile)
        self.compiled = pd.DataFrame()
        self.histofile = 'Histogram_log10D.csv'

    def compile(self):
        #get list of files to compile
        if access(self.inputdir, R_OK):
            result = [y for x in walk(self.inputdir) for y in glob(join(x[0], self.histofile))]
            print(result)
            c = pd.DataFrame()
            base = self.inputdir.split(sep)
            suffixes = []
            for f in result:
                df = pd.read_csv(f)
                cell = f.split(sep)
                suffixes.append(cell[len(base)])
                if c.empty:
                    c = df
                else:
                    c = c.merge(df, how='outer', left_on='bins', right_on='bins', suffixes=suffixes)

            c.to_csv(self.compiledfile, index=False)
            print("Data compiled to " + self.compiledfile)
            self.compiled = c

    def runStats(self):
        print("Running stats")
        df = self.compiled
        df['Total_sum'] = df.apply(lambda x: (x[1:].sum()),axis=1)
        df['Total_count'] = df.apply(lambda x: (x[1:-1].count()), axis=1)
        df['Total_mean'] = df.apply(lambda x: (x[1:-2].mean()), axis=1)
        df['Total_std'] = df.apply(lambda x: (x[1:-3].std()), axis=1)
        df['Total_sem'] = df.apply(lambda x: (x.loc['Total_std']/np.sqrt(x.loc['Total_count'])), axis=1)
        df.to_csv(self.compiledfile, index=False)
        self.compiled = df

    def showPlots(self):
        print("Show plots")
        df = self.compiled
        fig, ax = plt.subplots()
        labels=[]
        for i in range(1,len(df.columns)-5):
            df.plot.line('bins',i,ax=ax)
            labels.append(df.columns[i])
        lines, _ = ax.get_legend_handles_labels()
        ax.legend(lines, labels, loc='best')
        plt.show()

#################################################################################################
if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
            Compiles histogram data from a directory (recursively looks for Histogram_log10D.csv) into an output file with stats

             ''')
    parser.add_argument('--filedir', action='store', help='Directory containing files', default="data")
    parser.add_argument('--datafile', action='store', help='Initial data file - D', default="AllHistogram_log10D.csv")
    parser.add_argument('--outputdir', action='store', help='Output directory', default="data")
    parser.add_argument('--prefix', action='store', help='Prefix for compiled file eg STIM or NOSTIM', default="")

    args = parser.parse_args()

    print("Loading Input from :", args.filedir)

    try:
        fmsd = HistoStats(args.filedir,args.outputdir,args.datafile,args.prefix)
        fmsd.compile()
        fmsd.runStats()
        fmsd.showPlots()
    except ValueError as e:
        print("Error: ", e)