# -*- coding: utf-8 -*-
"""
MSD Analysis script: compareMSD
Compiles MSD data from directories - expects input format:

STIM OR NOSTIM
 | -- cell1                                         <-- uses this name as cell ID
        | -- celldata
                 | -- Filtered_AllROI-MSD.csv files    <-- this name must match (generated from histogramLogD)

and compiles to top level as <prefix>_AllMSD.csv where prefix can be STIM, NOSTIM (example)

Analysis per run (prefix):
      1. All cells data with Mean, SEM, Count, STD per timepoint - appended to compiled file
(Data files encoded in ISO-8859-1)


Created on Tue Sep 5 2017

@author: Liz Cooper-Williams, QBI
"""

import argparse
from os import R_OK, access, walk, sep
from os.path import join
from glob import glob
from collections import OrderedDict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class CompareMSD():
    def __init__(self, inputdir, outputdir,datafile, prefix=''):
        self.inputdir = inputdir
        self.outputdir = outputdir
        if len(prefix) > 0:
            prefix = prefix + "_"
        self.prefix = prefix
        self.compiledfile = join(outputdir,prefix + datafile)
        self.compiled = pd.DataFrame()
        self.histofile = 'Filtered_AllROI-MSD.txt'
        self.numcells = 0
        self.msdpoints = 10

    def compile(self):
        #get list of files to compile
        if access(self.inputdir, R_OK):
            #result = glob[join(self.inputdir,self.histofile)]
            result = [y for x in walk(self.inputdir) for y in glob(join(x[0], self.histofile))]
            print(result)
            self.numcells = len(result)
            base = self.inputdir.split(sep)
            timepoints = [str(x) for x in range(1,self.msdpoints + 1)]
            cols = ['Cell','Stats'] + timepoints
            data = pd.DataFrame(columns=cols)
            ctr = 0
            for f in result:
                df = pd.read_csv(f)
                #Get cellname
                cells = f.split(sep)
                cell = cells[len(base)]
                stats=OrderedDict({'avgs': [cell,'Mean'],
                       'counts': [cell,'Count'],
                       'stds':[cell,'Std'],
                       'sems':[cell,'SEM'],
                       'medians': [cell,'Median']})

                for i in timepoints:
                    stats['avgs'].append(df[i].mean())
                    stats['counts'].append(df[i].count())
                    stats['stds'].append(df[i].std())
                    stats['sems'].append(df[i].std()/np.sqrt(df[i].count()))
                    stats['medians'].append(df[i].median())

                for key in stats.keys():
                    data.loc[ctr] = stats[key]
                    ctr += 1

            #Calculate avgs of avg
            cell = 'ALL'
            stats = OrderedDict({'avgs': [cell, 'Avg_Mean'],
                                 'counts': [cell, 'Avg_Count'],
                                 'stds': [cell, 'Avg_Std'],
                                 'sems': [cell, 'Avg_SEM'],
                                 'medians': [cell, 'Avg_Median']})
            for i in timepoints:
                d = data.groupby(['Stats'])[i].mean()
                print(d)
                stats['avgs'].append(d['Mean'])
                stats['counts'].append(d['Count'])
                stats['stds'].append(d['Std'])
                stats['sems'].append(d['SEM'])
                stats['medians'].append(d['Median'])
            for key in stats.keys():
                data.loc[ctr] = stats[key]
                ctr += 1
            data.to_csv(self.compiledfile, index=False)
            print("Data compiled to " + self.compiledfile)
            self.compiled = data

    def showPlots(self,ax=None):
        if self.compiled is not None:
            df = self.compiled
            if ax is None:
                fig, ax = plt.subplots()
            means = df.groupby('Stats').get_group('Mean')
            sems = df.groupby('Stats').get_group('SEM')
            x = [str(x) for x in range(1, self.msdpoints + 1)]
            xi = [x for x in range(1, self.msdpoints + 1)]
            labels=[]
            for ctr in range(0,len(means)):
                labels.append(means['Cell'].iloc[ctr])
                plt.errorbar(xi, means[x].iloc[ctr], yerr=sems[x].iloc[ctr])

            plt.legend(labels)
            plt.title('MSDs per cell')
            #plt.show()

    def showAvgPlot(self, ax=None):
        if self.compiled is not None:
            df = self.compiled
            width = 0.15
            if ax is None:
                fig, ax = plt.subplots()
            x = [str(x) for x in range(1, self.msdpoints + 1)]
            xi = [x for x in range(1, self.msdpoints + 1)]
            all = df.groupby('Cell').get_group('ALL')
            allmeans = all.groupby('Stats').get_group('Avg_Mean')
            allsems = all.groupby('Stats').get_group('Avg_SEM')
            plt.errorbar(xi,allmeans[x].iloc[0],yerr=allsems[x].iloc[0])
            plt.title('Average MSD')
            #plt.show()

#################################################################################################
if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
            Compiles histogram data from a directory (recursively looks for Histogram_log10D.csv) into an output file with stats

             ''')
    parser.add_argument('--filedir', action='store', help='Directory containing files', default="data")
    parser.add_argument('--datafile', action='store', help='Initial data file - D', default="Avg_MSD.csv")
    parser.add_argument('--outputdir', action='store', help='Output directory', default="data")
    parser.add_argument('--prefix', action='store', help='Prefix for compiled file eg STIM or NOSTIM', default="")
    parser.add_argument('--threshold', action='store', help='Threshold between mobile and immobile', default="-1.6")
    args = parser.parse_args()

    print("Loading Input from :", args.filedir)

    try:
        fmsd = CompareMSD(args.filedir,args.outputdir,args.datafile,args.prefix)
        fmsd.compile()
        #fmsd.showPlots()
        #fmsd.showAvgPlot()
        # Set the figure
        fig = plt.figure(figsize=(10, 5))
        axes1 = plt.subplot(121)
        fmsd.showPlots(axes1)

        axes2 = plt.subplot(122)
        fmsd.showAvgPlot(axes2)

        figtype = 'png'  # png, pdf, ps, eps and svg.
        outputfile = join(args.outputdir, 'Avg_MSD.' + figtype)
        plt.savefig(outputfile, facecolor='w', edgecolor='w', format=figtype)
        plt.show()


    except ValueError as e:
        print("Error: ", e)
