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

import numpy as np
import pandas
from scipy.stats import norm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt



class FrequencyDiffusion():
    def __init__(self, minlimit, maxlimit,binwidth,datafile):
        #self.msdpoints = 10
        # holds raw or filtered data
        self.data = None
        self.fig = None
        #self.msd = None
        #Frequency range limits
        self.fmin = float(minlimit)
        self.fmax = float(maxlimit)
        self.binwidth = float(binwidth)
        self.encoding = 'ISO-8859-1'
        self.diffcolumn = 'log10D' #'D(µm²/s)' #must be exact label
        self.load_datafiles(datafile)

    def load_datafiles(self,datafile):
        self.data = pandas.read_csv(datafile,encoding = self.encoding)
        print("Data loaded:", len(self.data))
        #Allow overwrite of range?
        #self.fmin = min(self.data[self.diffcolumn])
        #self.fmax = max(self.data[self.diffcolumn])

    def getStats(self, bimodal=True):
        """
        Get stats from histogram column
        :param mean: get mean if true or median if false
        :return: mean and variance
        """
        mean = None
        variance = None
        if not self.data.empty:
            ndata = self.data[self.diffcolumn]
            if not bimodal:
                mean = np.mean(ndata)
                variance = np.var(ndata)
                print("Mean:", mean)
            else:
                #two sets
                mean = np.median(self.data[self.diffcolumn])
                print("Median:", mean)
            variance = np.var(self.data[self.diffcolumn])
            print("Variance:", variance)
        return (mean,variance)

    def gauss(self,x, mu, sigma, A):
        return A * np.exp(-(x - mu) ** 2 / 2 / sigma ** 2)

    def bimodal(self,x, mu1, sigma1, A1, mu2, sigma2, A2):
        return self.gauss(x, mu1, sigma1, A1) + self.gauss(x, mu2, sigma2, A2)

    def generateHistogram(self, outputdir=None):
        """
        Generate histogram and save to outputdir
        :param outputdir:
        :return:
        """
        if not self.data.empty:
            print("Generating histogram")
            num_bins = int((self.fmax-self.fmin)/self.binwidth) #smaller binwidth better for fitting eg 0.1 or 0.05
            data = self.data[self.diffcolumn]
            #Create figure
            self.fig = plt.figure()
            n, bins, patches = plt.hist(data, bins=num_bins,range=[self.fmin, self.fmax], align='mid',normed=1, alpha=0.75)
            #Save bins
            plt.grid(which='major')
            plt.xlabel('log10D')
            plt.ylabel('Frequency')

            bincenters = 0.5 * (bins[1:] + bins[:-1]) # OR save as bins minus first or last
            self.histdata = pandas.DataFrame({'bins': bincenters, 'log10D': n})

            #Save plot to figure
            if outputdir is not None:
                figtype='png' #png, pdf, ps, eps and svg.
                outputfile = join(outputdir,'histogram_log10D'+figtype)
                plt.savefig(outputfile, facecolor='w', edgecolor='w', format=figtype)
                print("Saved histogram to ", outputfile)
                outputfile.replace(figtype,'csv')
                self.hist.to_csv(outputfile)
                print("Saved histogram data to ", outputfile)
            plt.show()


############### MAIN ############################
if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
            Generates frequency histogram from datafile to output directory

             ''')
    parser.add_argument('--filedir', action='store', help='Directory containing files', default="data")
    parser.add_argument('--datafile', action='store', help='Initial data file', default="Filtered_AllROI-D.txt")
    parser.add_argument('--outputdir', action='store', help='Output directory (must exist)', default="data")
    parser.add_argument('--minlimit', action='store', help='Min filter', default="-5")
    parser.add_argument('--maxlimit', action='store', help='Max filter', default="1")
    parser.add_argument('--binwidth', action='store', help='Bin width', default="0.2")
    args = parser.parse_args()

    datafile = join(args.filedir, args.datafile)
    outputdir = args.outputdir
    print("Input:", datafile)

    try:
        fd = FrequencyDiffusion(args.minlimit, args.maxlimit,args.binwidth,datafile)
        fd.generateHistogram(outputdir)

    except ValueError as e:
        print("Error:", e)


