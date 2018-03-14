# -*- coding: utf-8 -*-
"""
MSD Analysis script: batchLogD
Compiles Log10(D) data from directories - expects input format:

STIM OR NOSTIM                                      <-- USE THIS AS INPUT DIRECTORY
 | -- cell1                                         <-- uses this name as cell ID
        | -- celldata
                 | -- Filtered_log10D.csv files    <-- this name must match (generated from filterMSD)

and compiles to top level as <prefix>_All_log10D.csv where prefix can be STIM, NOSTIM (example) in outputdir


Created on Sep 8 2017

@author: Liz Cooper-Williams, QBI
"""

import argparse
import logging
from os.path import join

import matplotlib.pyplot as plt
import pandas as pd
# import numpy as np
from numpy import sqrt, round
from plotly import offline
from plotly.graph_objs import Layout, Scatter

from msdapp.msd.batchStats import BatchStats


class BatchLogd(BatchStats):
    def __init__(self, *args):
        self.datafield = 'FILTERED_FILENAME'
        super().__init__(*args)
        if self.config is not None:
            if 'BATCHD_FILENAME' in self.config:
                self.outputfile = self.config['BATCHD_FILENAME']
            else:
                self.outputfile = 'All_log10D.csv'
            self.logcol = self.config['LOG_COLUMN']
            print("BatchLogD: Config file loaded")
        else:  # defaults
            self.outputfile = 'All_log10D.csv'
            self.datafile = 'Filtered_log10D.csv'
            self.logcol = 'log10D'
            print("BatchLogD: Using config defaults")

        self.compiledfile = join(self.outputdir, self.searchtext + "_" + self.outputfile)
        self.compiled = self.__compile()

    def __compile(self):
        """
        Reads all inputfiles from inputdir, appends data into single dataframe
        :return: dataframe
        """
        try:
            # Compile all selected files
            logging.info("BatchLogD: Compiling %d files" % self.numcells)
            batchfile={}
            for f in self.inputfiles:
                df = pd.read_csv(f)
                cell = self.generateID(f) #TODO add ROI to ID
                #create dict
                batchfile[cell] = df[self.logcol]

            c = pd.DataFrame.from_dict(batchfile)
            if not c.empty:
                c.columns = self.deduplicate(c.columns)
                logging.info("BatchLogD: Compiled %d files" % len(c.columns))
            else:
                logging.error("BatchLogD: Unable to compile files to: %s" % self.compiledfile)
            return c
        except Exception as e:
            msg = "Error: in BatchLogD compile process - %s" % e
            raise IOError(msg)

    def saveCompiled(self):
        if not self.compiled.empty:
            self.compiled.to_csv(self.compiledfile, index=False)
            logging.info("BatchLogD: Data saved to " + self.compiledfile)




#################################################################################################
if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
            Compiles log10(D) data from a directory (recursively looks for Filtered_log10D.csv) into an output file.
             ''')
    parser.add_argument('--filedir', action='store', help='Directory containing files', default="data")
    parser.add_argument('--outputdir', action='store', help='Output directory', default="data")
    parser.add_argument('--prefix', action='store', help='Prefix for compiled file eg STIM or NOSTIM', default="")
    parser.add_argument('--expt', action='store', help='ProteinCelltype as shown on directory names',
                        default="")
    parser.add_argument('--config', action='store', help='Config file for parameters', default=None)
    args = parser.parse_args()

    print("Loading Input from :", args.filedir)

    try:
        fmsd = BatchLogd(args.filedir, args.outputdir, args.prefix, args.expt, args.config)
        fmsd.saveCompiled()
        print('Finished: ', fmsd.compiledfile)


    except ValueError as e:
        print("Error: ", e)
