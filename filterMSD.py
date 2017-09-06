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
from os import R_OK, access
from os.path import join

import numpy as np
import pandas


class FilterMSD():
    def __init__(self):
        self.msdpoints = 10
        # holds raw or filtered data
        self.data = None
        self.msd = None
        self.encoding = 'ISO-8859-1'
        self.diffcolumn = 'D(µm²/s)'
        self.field = 'log10D'

    def load_datafiles(self, datafile, datafile_msd):
        """
        Load text datafiles as csv into dataframes
        MSD file has uneven rows - but only require first 10 points
        :param datafile:
        :param datafile_msd:
        :return:
        """
        data = pandas.read_csv(datafile, encoding=self.encoding, skiprows=2, delimiter='\t')
        # Uneven rows - detect max columns
        max_msdpoints = self.msdpoints + 2  # max msd points plus first 2 cols
        cols = ['ROI', 'Trace'] + [str(x) for x in range(1, self.msdpoints + 1)]
        msd = pandas.DataFrame([], columns=cols)
        f = open(datafile_msd, encoding=self.encoding)
        f.seek(0)
        for row in f.readlines():
            if row.startswith('#'):
                continue
            s = pandas.Series(row.split('\t'))
            s = s[0:max_msdpoints]  # only first 10 points
            s1 = s.iloc[-1].split('\n')  # remove end of line if present
            s.iloc[-1] = s1[0]
            # padding
            x = list(s.values) + [np.nan for i in range(len(s), max_msdpoints)]
            s = pandas.Series(x)
            msd = msd.append(s, ignore_index=True)
        #Add log10 column
        data[self.field] = np.log10(data[self.diffcolumn])
        self.data = data
        self.msd = msd
        return (data, msd)

    def filter_datafiles(self, data, msd, field, minval, maxval):
        """
        Filter field with minval and maxval
        :param data:
        :param msd:
        :param field:
        :param minval:
        :param maxval:
        :return: filtered dataframes for data and msd
        """
        minfilter = data[field] >= minval
        maxfilter = data[field] <= maxval
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
    parser.add_argument('--outputdir', action='store', help='Output directory', default="data")
    parser.add_argument('--minlimit', action='store', help='Min filter', default="-4")
    parser.add_argument('--maxlimit', action='store', help='Max filter', default="1")
    args = parser.parse_args()

    datafile = join(args.filedir, args.datafile)
    datafile_msd = join(args.filedir, args.datafile_msd)
    outputdir = args.outputdir
    print("Input:", datafile)

    try:
        fmsd = FilterMSD()
        (data, msd) = fmsd.load_datafiles(datafile, datafile_msd)

        if not data.empty:
            # print(data)
            field = fmsd.field
            print("Rows loaded= ", len(data), ' msd=', len(msd))
            (filtered, filtered_msd) = fmsd.filter_datafiles(data, msd, field, int(args.minlimit), int(args.maxlimit))
            print("Rows after filtering= ", len(filtered), ' msd=', len(filtered_msd))
            # Save files
            fdata = join(args.outputdir, "Filtered_log10D.csv")
            fmsd = join(args.outputdir, "Filtered_" + args.datafile_msd)
            filtered.to_csv(fdata[field], index=False)  # with or without original index numbers
            filtered_msd.to_csv(fmsd, index=True)
            print("Files saved to: ", fdata, fmsd)
        else:
            raise ValueError("Data not loaded")


    except ValueError as e:
        print("Error: ", e)

    except OSError as e:
        if access(datafile, R_OK):
            print('Unknown file error:', e)
        else:
            print("Cannot access file or directory: ", e)
