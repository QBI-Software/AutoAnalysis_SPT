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


def load_datafiles(datafile, datafile_msd):
    """
    Load text datafiles as csv into dataframes
    MSD file has uneven rows - but only require first 10 points
    :param datafile:
    :param datafile_msd:
    :return:
    """
    data = pandas.read_csv(datafile, encoding='ISO-8859-1', skiprows=2, delimiter='\t')
    # Uneven rows - detect max columns
    max_msdpoints = 12  # max msd points plus first 2 cols
    cols = range(0, max_msdpoints)
    msd = pandas.DataFrame([], columns=cols)
    f = open(datafile_msd, encoding='ISO-8859-1')
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

    return (data,msd)

def filter_datafiles(data,msd, field, minval, maxval):
    """
    Filter field with minval and maxval
    :param data:
    :param msd:
    :param field:
    :param minval:
    :param maxval:
    :return: filtered dataframes for data and msd
    """
    minfilter = data[field] > int(minval)
    maxfilter = data[field] < int(maxval)
    mmfilter = minfilter & maxfilter
    filtered = data[mmfilter]
    filtered_msd = msd[mmfilter]
    return (filtered,filtered_msd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Parse Excel Files',
                                     description='''\
            Reads a directory and extracts sheet into an output file

             ''')
    parser.add_argument('--filedir', action='store', help='Directory containing files', default="data")
    parser.add_argument('--datafile', action='store', help='Initial data file', default="AllROI-D.txt")
    parser.add_argument('--datafile_msd', action='store', help='Initial data file', default="AllROI-MSD.txt")
    parser.add_argument('--output', action='store', help='Output file name with full path', default="filteredMSD.csv")
    parser.add_argument('--minlimit', action='store', help='Min filter', default="-5")
    parser.add_argument('--maxlimit', action='store', help='Max filter', default="1")
    args = parser.parse_args()

    datafile = join(args.filedir, args.datafile)
    datafile_msd = join(args.filedir, args.datafile_msd)
    outputfile = args.output
    print("Input:", datafile)

    try:
        (data,msd) = load_datafiles(datafile, datafile_msd)

        if not data.empty:
            #print(data)
            data['log10D'] = np.log10(data['D(µm²/s)'])
            print("Rows loaded= ", len(data), ' msd=', len(msd))
            (filtered,filtered_msd) = filter_datafiles(data,msd,'log10D', args.minlimit, args.maxlimit)
            print("Rows after filtering= ", len(filtered), ' msd=', len(filtered_msd))
            #Save files
            fdata = join(args.filedir, "Filtered_"+ args.datafile)
            fmsd = join(args.filedir, "Filtered_" + args.datafile_msd)
            filtered.to_csv(fdata, index=False) # with or without original index numbers
            filtered_msd.to_csv(fmsd, index=False)
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