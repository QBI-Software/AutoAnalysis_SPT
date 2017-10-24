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
from os import R_OK, access
from os.path import join
import matplotlib.pyplot as plt
import numpy as np
import pandas
from configobj import ConfigObj


class HistogramLogD():
    def __init__(self, datafile, configfile=None, minlimit=-5, maxlimit=1, binwidth=0.02, ):
        self.encoding = 'ISO-8859-1'
        if configfile is not None:
            self.__loadConfig(configfile)
        else:
            self.msdpoints = 10
            self.histofile = 'Histogram_log10D.csv'
            self.logcolumn = 'log10D'  # 'D(µm²/s)' #must be exact label
            # Frequency range limits
            self.fmin = float(minlimit)
            self.fmax = float(maxlimit)
            self.binwidth = float(binwidth)

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
            except:
                raise IOError

    def __load_datafiles(self, datafile):
        self.data = pandas.read_csv(datafile, encoding=self.encoding)
        print("Data loaded:", len(self.data))
        # Allow overwrite of range?
        # self.fmin = min(self.data[self.logcolumn])
        # self.fmax = max(self.data[self.logcolumn])

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

    def generateHistogram(self, outputdir=None):
        """
        Generate histogram and save to outputdir
        :param outputdir:
        :return:
        """
        if not self.data.empty:
            print("Generating histogram")
            num_bins = abs(
                int((self.fmax - self.fmin) / self.binwidth))  # smaller binwidth better for fitting eg 0.1 or 0.05
            data = self.data[self.logcolumn]
            # Use numpy with density as more accurate - include extra bin for equal
            hist = np.histogram(data, bins=num_bins + 1, range=[int(self.fmin), int(self.fmax) + self.binwidth],
                                density=True)
            self.histdata = pandas.DataFrame({'bins': hist[1][0:-1], 'log10D': hist[0]})

            # Create figure
            self.fig = plt.figure()
            n, bins, patches = plt.hist(data, bins=hist[1][0:-1], align='mid', normed=1, alpha=0.75)
            plt.grid(which='major')
            plt.xlabel('log10D')
            plt.ylabel('Frequency')

            # Save plot to figure
            if outputdir is not None:
                figtype = 'png'  # png, pdf, ps, eps and svg.
                fname = self.histofile.replace('csv', figtype)
                outputfile = join(outputdir, fname)
                plt.savefig(outputfile, facecolor='w', edgecolor='w', format=figtype)
                print("Saved histogram to ", outputfile)
                outputfile2 = join(outputdir, self.histofile)
                self.histdata.to_csv(outputfile2, index=False)
                print("Saved histogram data to ", outputfile2)
            plt.close()
            # For testing - will stop here until fig closes
            # plt.show()
            return (outputfile, outputfile2)


############### MAIN ############################
if __name__ == "__main__":
    import sys
    import plotly
    from plotly.graph_objs import Layout, Histogram

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
            Generates frequency histogram from datafile to output directory

             ''')
    parser.add_argument('--filedir', action='store', help='Directory containing files', default="data")
    parser.add_argument('--datafile', action='store', help='Initial data file', default="Filtered_log10D.csv")
    parser.add_argument('--outputdir', action='store', help='Output directory (must exist)', default="output")
    parser.add_argument('--minlimit', action='store', help='Min filter', default="-5")
    parser.add_argument('--maxlimit', action='store', help='Max filter', default="1")
    parser.add_argument('--binwidth', action='store', help='Bin width', default="0.2")
    parser.add_argument('--config', action='store', help='Config file for parameters', default=None)
    args = parser.parse_args()

    datafile = join(args.filedir, args.datafile)
    outputdir = args.outputdir
    print("Input:", datafile)

    try:
        fd = HistogramLogD(datafile, args.config, float(args.minlimit), float(args.maxlimit), args.binwidth)
        fd.generateHistogram(outputdir)
        # Plotly Offline
        data = fd.data[fd.logcolumn]
        plotly.offline.plot({
            "data": [Histogram(x=data, xbins=dict(start=int(fd.fmin), end=int(fd.fmax), size=fd.binwidth))],
            "layout": Layout(title="Log10D histogram")
        })

    except ValueError as e:
        print("Error:", e)
