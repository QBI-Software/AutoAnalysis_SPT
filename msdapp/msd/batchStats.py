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
    def __init__(self, inputfiles, outputdir, prefix, expt, configfile=None, nolistfilter=False):
        self.encoding = 'ISO-8859-1'
        self.__loadConfig(configfile)
        if self.config is not None and self.datafield is not None:
            self.datafile = self.config[self.datafield]
        else:
            raise ValueError("Cannot determine which files to compile - check config Datafile option")
        self.searchtext = expt + prefix
        self.expt = expt
        self.prefix = prefix
        (self.base, self.inputfiles) = self.getSelectedFiles(inputfiles, self.datafile, expt, prefix, nofilter=nolistfilter)
        self.numcells = len(self.inputfiles)
        self.outputdir = outputdir
        if self.roi:
            self.n = 0
        else:
            self.n = 1  # generating id


    def __loadConfig(self, configfile=None):
        try:
            if configfile is not None and access(configfile, R_OK):
                config = ConfigObj(configfile, encoding=self.encoding)
                self.config = config
                if 'GROUPBY_ROI' in config.keys():
                    self.roi = int(self.config['GROUPBY_ROI'])
                    msg = "Batch: Config file loaded. Group by ROIs: %d" % self.roi
                else:
                    msg = "Batch: Config file loaded."
                logging.info(msg)
            else:
                self.config = None
                self.roi = 0
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

    def getSelectedFiles(self, inputdir, datafile, expt, prefix, nofilter=False):
        """
        Check list or directory matches searchtext(expt) and prefix(group) and contains only datafiles
        tries several methods for detecting files
        :param inputdir: list of files or input directory
        :param datafile: matching datafile name
        :param expt: searchstring in filename/filepath
        :param prefix: comparison group - also needs to appear in filepath or filename
        :param nofilter: assume provided list is correct - no further matching
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
            if not nofilter:
                files = [f for f in allfiles if re.search(searchtext, f, flags=re.IGNORECASE)]
                if len(files) <= 0:
                    files = [f for f in allfiles if prefix.upper() in f.upper().split(sep)]
                else:
                    files = allfiles #default assume prefix and expt strings are not found
            else:
                files = allfiles
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
            if (self.roi and re.search('ROI_\d',f)):
                m = re.search('ROI_\d', f)
                roi_id = m.group(0)
                if roi_id == 'ROI_1':
                    self.n +=1
                cellid = 'c{0:03d}_{1}'.format(self.n,m.group(0))
            else:
                cellid = 'c{0:03d}'.format(self.n)
                self.n += 1
            cell = "_".join([self.searchtext, cellid])

        print("base=", self.base, " cellid=", cell)
        return cell
