# -*- coding: utf-8 -*-
"""
MSD Analysis script: compareMSD
Compiles MSD data from directories - expects input format:

STIM OR NOSTIM
 | -- cell1                                         <-- uses this name as cell ID
        | -- celldata
                 | -- Filtered_MSD.csv files    <-- this name must match (generated from histogramLogD)

and compiles to top level as <prefix>_AllMSD.csv where prefix can be STIM, NOSTIM (example)

Analysis per run (prefix):
      1. All cells data with Mean, SEM, Count, STD per timepoint - appended to compiled file
      2. Overlay MSD vs timepoints -> Calculate Area Under Curve -> add to file
      3. Plot Avg MSD with SD
(Data files encoded in ISO-8859-1)


Created on Tue Sep 5 2017

@author: Liz Cooper-Williams, QBI
"""

import argparse
from os import R_OK, access, walk, sep
from os.path import join, expanduser, commonpath, isdir
from glob import glob, iglob
from collections import OrderedDict
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
from configobj import ConfigObj

class CompareMSD():
    def __init__(self, inputfiles, outputdir,prefix, expt,configfile=None):
        self.encoding = 'ISO-8859-1'
        if configfile is not None:
            self.__loadConfig(configfile)
        else:
            self.msdcompare = 'Avg_MSD.csv'
            self.msdfile = 'Filtered_MSD.csv'
            self.msdpoints = 10
            self.timeint = 0.02
        #self.expt = expt
        #self.prefix = prefix
        self.searchtext = expt + prefix
        if not isinstance(inputfiles, list) and isdir(inputfiles):
            self.base = inputfiles.split(sep)
            self.inputfiles = self.getSelectedFiles(inputfiles, self.msdfile, self.searchtext)
        else:
            self.inputfiles = inputfiles
            self.base = commonpath(self.inputfiles) #assumes common root directory
        self.numcells = len(self.inputfiles)
        self.outputdir = outputdir

        self.compiledfile = join(outputdir, self.searchtext + "_" + self.msdcompare)
        self.compiled = pd.DataFrame()
        self.n = 1  # generating id

        # TODO: Testing Only for filenames:
        #self.msdfile = 'AllROI-D.txt'

    def __loadConfig(self, configfile=None):
        if configfile is not None:
            try:
                if access(configfile, R_OK):
                    config = ConfigObj(configfile, encoding=self.encoding)
                    self.msdfile = config['FILTERED_MSD']
                    self.msdcompare = config['AVGMSD_FILENAME']
                    self.msdpoints = int(config['MSD_POINTS'])
                    self.timeint = float(config['TIME_INTERVAL'])
                    print("MSD: Config file loaded")
                else:
                    raise IOError("Cannot access Config file")
            except:
                raise IOError("Cannot load Config file")

    def deduplicate(self,itemlist):
        """
        Checks for duplicated column names and appends a number
        :param itemlist:
        :return:
        """
        u, indices = np.unique(itemlist, return_index=True)
        duplicates = [x for x in range(0, len(itemlist)) if x not in indices]
        i=0
        for d in duplicates:
            itemlist[d] = itemlist[d] + "_" + str(i)
            i = i + 1

        return itemlist

    def getSelectedFiles(self,inputdir, datafile, searchtext=None):
        # get list of files to compile
        allfiles = []
        if access(inputdir, R_OK):
            allfiles = [y for y in iglob(join(inputdir, '**', datafile), recursive=True)]
            print("Files Found: ", len(allfiles))
            if len(allfiles) > 0:
                # Filter on searchtext
                if searchtext is not None:
                    allfiles = [f for f in allfiles if re.search(searchtext, f, flags=re.IGNORECASE)]
                    if len(allfiles) == 0:
                        msg = "No matching files found: %s" % searchtext
                        raise IOError(msg)
            else:
                msg = "No files found"
                raise IOError(msg)
        else:
            msg = "ERROR: Unable to access inputdir: %s" % inputdir
            raise IOError(msg)
        return allfiles

    def generateID(self,f):
        # Generate unique cell ID
        cells = f.split(sep)
        base = self.base.split(sep)
        if len(base) > 4:
            cell = "_".join(cells[len(self.base):len(self.base) + 3])
        else:
            cellid = 'c{0:03d}'.format(self.n)
            cell = "_".join([self.searchtext, cellid])
            self.n += 1
        return cell

    def compile(self):
        try:
            # Compile all selected files
            timepoints = [str(x) for x in range(1,self.msdpoints + 1)]
            cols = ['Cell','Stats'] + timepoints
            data = pd.DataFrame(columns=cols, dtype=float)
            ctr = 0
            # TODO: Test with dummy file
            #f0 = 'D:\\Data\\msddata\\170801\\170801ProteinCelltype\\NOSTIM\\CELL1\\data\\processed\\Filtered_MSD.csv'
            base = self.base.split(sep)
            n = 1
            for f in self.inputfiles:
                df = pd.read_csv(f)
                cell = self.generateID()
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
            # stats = OrderedDict({'avgs': [cell, 'Avg_Mean'],
            #                      'counts': [cell, 'Avg_Count'],
            #                      'stds': [cell, 'Avg_Std'],
            #                      'sems': [cell, 'Avg_SEM'],
            #                      'medians': [cell, 'Avg_Median']})
            stats = OrderedDict({'avgs': [cell, 'Mean'],
                                 'counts': [cell, 'Count'],
                                 'stds': [cell, 'Std'],
                                 'sems': [cell, 'SEM'],
                                 'medians': [cell, 'Median']})
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

            #Sort by Stats
            df1 = data.sort_values(by=['Stats', 'Cell'])
            self.compiled = df1
            #Write to CSV
            df1.to_csv(self.compiledfile, index=False)
            print("Data compiled to " + self.compiledfile)

        except IOError as e:
            raise e
        return self.compiledfile



    def showPlotsWithAreas(self,ax=None):
        """
        Plots each cells MSD, calculates areas and saves to areas file
        :param ax:
        :return: areas
        """
        if self.compiled is not None:
            df = self.compiled
            if ax is None:
                fig, ax = plt.subplots()
            means = df.groupby('Stats').get_group('Mean')
            sems = df.groupby('Stats').get_group('SEM')
            x = [str(x) for x in range(1, self.msdpoints + 1)]
            xi = [x * self.timeint for x in range(1, self.msdpoints + 1)]
            labels=[]
            areas = []
            for ctr in range(0,len(means)):
                labels.append(means['Cell'].iloc[ctr])
                plt.errorbar(xi, means[x].iloc[ctr], yerr=sems[x].iloc[ctr])
                areas.append(np.trapz(means[x].iloc[ctr], dx=self.timeint))

            plt.legend(labels)
            plt.xlabel('Time (s)')
            plt.ylabel(r'MSD ($\mu$m2/s)')
            plt.title(self.searchtext.upper() + ' MSDs per cell')
            #plt.show()
            #save areas to new file
            df_area = pd.DataFrame({'Cell':labels, 'MSD Area': areas}, columns=['Cell','MSD Area'])
            areasfile = join(self.outputdir, self.searchtext + "_areas.csv")
            df_area.to_csv(areasfile, index=False)
            print('Areas output to', areasfile)
            return areasfile


    def showAvgPlot(self, ax=None):
        if self.compiled is not None:
            df = self.compiled
            width = 0.15
            if ax is None:
                fig, ax = plt.subplots()
            x = [str(x) for x in range(1, self.msdpoints + 1)]
            xi = [x * self.timeint for x in range(1, self.msdpoints + 1)] #convert to times
            all = df.groupby('Cell').get_group('ALL')
            allmeans = all.groupby('Stats').get_group('Mean')
            allsems = all.groupby('Stats').get_group('SEM')
            plt.errorbar(xi,allmeans[x].iloc[0],yerr=allsems[x].iloc[0])
            plt.title(self.searchtext.upper() + ' Average MSD')
            plt.xlabel('Time (s)')
            plt.ylabel(r'MSD ($\mu$m2/s)')
            #plt.show()

#################################################################################################
if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
            Compiles histogram data from a directory (recursively looks for Filtered_MSD.csv) into an output file with stats

             ''')
    parser.add_argument('--filedir', action='store', help='Directory containing files', default="data")
    parser.add_argument('--outputdir', action='store', help='Output directory', default="data")
    parser.add_argument('--prefix', action='store', help='Prefix for compiled file eg STIM or NOSTIM', default="")
    parser.add_argument('--expt', action='store', help='ProteinCelltype as shown on directory names', default="ProteinCelltype")
    parser.add_argument('--config', action='store', help='Config file for parameters', default=None)
    args = parser.parse_args()

    print("Loading Input from :", args.filedir)

    try:
        fmsd = CompareMSD(args.filedir,args.outputdir,args.prefix,args.expt,args.config)
        fmsd.compile()

        # Set the figure
        fig = plt.figure(figsize=(10, 5))
        axes1 = plt.subplot(121)
        fmsd.showPlotsWithAreas(axes1)

        axes2 = plt.subplot(122)
        fmsd.showAvgPlot(axes2)

        figtype = 'png'  # png, pdf, ps, eps and svg.
        figname = fmsd.compiledfile.replace('csv', figtype)
        plt.savefig(figname, facecolor='w', edgecolor='w', format=figtype)
        plt.show()

    except IOError as e:
        print("IOError: ", e)
    except ValueError as e:
        print("Error: ", e)

