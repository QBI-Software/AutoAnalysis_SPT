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
        self.prefix = prefix
        self.compiledfile = join(outputdir,prefix + datafile)
        self.compiled = pd.DataFrame()
        self.histofile = 'Histogram_log10D.csv'
        self.numcells = 0

    def compile(self):
        #get list of files to compile
        if access(self.inputdir, R_OK):
            result = [y for x in walk(self.inputdir) for y in glob(join(x[0], self.histofile))]
            print(result)
            c = pd.DataFrame()
            base = self.inputdir.split(sep)
            suffixes = []
            self.numcells = len(result)
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
        #ORDER: mean,sem,count,std,sum
        df['SUM'] = df.apply(lambda x: (x[1:].sum()),axis=1)
        df['COUNT'] = df.apply(lambda x: (x[1:-1].count()), axis=1)
        df['MEAN'] = df.apply(lambda x: (x[1:-2].mean()), axis=1)
        df['STD'] = df.apply(lambda x: (x[1:-3].std()), axis=1)
        df['SEM'] = df.apply(lambda x: (x.loc['STD']/np.sqrt(x.loc['COUNT'])), axis=1)
        df.to_csv(self.compiledfile, index=False)
        self.compiled = df

    def splitMobile(self, threshold):
        print("Split mobile and immobile fractions")
        df = self.compiled
        labels =[]
        immobile =[]
        mobile =[]
        ratio = []
        try:
            if type(threshold) != 'float':
                threshold = float(threshold)
            for i in range(1,self.numcells + 1):
                label = df.columns[i]
                labels.append(label)
                immobile.append(df[label][df['bins'] <= threshold].sum())
                mobile.append(df[label][df['bins'] > threshold].sum())

            df_results = pd.DataFrame({'Cell': labels, 'Immobile': immobile, 'Mobile': mobile})
            df_results['Ratio'] = df_results['Immobile']/ df_results['Mobile']
            ratiofile = join(self.outputdir,self.prefix + "_ratios.csv")
            df_results.to_csv(ratiofile)
            print("Output ratios:", ratiofile)

        except ValueError as e:
            print("Error:", e)


    def showPlots(self, ax=None,threshold=False):
        title = "Individual cells"
        df = self.compiled
        if ax is None:
            fig, ax = plt.subplots()
        labels=[]
        for i in range(1,len(df.columns)-5):
            df.plot.line('bins', i, ax=ax)
            labels.append(df.columns[i])
        #plot threshold line
        if threshold:
            plt.axvline(x=-1.6, color='r', linestyle='-', linewidth=0.5)
        lines, _ = ax.get_legend_handles_labels()
        ax.legend(lines, labels, loc='best')
        plt.title(title)


    def showAvgPlot(self, ax=None):
        print("Show average plots for treatments")
        df = self.compiled
        width=0.15
        if ax is None:
            fig, ax = plt.subplots()
        plt.bar(df['bins'],df['MEAN'],yerr=df['SEM'], width=width)
        #df['Total_mean'].plot.bar(yerr=df['Total_sem'])
        plt.xlabel('bins')
        plt.title('Average with SEM')


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
    parser.add_argument('--threshold', action='store', help='Threshold between mobile and immobile', default="-1.6")
    args = parser.parse_args()

    print("Loading Input from :", args.filedir)

    try:
        fmsd = HistoStats(args.filedir,args.outputdir,args.datafile,args.prefix)
        fmsd.compile()
        fmsd.runStats()
        # Split to Mobile/immobile fractions - output
        fmsd.splitMobile(float(args.threshold))
        # Set the figure
        #fig = plt.figure(figsize=(10, 5))
        #axes1 = plt.subplot(121)
        #fmsd.showPlots(axes1,False)

        #axes2 = plt.subplot(122)
        #fmsd.showAvgPlot(axes2)
        #plt.show()


    except ValueError as e:
        print("Error: ", e)