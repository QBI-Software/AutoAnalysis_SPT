# -*- coding: utf-8 -*-
"""
MSD Analysis script: ratioStats
Compares ratios from compiled files
1. NOSTIM_ratios.csv and STIM_ratios.csv
2. Runs paired t-test 2 tailed (p<0.05)
3. Output ratio_stats.csv
4. Generates comparative overlay plots for STIM vs NOSTIM
    a. Avg MSD +/- SD
    b. Avg Log10D +/- SD
    c. Mobile fraction ratios as grouped scatterplots with mean +/- SD


Created on Tue Sep 5 2017

@author: Liz Cooper-Williams, QBI
"""

import argparse
from os import R_OK, access
from os.path import basename, join, expanduser

import pandas as pd
from configobj import ConfigObj, ConfigObjError
from scipy import stats
from numpy import isnan
import seaborn as sns
import matplotlib.pyplot as plt


class MSDStats():
    def __init__(self, dir1, dir2, outputdir, prefix1=None, prefix2=None, configfile=None):
        """
        Load initial data
        :param ratio1: Full Filename of ratios.csv
        :param ratio2: Full Filename of ratios.csv
        :param prefix1: Prefix of file 1 - if none will try and get from underscore
        :param prefix2: Prefix of file 2 - if none will try and get from underscore
        """
        self.encoding = 'ISO-8859-1'
        if not access(dir1,R_OK) or not access(dir2,R_OK):
            raise IOError("Cannot access group directories")
        if configfile is not None:
            self.__loadConfig(configfile)
        else:
            self.histo = 'AllHistogram_log10D.csv'
            self.msd = 'Avg_MSD.csv'
            self.msdpoints = 10
            self.timeint = 0.02
        self.outputdir = outputdir

        if prefix1 is not None and prefix2 is not None:
            self.prefixes = [prefix1, prefix2]
        else:
            self.prefixes = ['NOSTIM', 'STIM']
        self.outputfilename = "_".join(self.prefixes) + '_stats.csv'
        self.histodata = self.__loadData(dir1, dir2, self.histo,'bins')
        self.ratiodata = self.__loadData(dir1, dir2,'ratios.csv','Cell')
        self.areadata = self.__loadData(dir1, dir2,'areas.csv','Cell')
        self.msddata = self.__loadData(dir1, dir2, self.msd, 'Cell')
        self.msddatafiles = []
        dirs = [dir1,dir2]
        self.msddatafiles = [join(dirs[i], self.prefixes[i] + "_" + self.msd) for i in [0,1]]



    def __loadConfig(self, configfile):
        """
        Universal config file - extract required fields
        :param configfile:
        :return:
        """
        try:
            if not access(configfile, R_OK):
                raise IOError("Cannot access configfile: %s" % configfile)
            config = ConfigObj(configfile, encoding=self.encoding)
            self.histo = config['ALLSTATS_FILENAME']
            self.msd = config['AVGMSD_FILENAME']
            self.msdpoints = int(config['MSD_POINTS'])
            self.timeint = float(config['TIME_INTERVAL'])
            print("MSDStats: Config file loaded")
        except ConfigObjError as c:
            raise ValueError("ERROR: config file load error: %s", configfile)

    def __loadData(self,dir1,dir2,basename, mergefield):
        """
        Find AllHistogram files for each
        :param dir1: group1 directory
        :param dir2: group2 directory
        :param basename: filename to search for +prefix
        :return:
        """
        # Load from csv and merge
        data = None
        try:
            dirs = [dir1,dir2]
            files =[]
            i = 0
            for prefix in self.prefixes:
                files.append(join(dirs[i], prefix + "_" + basename))
                i = i+1
            prefixes = ["_"+p for p in self.prefixes]
            if len(files) == 2:
                data = pd.read_csv(files[0])
                data2 = pd.read_csv(files[1])
                data = data.merge(data2, how='outer', left_on=mergefield, right_on=mergefield, suffixes=prefixes)

        except ValueError as e:
            print('Error: Unable to merge data files:', e)
            raise e

        return data



    def runTtests(self):
        """
         T-test on TWO RELATED samples of scores, a and b.
         This is a two-sided test for the null hypothesis that 2 related or repeated samples have identical average (expected) values.
        :return: dataframe
        """
        print("Running t-tests on data")
        headers = ['Compare', 'Groups','T-test', 'p-value','Significance (0.05)']
        df = pd.DataFrame(columns=headers)
        # Ratios comparison
        if self.ratiodata is not None:
            (dstats, p) = stats.ttest_rel(self.ratiodata['Ratio_' + self.prefixes[0]], self.ratiodata['Ratio_' + self.prefixes[1]], nan_policy='omit')
            #Output as CSV
            if not isnan(p):
                signif =(p >= 0.05)
            else:
                signif ='unknown'
            data = ['Ratios', " vs ".join(self.prefixes), dstats, p, signif]
            df1 = pd.DataFrame([data], columns=headers)
            df = df.append(df1)

        #Areas comparison
        if self.areadata is not None:
            # Exclude ALL row
            individareas = self.areadata[self.areadata['Cell'] != 'ALL']
            (dstats, p) = stats.ttest_rel(individareas['MSD Area_' + self.prefixes[0]], individareas['MSD Area_' + self.prefixes[1]], nan_policy='omit')
            # Output as CSV
            if not isnan(p):
                signif =(p >= 0.05)
            else:
                signif = 'unknown'
            data = ['MSD Area', " vs ".join(self.prefixes), dstats, p, signif]
            df1 = pd.DataFrame([data], columns=headers)
            df = df.append(df1)

        return df

    def showMSDAvgPlot(self,ax=None):
        """
        Overlay Avg MSD plots for each group
        :param ax:
        :return:
        """
        if ax is None:
            fig, ax = plt.subplots()
        x = [str(x) for x in range(1, self.msdpoints + 1)]
        xi = [x * self.timeint for x in range(1, self.msdpoints + 1)]  # convert to times
        for file in self.msddatafiles:
            df = pd.read_csv(file)
            all = df.groupby('Cell').get_group('ALL')
            allmeans = all.groupby('Stats').get_group('Mean')
            allsems = all.groupby('Stats').get_group('SEM')
            plt.errorbar(xi, allmeans[x].iloc[0], yerr=allsems[x].iloc[0])
        plt.title('Mean MSD with SEM')
        plt.xlabel('Time (s)')
        plt.ylabel(r'MSD ($\mu$m2/s)')
        plt.legend(self.prefixes)
        # plt.show()

    def showHistoAvgPlot(self,ax=None):
        if ax is None:
            fig, ax = plt.subplots()
        df = self.histodata
        width = 0.15
        for prefix in self.prefixes:
            meancol = 'MEAN_'+prefix
            semcol = 'SEM_' + prefix
            plt.errorbar(df['bins'], df[meancol], yerr=df[semcol], fmt='--o')
        # df['Total_mean'].plot.bar(yerr=df['Total_sem'])
        plt.xlabel('Log (D)')
        plt.ylabel('Frequency')
        plt.title('Mean D with SEM')
        plt.legend(self.prefixes)

    def showRatioPlot(self,ax=None):
        if ax is None:
            fig, ax = plt.subplots()
        df = self.ratiodata
        cols = ['Ratio_' + prefix  for prefix in self.prefixes]
        sns.swarmplot(data=df[cols])
        df.boxplot(cols)
        # df['Total_mean'].plot.bar(yerr=df['Total_sem'])
        plt.xlabel('Group')
        plt.ylabel('Mobile Fraction')
        plt.title('Mobile/Immobile Ratios')


    def showAreaPlot(self,ax=None):
        if ax is None:
            fig, ax = plt.subplots()
        df = self.areadata[self.areadata['Cell'] != 'ALL']
        cols = ['MSD Area_' + prefix  for prefix in self.prefixes]
        sns.swarmplot(data=df[cols])
        df.boxplot(cols)
        # df['Total_mean'].plot.bar(yerr=df['Total_sem'])
        plt.xlabel('Group')
        plt.ylabel('Mobile Fraction')
        plt.title('MSD Areas under curve')


    def showPlots(self, plottitle):
        """
        Generate comparative plots:
        1. Avg MSD line, points with SEM
        :return:
        """
        fig = plt.figure(figsize=(10, 10))
        fig.suptitle(plottitle)
        axes1 = plt.subplot(221)
        self.showMSDAvgPlot(axes1)

        axes2 = plt.subplot(222)
        self.showHistoAvgPlot(axes2)

        axes3 = plt.subplot(223)
        self.showRatioPlot(axes3)

        axes4 = plt.subplot(224)
        self.showAreaPlot(axes4)

        # figtype = 'png'  # png, pdf, ps, eps and svg.
        # figname = join(self.outputdir,self.outputfilename).replace('csv', figtype)
        # plt.savefig(figname, facecolor='w', edgecolor='w', format=figtype)


        plt.show()

############################################################################################
if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
            Generates frequency histogram from datafile to output directory

             ''')
    parser.add_argument('--dir1', action='store', help='Directory with group1 data', default="output")
    parser.add_argument('--dir2', action='store', help='Directory with group2 data', default="output")
    parser.add_argument('--prefix1', action='store', help='Group1', default="NOSTIM")
    parser.add_argument('--prefix2', action='store', help='Group2', default="STIM")
    parser.add_argument('--outputdir', action='store', help='Output directory (must exist)', default="output")
    parser.add_argument('--configfile', action='store', help='Configfile', default="~\.msdcfg")
    args = parser.parse_args()
    configfile = join(expanduser('~'), '.msdcfg')
    try:
        rs = MSDStats(args.dir1, args.dir2, args.outputdir, args.prefix1,args.prefix2,configfile)
        results_df = rs.runTtests()
        print(results_df)
        rs.showPlots("Test cells")

    except ValueError as e:
        print("Error: ", e)
        exit(0)
