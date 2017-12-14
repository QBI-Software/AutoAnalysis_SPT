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

import logging
import re
from glob import iglob
from os import R_OK, access
from os.path import join, isdir, commonpath, sep

from configobj import ConfigObj
from numpy import unique


class BatchStats:
    def __init__(self, inputfiles, outputdir, prefix, expt, configfile=None):
        self.encoding = 'ISO-8859-1'
        self.__loadConfig(configfile)
        if self.config is not None and self.datafield is not None:
            self.datafile = self.config[self.datafield]
        else:
            raise ValueError("Cannot determine which files to compile - check config Datafile option")
        self.searchtext = expt + prefix
        self.expt = expt
        self.prefix = prefix
        (self.base, self.inputfiles) = self.getSelectedFiles(inputfiles, self.datafile, expt, prefix)
        self.numcells = len(self.inputfiles)
        self.outputdir = outputdir
        self.n = 1  # generating id

    def __loadConfig(self, configfile=None):
        try:
            if configfile is not None and access(configfile, R_OK):
                config = ConfigObj(configfile, encoding=self.encoding)
                self.config = config
                logging.info("Batch: Config file loaded")
            else:
                self.config = None
                logging.warning("Batch: NO Config file loaded")

        except:
            raise IOError("Batch: Cannot load Config file")

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
        """
        Check list or directory matches searchtext(expt) and prefix(group) and contains only datafiles
        tries several methods for detecting files
        :param inputdir: list of files or input directory
        :param datafile: matching datafile name
        :param expt: searchstring in filename/filepath
        :param prefix: comparison group - also needs to appear in filepath or filename
        :return: basename and file list
        """
        files = []
        base = ''
        searchtext = expt + prefix
        # get list of files from a directory
        if not isinstance(inputdir, list) and isdir(inputdir):
            base = inputdir
            if access(inputdir, R_OK):
                allfiles = [y for y in iglob(join(inputdir, '**', datafile), recursive=True)]
                if len(allfiles) > 0:
                    # Filter on searchtext - single word in directory path
                    files = [f for f in allfiles if re.search(searchtext, f, flags=re.IGNORECASE)]
                    if len(files) <= 0:
                        # try separate expt and prefix - case insensitive on windows but ?mac
                        allfiles = [y for y in iglob(join(base, '**', prefix, '**', datafile), recursive=True)]
                        files = [f for f in allfiles if re.search(expt, f, flags=re.IGNORECASE)]
                    if len(files) <= 0:
                        # try uppercase directory name
                        files = [f for f in allfiles if prefix.upper() in f.upper().split(sep)]
                    if len(files) <= 0:
                        msg = "Batch: No match in path for both expt + prefix: %s %s" % (expt, prefix)
                        logging.error(msg)
                        raise ValueError(msg)
                else:
                    msg = "Batch: No files found in input"
                    logging.error(msg)
                    raise IOError(msg)

            else:
                raise IOError("Batch: Cannot access directory: %s", inputdir)
        else:
            # assume we have a list as input - exclude duplicates
            if isinstance(inputdir, list):
                allfiles = unique(inputdir).tolist()
            else:
                allfiles = unique(inputdir.tolist()).tolist()
            files = [f for f in allfiles if re.search(searchtext, f, flags=re.IGNORECASE)]
            if len(files) <= 0:
                files = [f for f in allfiles if prefix.upper() in f.upper().split(sep)]
            else:
                files = allfiles #default assume prefix and expt strings are not found
            base = commonpath(files)
        print("Total Files Found: ", len(files))

        return (base, files)

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
