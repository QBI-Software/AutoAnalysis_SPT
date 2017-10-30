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
import logging
from os import R_OK, access
from os.path import join, splitext

#import numpy as np
from numpy import log10,nan, isnan
import pandas
from configobj import ConfigObj


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
            data = pandas.read_csv(datafile, encoding=self.encoding, skiprows=2, delimiter='\t')
            # Add log10 column
            data[self.logcolumn] = log10(data[self.diffcolumn])
            logging.info("FilterMSD: datafile loaded with log10D (%s)" % datafile)
            # Load MSD data file
            max_msdpoints = self.msdpoints + 2  # max msd points plus first 2 cols
            fpath = splitext(datafile_msd)
            if '.xls' in fpath[1]:
                msdall = pandas.read_excel(datafile_msd, sheetname=0, skiprows=1)
                allcols = ['ROI', 'Trace'] + [i for i in range(1, len(msdall.iloc[0]) - 1)]
                msdall.columns = allcols
                msd = msdall.iloc[:, 0:max_msdpoints]
            else:
                # Txt file is \t delim but has Uneven rows so need to parse line by line - detect max columns
                # This is very slow but get errors if trying read_csv with pd.read_csv(dmsd, sep='\t')
                cols = ['ROI', 'Trace'] + [str(x) for x in range(1, self.msdpoints + 1)]
                msd = pandas.DataFrame([])
                f = open(datafile_msd, encoding=self.encoding)
                f.seek(0)
                if len(f.readline().strip()) > 0:
                    for row in f.readlines():
                        if row.startswith('#'):
                            continue
                        s = pandas.Series(row.split('\t'))
                        s = s[0:max_msdpoints]  # only first 10 points
                        s1 = s.iloc[-1].split('\n')  # remove end of line if present
                        s.iloc[-1] = s1[0]
                        # padding
                        x = list(s.values) + [nan for i in range(len(s), max_msdpoints)]
                        s = pandas.Series(x)
                        msd = msd.append(s, ignore_index=True)
                    msd.columns = cols
                else:
                    msg = "Processing error: datafile maybe corrupt: %s" % datafile_msd
                    raise Exception(msg)
            logging.info("FilterMSD: msdfile loaded (%s)" % datafile_msd)
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
            msg = "Rows filtered: \tData\tMSD\t\t%d\t%d\n\t" \
                  "\t%d\t%d" % (num_data, num_msd, len(filtered), len(filtered_msd))
            print(msg)
            logging.info(msg)
            # Save files
            fdata = join(self.outputdir, self.filteredfname)
            fmsd = join(self.outputdir, self.filtered_msd)
            try:
                filtered.to_csv(fdata, columns=[logcolumn], index=False)  # with or without original index numbers
                filtered_msd.to_csv(fmsd, index=True)
                print("Files saved: ")
                print('\t', fdata, '\n\t', fmsd)
                results = (fdata, fmsd, num_data, len(filtered), num_msd, len(filtered_msd))
            except IOError as e:
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
    parser.add_argument('--datafile_msd', action='store', help='Initial data file - MSD', default="AllROI-MSD.xlsx")
    parser.add_argument('--outputdir', action='store', help='Output directory', default="data")
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
