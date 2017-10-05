# -*- coding: utf-8 -*-
"""
MSD Analysis script: batchHistogramStats
Compiles histogram data from directories - expects input format:

STIM OR NOSTIM                                      <-- USE THIS AS INPUT DIRECTORY
 | -- cell1                                         <-- uses this name as cell ID
        | -- celldata
                 | -- Histogram_log10D.csv files    <-- this name must match (generated from histogramLogD)

and compiles to top level as <prefix>_AllHistogram_log10D.csv where prefix can be STIM, NOSTIM (example) in outputdir

Analysis per run (prefix):
      1. All cells data with Mean, SEM, Count, STD, Sum per bin - appended to compiled file
      2. Immobile, Mobile, Ratio per cell

Plots:
    1. Overlaid histogram plot of each cell with threshold line
    2. Avg histogram with SEM bars
    3.

Created on Sep 8 2017

@author: Liz Cooper-Williams, QBI
"""

import argparse
from os import R_OK, access, walk, sep
from os.path import join
from glob import glob
from configobj import ConfigObj

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class HistoStats():
    def __init__(self, inputdir, outputdir,threshold, prefix='', configfile=None):
        if configfile is not None:
            self.__loadConfig(configfile)
        else:
            self.outputfile='AllHistogram_log10D.csv'
            self.histofile = 'Histogram_log10D.csv'
            self.threshold = threshold
        self.inputdir = inputdir
        self.outputdir = outputdir
        if len(prefix) > 0:
            prefix = prefix + "_"
        self.prefix = prefix
        self.compiledfile = join(outputdir,prefix + self.outputfile)
        self.compiled = pd.DataFrame()
        self.numcells = 0

    def __loadConfig(self, configfile=None):
        if configfile is not None:
            try:
                access(configfile, R_OK)
                config = ConfigObj(configfile, encoding='ISO-8859-1')
                self.histofile = config['HISTOGRAM_FILENAME']
                self.threshold = float(config['THRESHOLD'])
                self.outputfile = config['ALLSTATS_FILENAME']
            except:
                raise IOError

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
            return self.compiledfile
        else:
            return None

    def runStats(self):
        print("Running stats")
        df = self.compiled
        #Calculate stats
        n = self.numcells + 1
        df['MEAN'] = df.apply(lambda x: (x[1:n].mean()), axis=1)
        df['COUNT'] = df.apply(lambda x: (x[1:n].count()), axis=1)
        df['STD'] = df.apply(lambda x: (x[1:n].std()), axis=1)
        df['SEM'] = df.apply(lambda x: (x.loc['STD']/np.sqrt(x.loc['COUNT'])), axis=1)
        df['SUM'] = df.apply(lambda x: (x[1:n].sum()), axis=1)
        #reorder ORDER: mean,sem,count,std,sum
        cols = df.columns[0:n].tolist() +['MEAN','SEM','COUNT','STD','SUM']
        df = df.reindex_axis(cols, axis=1)
        df.to_csv(self.compiledfile, index=False)
        self.compiled = df
        return self.compiledfile


    def splitMobile(self):
        print("Split mobile and immobile fractions")
        df = self.compiled
        labels =[]
        immobile =[]
        mobile =[]
        ratiofile = None
        try:
            if type(self.threshold) != 'float':
                threshold = float(self.threshold)
            else:
                threshold = self.threshold
            for i in range(1,self.numcells + 1):
                label = df.columns[i]
                labels.append(label)
                immobile.append(df[label][df['bins'] <= threshold].sum())
                mobile.append(df[label][df['bins'] > threshold].sum())

            df_results = pd.DataFrame({'Cell': labels, 'Immobile': immobile, 'Mobile': mobile})
            df_results['Ratio'] = df_results['Mobile']/ df_results['Immobile']

            ratiofile = join(self.outputdir,self.prefix + "ratios.csv")
            df_results.to_csv(ratiofile, index=False)
            print("Output ratios:", ratiofile)

        except ValueError as e:
            print("Error:", e)
        return ratiofile


    def showPlots(self, ax=None):
        title = "Individual cells"
        df = self.compiled
        if ax is None:
            fig, ax = plt.subplots()
        labels=[]
        for i in range(1,self.numcells + 1):
            df.plot.line('bins', i, ax=ax)
            labels.append(df.columns[i])
        #plot threshold line
        if self.threshold:
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
    parser.add_argument('--outputdir', action='store', help='Output directory', default="data")
    parser.add_argument('--prefix', action='store', help='Prefix for compiled file eg STIM or NOSTIM', default="")
    parser.add_argument('--threshold', action='store', help='Threshold between mobile and immobile', default="-1.6")
    parser.add_argument('--config', action='store', help='Config file for parameters', default=None)
    args = parser.parse_args()

    print("Loading Input from :", args.filedir)

    try:
        fmsd = HistoStats(args.filedir,args.outputdir,float(args.threshold), args.prefix,args.config)
        fmsd.compile()
        fmsd.runStats()
        # Split to Mobile/immobile fractions - output
        fmsd.splitMobile()
        # Set the figure
        fig = plt.figure(figsize=(10, 5))
        axes1 = plt.subplot(121)
        fmsd.showPlots(axes1)

        axes2 = plt.subplot(122)
        fmsd.showAvgPlot(axes2)

        figtype = 'png'  # png, pdf, ps, eps and svg.
        figname = fmsd.compiledfile.replace('csv', figtype)
        plt.savefig(figname, facecolor='w', edgecolor='w', format=figtype)
        plt.show()

    except ValueError as e:
        print("Error: ", e)