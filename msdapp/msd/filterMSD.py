# -*- coding: utf-8 -*-
"""
MSD Analysis script: filterMSD
Filters data from
1. AllROI-D.txt - #Diffusion Coefficient in um^2/s; Linear fit performed on the 4 first points of trajectories > 8 points
2. AllROI-MSD.txt #MSD(DeltaT) in um^2
(Data files encoded in ISO-8859-1)


Created on Tue Sep 5 2017

@author: Liz Cooper-Williams, QBI
"""

import argparse
import csv
import logging
from collections import OrderedDict
from os import R_OK, access, mkdir
from os.path import join, splitext, exists

import pandas as pd
from configobj import ConfigObj
# import numpy as np
from numpy import log10


class FilterMSD():
    def __init__(self, configfile, datafile, datafile_msd, outputdir, minlimit=-5.0, maxlimit=1.0):
        self.encoding = 'ISO-8859-1'
        if configfile is not None:
            self.__loadConfig(configfile)
        else:
            self.msdpoints = 10
            self.diffcolumn = 'D(µm²/s)'
            self.logcolumn = 'log10D'
            self.filteredfname = 'Filtered_log10D.csv'
            self.filtered_msd = 'Filtered_MSD.csv'
            self.minlimit = float(minlimit)
            self.maxlimit = float(maxlimit)
            self.roi = 0
            # Load data
        self.outputdir = outputdir
        print("FilterMSD: Loading data ...")
        (self.data, self.msd) = self.load_datafiles(datafile, datafile_msd)
        if self.data is None:
            raise ValueError("Processing error")
        else:
            print("...loaded")

    def __loadConfig(self, configfile=None):
        if configfile is not None:
            try:
                access(configfile, R_OK)
                config = ConfigObj(configfile)
            except:
                # Chars work differently for diff OSes
                print("Encoding required for Config")
                config = ConfigObj(configfile, encoding=self.encoding)
            self.filteredfname = config['FILTERED_FILENAME']
            self.filtered_msd = config['FILTERED_MSD']
            self.diffcolumn = config['DIFF_COLUMN']
            self.logcolumn = config['LOG_COLUMN']
            self.msdpoints = int(config['MSD_POINTS'])
            self.minlimit = float(config['MINLIMIT'])
            self.maxlimit = float(config['MAXLIMIT'])
            self.roi = int(config['GROUPBY_ROI'])
            if 'ENCODING' in config:
                self.encoding = config['ENCODING']

    def load_datafiles(self, datafile, datafile_msd):
        """
        Load text datafiles as csv into dataframes
        MSD file has uneven rows - but only require first 10 points
        :param datafile:
        :param datafile_msd:
        :return:
        """
        try:
            data = None
            msd = None
            # Load Data file
            data = pd.read_csv(datafile, encoding=self.encoding, skiprows=2, delimiter='\t')
            # Add log10 column
            data[self.logcolumn] = log10(data[self.diffcolumn])
            logging.info("FilterMSD: datafile loaded with log10D (%s)" % datafile)
            # Load MSD data file
            max_msdpoints = self.msdpoints + 2  # max msd points plus first 2 cols
            fpath = splitext(datafile_msd)
            if '.xls' in fpath[1]:
                msdall = pd.read_excel(datafile_msd, sheetname=0, skiprows=1)
                allcols = ['ROI', 'Trace'] + [i for i in range(1, len(msdall.iloc[0]) - 1)]
                msdall.columns = allcols
                msd = msdall.iloc[:, 0:max_msdpoints]
            else:
                # Txt file is \t delim but has Uneven rows so need to parse line by line - detect max columns
                # This is very slow but get errors if trying read_csv with pd.read_csv(dmsd, sep='\t')
                cols = ['ROI', 'Trace'] + [str(x) for x in range(1, self.msdpoints + 1)]
                msddata = OrderedDict()
                for c in cols:
                    msddata[c] = []

                with open(datafile_msd, encoding=self.encoding) as f:
                    reader = csv.reader(f, delimiter="\t")
                    d = list(reader)
                    print("FilterMSD: MSD file Lines=", len(d))
                    print(d[0][0])
                    if not (d[0][0].startswith('#MSD')):
                        msg = "Processing error: datafile maybe corrupt: %s" % datafile_msd
                        raise Exception(msg)
                    for row in d:
                        if row[0].startswith('#') or len(row[0]) <= 0:
                            continue
                        msddata['ROI'].append(row[0])
                        msddata['Trace'].append(row[1])
                        for i in range(2, max_msdpoints):
                            if len(row) > i:
                                msddata[str(i - 1)].append(row[i])
                            else:
                                msddata[str(i - 1)].append('')

                msd = pd.DataFrame.from_dict(msddata)
            msg = "FilterMSD: msdfile load(%s)" % datafile_msd
            if msd.empty:
                msg = "Load failed: " + msg
                raise Exception(msg)
            else:
                logging.info(msg)
            return (data, msd)
        except Exception as e:
            print(e)
            logging.error(e)

    def runFilter(self):
        """
        Run filter over datasets and save to file
        :return:
        """
        results = None
        if not self.data.empty:
            # print(data)
            logcolumn = self.logcolumn
            num_data = len(self.data)
            num_msd = len(self.msd)
            (filtered, filtered_msd) = self.filter_datafiles()
            msg = "Rows filtered: \tData=%d of %d\tMSD=%d of %d\n" % (len(filtered), num_data, len(filtered_msd), num_msd)
            print(msg)
            logging.info(msg)
            # Save files  if GroupbyROI - save to subdirectories
            try:

                if self.roi:
                    print('ROI config is ON:',self.roi)
                    roilist = filtered.groupby('ROI')
                    msdlist = filtered_msd.groupby('ROI')
                    results=0
                    for g in roilist.groups:
                        df = roilist.get_group(g)
                        if g in msdlist.groups.keys():
                            dm = msdlist.get_group(g)
                        elif str(g) in msdlist.groups.keys():
                            dm = msdlist.get_group(str(g))
                        elif ' '+str(g) in msdlist.groups.keys():
                            dm = msdlist.get_group(' '+str(g))
                        else:
                            raise ValueError('Cannot group MSD file - check if has ROIs')

                        sdir = join(self.outputdir,'ROI_' + str(g))
                        if not exists(sdir):
                            mkdir(sdir)
                        fdata = join(sdir,self.filteredfname)
                        fmsd = join(sdir, self.filtered_msd)
                        df.to_csv(fdata, columns=[logcolumn], index=False)  # with or without original index numbers
                        dm.to_csv(fmsd, index=True)
                        msg ="ROI Files saved: \n\t%s\n\t%s" % (fdata,fmsd)
                        logging.info(msg)
                        print(msg)
                        results += 1
                else:
                    fdata = join(self.outputdir, self.filteredfname)
                    fmsd = join(self.outputdir, self.filtered_msd)
                    print('saving files')
                    filtered.to_csv(fdata, columns=[logcolumn], index=False)  # with or without original index numbers
                    filtered_msd.to_csv(fmsd, index=True)
                    print("Files saved: ")
                    print('\t', fdata, '\n\t', fmsd)
                    results = (fdata, fmsd, num_data, len(filtered), num_msd, len(filtered_msd))
            except IOError as e:
                logging.error(e)
                raise e

        else:
            raise ValueError("Data not loaded")
        return results

    def filter_datafiles(self):
        """
        Filter field with minval and maxval

        :return: filtered dataframes for data and msd
        """
        data = self.data
        msd = self.msd
        logcolumn = self.logcolumn
        minval = self.minlimit
        maxval = self.maxlimit
        minfilter = data[logcolumn] > minval
        maxfilter = data[logcolumn] < maxval
        mmfilter = minfilter & maxfilter
        filtered = data[mmfilter]
        filtered_msd = msd[mmfilter]
        self.data = filtered
        self.msd = filtered_msd
        return (filtered, filtered_msd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='filterMSD',
                                     description='''\
            Reads data files from a directory and filters into an output file

             ''')
    parser.add_argument('--filedir', action='store', help='Directory containing files', default="data")
    parser.add_argument('--datafile', action='store', help='Initial data file - D', default="AllROI-D.txt")
    parser.add_argument('--datafile_msd', action='store', help='Initial data file - MSD', default="AllROI-MSD.txt")
    parser.add_argument('--outputdir', action='store', help='Output directory', default="..\\..\\data")
    parser.add_argument('--minlimit', action='store', help='Min filter', default="-5")
    parser.add_argument('--maxlimit', action='store', help='Max filter', default="1")
    parser.add_argument('--config', action='store', help='Config file for parameters', default=None)
    args = parser.parse_args()

    datafile = join(args.filedir, args.datafile)
    datafile_msd = join(args.filedir, args.datafile_msd)
    outputdir = args.outputdir
    print("Input:", datafile)

    try:
        fmsd = FilterMSD(args.config, datafile, datafile_msd, outputdir, float(args.minlimit), float(args.maxlimit))
        if fmsd.data is not None:
            fmsd.runFilter()

    except ValueError as e:
        print("Error: ", e)

    except OSError as e:
        if access(datafile, R_OK):
            print('Unknown file error:', e)
        else:
            print("Cannot access file or directory: ", e)
