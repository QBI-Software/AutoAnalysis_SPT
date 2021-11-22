# -*- coding: utf-8 -*-
"""
MSD Analysis script: frequencyDiffusion
Create frequency histogram data from
1. Filtered_AllROI-D.txt - #Diffusion Coefficient in um^2/s
for individual cells and all cells

(Data files encoded in ISO-8859-1)


Created on Tue Sep 5 2017

@author: Liz Cooper-Williams, QBI
"""

import argparse
import logging
from os import R_OK, access, remove
from os.path import join, split
# #maintain this order of matplotlib
# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
# plt.style.use('seaborn-paper')
import numpy as np
# from numpy import nan, isnan, mean, median, var, std, exp, histogram,linspace
import pandas
import seaborn as sns
from configobj import ConfigObj
from plotly import offline
from plotly.graph_objs import Layout, Histogram


class HistogramLogD():
    def __init__(self, datafile, configfile=None, showplots=False):
        self.encoding = 'ISO-8859-1'
        self.showplots = showplots
        parts = split(datafile)
        self.datafile = parts[1]
        self.inputdir = parts[0]
        self.cellid = datafile #.replace(sep,"_")
        if configfile is not None:
            self.__loadConfig(configfile)
        else:
            self.msdpoints = 10
            self.histofile = 'Histogram_log10D.csv'
            self.logcolumn = 'log10D'  # must be exact label
            # Frequency range limits
            self.fmin = -5.0
            self.fmax = 1.0
            self.binwidth = 0.2

        # holds raw or filtered data
        self.data = None
        self.fig = None

        # Load data
        self.__load_datafiles(datafile)

    def __loadConfig(self, configfile=None):
        if configfile is not None:

            try:
                access(configfile, R_OK)
                config = ConfigObj(configfile, encoding=self.encoding)
                self.histofile = config['HISTOGRAM_FILENAME']
                self.fmin = float(config['MINLIMIT'])
                self.fmax = float(config['MAXLIMIT'])
                self.binwidth = float(config['BINWIDTH'])
                self.logcolumn = config['LOG_COLUMN']
                if 'ENCODING' in config:
                    self.encoding = config['ENCODING']
            except:
                raise IOError

    def __load_datafiles(self, datafile):
        self.data = pandas.read_csv(datafile, encoding=self.encoding)
        print("Histogram: Data loaded:", len(self.data))

    def getStats(self, bimodal=True):
        """
        Get stats from histogram column
        :param mean: get mean if true or median if false
        :return: mean and variance
        """
        mean = None
        variance = None
        if not self.data.empty:
            ndata = self.data[self.logcolumn]
            if not bimodal:
                mean = np.mean(ndata)
                variance = np.var(ndata)
                print("Mean:", mean)
            else:
                # two sets
                mean = np.median(self.data[self.logcolumn])
                print("Median:", mean)
            variance = np.var(self.data[self.logcolumn])
            print("Variance:", variance)
        return (mean, variance)

    def gauss(self, x, mu, sigma, A):
        return A * np.exp(-(x - mu) ** 2 / 2 / sigma ** 2)

    def bimodal(self, x, mu1, sigma1, A1, mu2, sigma2, A2):
        return self.gauss(x, mu1, sigma1, A1) + self.gauss(x, mu2, sigma2, A2)

    def generateHistogram(self, freq=0,outputdir=None):
        """
        Generate histogram and save to outputdir
        :param outputdir: where to save csv and png files to
        :param freq: 0=relative freq, 1=density, 2=cumulative
        :return:
        """
        if not self.data.empty:
            print("Generating histogram")
            if outputdir is None:
                outputdir = self.inputdir
            data = self.data[self.logcolumn]
            # Require centre-bins to match with Graphpad Prism histogram but numpy uses bin-edges
            # Generate bins around centers
            xmin = self.fmin - (self.binwidth / 2)
            xmax = self.fmax + (self.binwidth / 2)
            n_bins = int(abs((self.fmax - self.fmin) / self.binwidth)) + 1
            # Generate histogram counts
            n, bins = np.histogram(data, bins=n_bins, range=(xmin, xmax))
            # h = histogram(A,edges,'Normalization','pdf') - PDF normalization gives total=1
            sum_n = sum(n)
            area_n = sum(n*self.binwidth)
            # Relabel bins as centres
            centrebins = np.linspace(self.fmin, self.fmax, n_bins)
            n_norm = n / sum_n
            self.histdata = pandas.DataFrame({'bins': centrebins, self.logcolumn: n_norm})
            outputfile = join(outputdir, self.histofile)
            self.histdata.to_csv(outputfile, index=False)
            print("Saved histogram data to ", outputfile)
            figtype = 'png'  # png, pdf, ps, eps and svg.
            figfile = outputfile.replace('csv', figtype)
            try:
                # Create figure - causes Runtime errors in Thread
                self.fig = plt.figure()
                #plt.figure()
                # Seaborn fig
                sns.set_style("whitegrid")
                sns.set_context("paper")
                # sns.set(color_codes=True)
                ylabel = 'Relative frequency'
                ax = sns.barplot(centrebins, n_norm)
                plt.xlabel(self.logcolumn)
                plt.ylabel(ylabel)
                plt.title(self.cellid)

                # Save plot to figure

                plt.savefig(figfile, facecolor='w', edgecolor='w', format=figtype)
                print("Saved histogram to ", figfile)

                # will stop here until fig is manually closed
                if self.showplots:
                    plt.show()
                else:
                    plt.close()
            except RuntimeError as e:
                msg = 'Unable to Create plots due to Matplotlib runtime errors'
                print(msg)
                logging.warning(msg)
                #remove previous fig if exists - otherwise inconsistent
                if access(figfile,R_OK):
                    remove(figfile)
                    logging.warning("File deleted: " + figfile)


            return (outputfile, figfile)

    def showPlotlyhistogram(self):
        # Plotly Offline
        data = fd.data[fd.logcolumn]
        offline.plot({
            "data": [Histogram(x=data, xbins=dict(start=int(fd.fmin), end=int(fd.fmax), size=fd.binwidth))],
            "layout": Layout(title="Log10(D) histogram for " + self.cellid)
        })

############### MAIN ############################
if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
            Generates frequency histogram from datafile to output directory

             ''')
    parser.add_argument('--filedir', action='store', help='Directory containing files', default="..\\..\\data")
    parser.add_argument('--datafile', action='store', help='Initial data file', default="Filtered_log10D.csv")
    parser.add_argument('--outputdir', action='store', help='Output directory (must exist)', default="..\\..\\data")
    parser.add_argument('--config', action='store', help='Config file for parameters', default=None)
    parser.add_argument('--showplots', action='store_true',help='Display popup plots', default=True)
    args = parser.parse_args()

    datafile = join(args.filedir, args.datafile)
    outputdir = args.outputdir
    print("Input:", datafile)

    try:
        fd = HistogramLogD(datafile, args.config, args.showplots)
        fd.generateHistogram(freq=0,outputdir=outputdir)
        #density
        fd.generateHistogram(freq=1,outputdir=outputdir)
        #cumulative
        fd.generateHistogram(freq=2,outputdir=outputdir)
        fd.showPlotlyhistogram()

    except ValueError as e:
        print("Error:", e)
