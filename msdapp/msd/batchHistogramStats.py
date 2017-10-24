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
from os.path import join

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from msdapp.msd.batchStats import BatchStats


class HistoStats(BatchStats):
    def __init__(self, *args):
        super().__init__(*args)
        if self.config is not None:
            self.datafile = self.config['HISTOGRAM_FILENAME']
            self.threshold = float(self.config['THRESHOLD'])
            self.outputfile = self.config['ALLSTATS_FILENAME']
            print("HIST: Config file loaded")
        else:  # defaults
            self.outputfile = 'AllHistogram_log10D.csv'
            self.datafile = 'Histogram_log10D.csv'
            self.threshold = -1.6
            print("HIST:Using config defaults")
        self.compiledfile = join(self.outputdir, self.searchtext + "_" + self.outputfile)
        self.compiled = pd.DataFrame()

    def compile(self):
        try:
            # Compile all selected files
            print("Compiling %d files" % self.numcells)
            c = pd.DataFrame()
            # base = self.base.split(sep)
            suffixes = ['bins']
            # TODO: Test with dummy file
            # f0 = 'D:\\Data\\msddata\\170801\\170801ProteinCelltype\\NOSTIM\\CELL1\\data\\processed\\Histogram_log10D.csv'
            # D:\data\msddata\NOSTIM\CELL1\data
            for f in self.inputfiles:
                df = pd.read_csv(f)
                cell = self.generateID(f)
                suffixes.append(cell)
                if c.empty:
                    c = df
                else:
                    try:
                        # c = c.merge(df, how='outer', left_on='bins', right_on='bins', suffixes=suffixes)
                        c = pd.concat([c, df.iloc[:, 1:]], axis=1)
                    except ValueError as e:
                        print(e)
                        raise Exception(e)
            if not c.empty:
                suffixes = self.deduplicate(suffixes)
                # newcols = [c.replace('log10D','') for c in c.columns.tolist()]
                c.columns = suffixes  # newcols
                c.to_csv(self.compiledfile, index=False)
                print("Data compiled to " + self.compiledfile)
                self.compiled = c
                return self.compiledfile
            else:
                return None
        except Exception as e:
            msg = "Error: in BatchHisto compile process - %s" % e
            raise IOError(msg)

    def runStats(self):
        print("Running stats")
        df = self.compiled
        # Calculate stats
        n = self.numcells + 1
        df['MEAN'] = df.apply(lambda x: (x[1:n].mean()), axis=1)
        df['COUNT'] = df.apply(lambda x: (x[1:n].count()), axis=1)
        df['STD'] = df.apply(lambda x: (x[1:n].std()), axis=1)
        df['SEM'] = df.apply(lambda x: (x.loc['STD'] / np.sqrt(x.loc['COUNT'])), axis=1)
        df['SUM'] = df.apply(lambda x: (x[1:n].sum()), axis=1)
        # reorder ORDER: mean,sem,count,std,sum
        cols = df.columns[0:n].tolist() + ['MEAN', 'SEM', 'COUNT', 'STD', 'SUM']
        df = df.reindex_axis(cols, axis=1)
        df.to_csv(self.compiledfile, index=False)
        self.compiled = df
        return self.compiledfile

    def splitMobile(self):
        print("Split mobile and immobile fractions")
        df = self.compiled
        n = len(df.columns)
        labels = df.columns[1:n - 5].tolist()
        immobile = []
        mobile = []
        ratiofile = None
        try:
            threshold = float(self.threshold)

            for label in labels:
                immobile.append(df[label][df['bins'] <= threshold].sum())
                mobile.append(df[label][df['bins'] > threshold].sum())

            df_results = pd.DataFrame({'Cell': labels, 'Immobile': immobile, 'Mobile': mobile})
            df_results['Ratio'] = df_results['Mobile'] / df_results['Immobile']

            ratiofile = join(self.outputdir, self.searchtext + "_ratios.csv")
            df_results.to_csv(ratiofile, index=False)
            print("Output ratios:", ratiofile)

        except ValueError as e:
            print("Error:", e)
            raise e
        return ratiofile

    def showPlots(self, ax=None):
        df = self.compiled
        if ax is None:
            fig, ax = plt.subplots()
        labels = []
        for i in range(1, self.numcells + 1):
            df.plot.line('bins', i, ax=ax)
            labels.append(df.columns[i])
        # plot threshold line
        if self.threshold:
            plt.axvline(x=self.threshold, color='r', linestyle='-', linewidth=0.5)
        lines, _ = ax.get_legend_handles_labels()
        ax.legend(lines, labels, loc=2, fontsize='xx-small')
        plt.title(self.searchtext.upper() + " " + "Individual cells")
        plt.xlabel('Log10(D)')
        plt.ylabel(r'Frequency distribution (fractions)')

    def showAvgPlot(self, ax=None):
        print("Show average plots for treatments")
        df = self.compiled
        width = 0.15
        if ax is None:
            fig, ax = plt.subplots()
        plt.errorbar(df['bins'], df['MEAN'], yerr=df['SEM'], fmt='--o')
        # df['Total_mean'].plot.bar(yerr=df['Total_sem'])
        plt.xlabel('Log10(D)')
        plt.title(self.searchtext.upper() + " " + 'Average with SEM')


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
    parser.add_argument('--expt', action='store', help='ProteinCelltype as shown on directory names',
                        default="ProteinCelltype")
    parser.add_argument('--config', action='store', help='Config file for parameters', default=None)
    args = parser.parse_args()

    print("Loading Input from :", args.filedir)

    try:
        fmsd = HistoStats(args.filedir, args.outputdir, args.prefix, args.expt, args.config)
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
