# -*- coding: utf-8 -*-
"""
Batch Analysis script: batchStats - Abstract Class
Compiles histogram data from directories - expects input format:

STIM OR NOSTIM                                      <-- USE THIS AS INPUT DIRECTORY
 | -- cell1                                         <-- uses this name as cell ID
        | -- celldata
                 | -- Histogram_log10D.csv files    <-- this name must match (generated from histogramLogD)

and compiles to top level as <prefix>_AllHistogram_log10D.csv where prefix can be STIM, NOSTIM (example) in outputdir

Created on Sep 8 2017

@author: Liz Cooper-Williams, QBI
"""

import re
from glob import iglob
from os import R_OK, access
from os.path import join, isdir, commonpath, sep
import logging
#import numpy as np
from numpy import unique
from configobj import ConfigObj


class BatchStats:
    def __init__(self, inputfiles, outputdir, prefix, expt, configfile=None):
        self.encoding = 'ISO-8859-1'
        self.__loadConfig(configfile)
        if self.config is not None and self.datafield is not None:
            self.datafile = self.config[self.datafield]
        self.searchtext = expt + prefix

        if not isinstance(inputfiles, list) and isdir(inputfiles):
            self.base = inputfiles #.split(sep)
            self.inputfiles = self.getSelectedFiles(inputfiles, self.datafile, expt,prefix)
        else:
            searchtext = prefix+expt
            files = [f for f in inputfiles if re.search(searchtext, f, flags=re.IGNORECASE)]
            if len(files)==0:
                files= [f for f in inputfiles if prefix.upper() in f.upper().split(sep)]
            self.inputfiles = files
            self.base = commonpath(self.inputfiles)
        self.numcells = len(self.inputfiles)
        self.outputdir = outputdir

        self.n = 1  # generating id

    def __loadConfig(self, configfile=None):
        try:
            if configfile is not None and access(configfile, R_OK):
                config = ConfigObj(configfile, encoding=self.encoding)
                self.config = config
                # self.datafile = ''
                # self.outputfile = ''
                print("Config file loaded")
            else:
                self.config = None

        except:
            raise IOError("Cannot load Config file")

    def deduplicate(self, itemlist):
        """
        Checks for duplicated column names and appends a number
        :param itemlist:
        :return:
        """
        u, indices = unique(itemlist, return_index=True)
        duplicates = [x for x in range(0, len(itemlist)) if x not in indices]
        i = 0
        for d in duplicates:
            itemlist[d] = itemlist[d] + "_" + str(i)
            i = i + 1

        return itemlist

    def getSelectedFiles(self, inputdir, datafile, expt, prefix):
        # get list of files to compile
        allfiles = []
        searchtext = expt + prefix
        if access(inputdir, R_OK):
            allfiles = [y for y in iglob(join(inputdir, '**', datafile), recursive=True)]
            print("All Files Found: ", len(allfiles))
            if len(allfiles) > 0:
                # Filter on searchtext - single word in directory path
                files = [f for f in allfiles if re.search(searchtext, f, flags=re.IGNORECASE)]
                if len(files) <= 0:
                    msg = "No matching files found for searchtext: %s" % searchtext
                    print(msg)
                    logging.warning(msg)
                    #try separate expt and prefix - case insensitive on windows but ?mac
                    allfiles = [y for y in iglob(join(inputdir, '**', prefix, '**', datafile), recursive=True)]
                    files = [f for f in allfiles if re.search(expt, f, flags=re.IGNORECASE)]
                    if len(files) <= 0:
                        msg= "No matching files found for expt + prefix: %s %s" % (expt,prefix)
                        logging.info(msg)
            else:
                msg = "No files found"
                raise IOError(msg)
        else:
            msg = "ERROR: Unable to access inputdir: %s" % inputdir
            raise IOError(msg)
        return files

    def generateID(self, f):
        # Generate unique cell ID
        cells = f.split(sep)
        base = self.base.split(sep)
        num = 3
        if 'CELLID' in self.config:
            num = int(self.config['CELLID'])
        if len(cells) > (len(base) + num + 1):
            cell = "_".join(cells[len(base):len(base) + num])
        else:
            cellid = 'c{0:03d}'.format(self.n)
            cell = "_".join([self.searchtext, cellid])
            self.n += 1
        print("base=", self.base, " cellid=", cell)
        return cell
