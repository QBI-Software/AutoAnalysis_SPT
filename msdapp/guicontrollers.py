import time
from multiprocessing import Manager, Process, freeze_support, Pool
from os import access, R_OK, mkdir
from os.path import join, dirname, exists
import threading
from glob import glob, iglob
import matplotlib.pyplot as plt
import pandas as pd
import wx
import logging
from configobj import ConfigObj
from os import access, R_OK, walk, mkdir
from os.path import join, expanduser, dirname, exists, split
import re
from queue import Queue
from msdapp.msd.batchCompareMSD import CompareMSD
from msdapp.msd.batchHistogramStats import HistoStats
from msdapp.msd.filterMSD import FilterMSD
from msdapp.msd.histogramLogD import HistogramLogD
from msdapp.msd.msdStats import MSDStats
import sys

freeze_support()
# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()
EVT_DATA_ID = wx.NewId()


def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

def EVT_DATA(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_DATA_ID, func)



class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class DataEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_DATA_ID)
        self.data = data
########################################################################

lock = threading.Lock()

class FilterThread(threading.Thread):
    """Multi Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, controller,wxObject, filenames, type, row):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self._stopevent = threading.Event()

        self.controller = controller
        self.wxObject = wxObject
        self.filenames = filenames
        self.row = row
        self.type = type

        #self.start()  # start the thread

    # ----------------------------------------------------------------------
    def run(self):
        lock.acquire(True)
        q = dict()
        total_files = len(self.filenames)
        for i in range(total_files):
            count = (i + 1 / total_files) * 100
            wx.PostEvent(self.wxObject, ResultEvent((count, self.row, i + 1, total_files, self.type)))
            self.processFilter(self.filenames[i], q)

        #self.controller.results[self.type] = pd.DataFrame.from_dict(q, orient='index')
        wx.PostEvent(self.wxObject, ResultEvent((100, self.row, total_files, total_files, self.type)))
        print('Finished FilterThread')
        lock.release()

    # ----------------------------------------------------------------------
    def processFilter(self, filename, q):
        """
        Activate filter process - multithreaded
        :param datafile:
        :param q:
        :return:
        """
        print("Process Filter with file:", filename)
        ##lock.acquire(True)
        try:
            datafile_msd = filename.replace(self.controller.datafile, self.controller.msdfile)
            if not access(datafile_msd, R_OK):
                raise IOError("Cannot find msd file: %s" % datafile_msd)
            # create local subdir for output
            outputdir = join(dirname(filename), 'processed')
            if not exists(outputdir):
                mkdir(outputdir)
            fmsd = FilterMSD(self.controller.configfile, filename, datafile_msd, outputdir)
            q[filename] = fmsd.runFilter()
        except KeyboardInterrupt:
            print("Keyboard interrupt in process: ", filename)
        finally:
            print("Filter: end thread", filename)
            ##lock.release()

    # ----------------------------------------------------------------------
    # def oldrun(self):
    #     """Run Worker Thread."""
    #     # This is the code executing in the new thread.
    #     total_files = len(self.filenames)
    #     #lock.acquire(True)
    #     print("Running Filter thread")
    #     tasks = []
    #     try:
    #         mm = Manager()
    #         q = mm.dict()
    #         i =0
    #         for i in range(total_files):
    #             p = Process(target=self.processFilter, args=(self.filenames[i], q))
    #             tasks.append(p)
    #             p.start()
    #
    #         for p in tasks:
    #             p.join()
    #             print('Task finished - i=', i)
    #             count = (i + 1 / total_files) * 100
    #             wx.PostEvent(self.wxObject, ResultEvent((count, self.row, i + 1, total_files, type)))
    #             i += 1
    #
    #         #self.controller.results = pd.DataFrame.from_dict(q, orient='index')
    #         wx.PostEvent(self.wxObject, ResultEvent((100,self.row, i+1, total_files, type)))
    #
    #     except KeyboardInterrupt:
    #         print("Keyboard interrupt in THREAD")
    #
    #     finally:
    #         #lock.release()
    #         # to be safe -- explicitly shutting down the manager
    #         mm.shutdown()
    #         print("Thread ended: ", self.type)

########################################################################
class HistogramThread(threading.Thread):
    """Multi Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, controller, wxObject, filenames, type, row):
        """Init Worker Thread Class."""
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        self.controller = controller
        self.wxObject = wxObject
        self.filenames = filenames
        self.row = row
        self.type = type
        #self.start()  # start the thread after

    # ----------------------------------------------------------------------
    def run(self):
        lock.acquire(True)
        q = dict()
        total_files = len(self.filenames)
        for i in range(total_files):
            count = (i + 1 / total_files) * 100
            wx.PostEvent(self.wxObject, ResultEvent((count, self.row, i + 1, total_files, self.type)))
            self.processHistogram(self.filenames[i], q)

        #self.controller.results[self.type] = pd.DataFrame.from_dict(q, orient='index')
        wx.PostEvent(self.wxObject, ResultEvent((100, self.row, total_files, total_files, self.type)))
        print('Finished HistogramThread')
        lock.release()

    # ----------------------------------------------------------------------
    def processHistogram(self, datafile, q):
        """

        :param datafile: eg Filtered_log10D.csv
        :param q:
        :return:
        """
        print("Process histogram with file:", datafile)
        # lock.acquire(True)
        try:
            outputdir = dirname(datafile)
            fd = HistogramLogD(datafile, self.controller.configfile)
            q[datafile] = fd.generateHistogram(outputdir)

        except KeyboardInterrupt:
            print("Keyboard interrupt in process: ", datafile)
        finally:
            print("Histogram: end thread", datafile)
            # lock.release()
    # ----------------------------------------------------------------------

    # def run(self):
    #     """Run Worker Thread."""
    #     # This is the code executing in the new thread.
    #     total_files = len(self.filenames)
    #
    #     print("Running Histogram thread")
    #     tasks = []
    #     try:
    #         mm = Manager()
    #         q = mm.dict()
    #         i = 0
    #         for i in range(total_files):
    #             p = Process(target=self.controller.processHistogram, args=(self.filenames[i], q))
    #             p.start()
    #             tasks.append(p)
    #
    #         for p in tasks:
    #             p.join()
    #             count = (i + 1 / total_files) * 100
    #             wx.PostEvent(self.wxObject, ResultEvent((count, self.row, i + 1, total_files, type)))
    #
    #         # self.controller.results = pd.DataFrame.from_dict(q, orient='index')
    #         wx.PostEvent(self.wxObject, ResultEvent((100, self.row, i + 1, total_files, type)))
    #
    #     except KeyboardInterrupt:
    #         print("Keyboard interrupt in THREAD")
    #
    #     finally:
    #         #lock.release()
    #         # to be safe -- explicitly shutting down the manager
    #         mm.shutdown()
    #         print("Thread ended: ", self.type)

class StatsThread(threading.Thread):
    """Multi Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, controller, wxObject, filenames, outputdir, expt, groups,type, row):
        """Init Worker Thread Class."""
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        self.controller = controller
        self.wxObject = wxObject
        self.filenames = filenames
        self.row = row
        self.type = type
        self.expt = expt
        self.groups = groups
        self.outputdir = outputdir
        # self.start()  # start the thread after

    # ----------------------------------------------------------------------
    def run(self):
        lock.acquire(True)
        q = dict()
        total = len(self.groups)
        i = 1
        pool = Pool()
        fmsds = []
        for group in self.groups:
            print("Running %s script: %s (%s)" % (self.type.title(), self.expt, group))
            fmsd = HistoStats(self.filenames, self.outputdir, group, self.expt, self.controller.configfile)
            fmsd.compile()
            compiledfile = fmsd.runStats()
            # Split to Mobile/immobile fractions - output
            ratiofile = fmsd.splitMobile()
            count = (i / total) * 100
            wx.PostEvent(self.wxObject, ResultEvent((count, self.row, i, total, self.type)))
            print("HISTOGRAM BATCH: %s: %s\n\t%s\n\t%s\n" % (self.expt, group, compiledfile, ratiofile))
            fmsds.append(fmsd)
            i += 1
        # Set the figures
        pool.map(self.controller.histplot, fmsds)
        #self.controller.results[self.type] = pd.DataFrame.from_dict(q, orient='index')
        wx.PostEvent(self.wxObject, ResultEvent((100, self.row, i-1, total, self.type)))

        print('Finished StatsThread')
        lock.release()


class MsdThread(threading.Thread):
    """Multi Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, controller, wxObject, filenames, outputdir,expt, groups,type, row):
        """Init Worker Thread Class."""
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        self.controller = controller
        self.wxObject = wxObject
        self.filenames = filenames
        self.row = row
        self.type = type
        self.expt = expt
        self.groups = groups
        self.outputdir = outputdir
        # self.start()  # start the thread after

    # ----------------------------------------------------------------------
    def run(self):
        lock.acquire(True)
        q = dict()
        total = len(self.groups)
        i = 1
        pool = Pool()
        fmsds =[]
        for group in self.groups:
            print("Running %s script: %s (%s)" % (self.type.title(), self.expt, group))
            fmsd = CompareMSD(self.filenames, self.outputdir, group, self.expt, self.controller.configfile)
            compiledfile = fmsd.compile()
            count = (i / total) * 100
            wx.PostEvent(self.wxObject, ResultEvent((count, self.row, i, total, type)))
            print("MSD BATCH: %s: %s\n\t%s\n" % (self.expt, group, compiledfile))
            i += 1
            fmsds.append(fmsd)

        # Set the figure
        pool.map(self.controller.msdplot, fmsds)
        wx.PostEvent(self.wxObject, ResultEvent((100, self.row, i - 1, total, type)))
        print('Finished MsdThread')
        lock.release()



########################################################################

class MSDController():
    def __init__(self, configfile):

        self.processes = [
            {'caption': '1. Filter Data', 'href': 'filter',
             'description': 'Filter log10 diffusion coefficient (log10D) and corresponding MSD data between min and max range',
             'files': 'DATA_FILENAME, MSD_FILENAME',
             'filesout': 'FILTERED_FILENAME, FILTERED_MSD'},
            {'caption': '2. Generate Histograms', 'href': 'histogram',
             'description': 'Generate relative frequency histograms of Log10 D data for individual cells and all cells',
             'files': 'FILTERED_FILENAME',
             'filesout': 'HISTOGRAM_FILENAME'},
            {'caption': '3. Histogram Stats', 'href': 'stats',
             'description': 'Compiles histogram data from all cell directories (batch) into one file in output directory with statistics',
             'files': 'HISTOGRAM_FILENAME',
             'filesout': 'ALLSTATS_FILENAME'},
            {'caption': '4. Compile MSD', 'href': 'msd',
             'description': 'Compiles MSD data from all cell directories (batch) into one file in output directory with statistics',
             'files': 'FILTERED_MSD',
             'filesout': 'AVGMSD_FILENAME'}
        ]
        self.configfile = configfile
        self.loaded = self.loadConfig()
        self.timer = wx.Timer()
        logging.basicConfig(level=logging.DEBUG, filename='msdthread.log',
                            format='[%(levelname)s] (%(threadName)-9s) %(message)s', )

        #Multiprocessing settings
        # multiprocessing.log_to_stderr()
        # logger = multiprocessing.get_logger()
        # logger.setLevel(logging.INFO)

    # ----------------------------------------------------------------------
    def loadConfig(self, config=None):
        """
        Load from config file or config object
        :param config:
        :return:
        """
        rtn = False
        try:
            if self.configfile is not None and access(self.configfile, R_OK):
                print("Loading config file:", self.configfile)
                config = ConfigObj(self.configfile, encoding='ISO-8859-1')
            else:
                print("Loading config object:", config.filename)

            self.datafile = config['DATA_FILENAME']  # AllROI-D.txt
            self.msdfile = config['MSD_FILENAME']  # AllROI-MSD.txt
            self.filteredfname = config['FILTERED_FILENAME']
            self.filtered_msd = config['FILTERED_MSD']
            self.histofile = config['HISTOGRAM_FILENAME']
            self.diffcolumn = config['DIFF_COLUMN']
            self.logcolumn = config['LOG_COLUMN']
            self.msdpoints = config['MSD_POINTS']
            self.minlimit = config['MINLIMIT']
            self.maxlimit = config['MAXLIMIT']
            self.timeint = config['TIME_INTERVAL']
            self.binwidth = config['BINWIDTH']
            self.threshold = config['THRESHOLD']
            self.allstats = config['ALLSTATS_FILENAME']
            self.msdcompare = config['AVGMSD_FILENAME']
            self.group1 = config['GROUP1']
            self.group2 = config['GROUP2']
            self.config = config
            rtn = True

        except:
            raise IOError
        return rtn





    # ----------------------------------------------------------------------
    def processTest(self,datafile,q):
        """
        For testing multi-processing
        :param datafile:
        :param q:
        :return:
        """
        print('Process Test - started')
        ##lock.acquire(True)
        result = 0
        for i in range(10):
            result += i
        q[datafile] = result
        ##lock.release()
        print('Process Test - end')

    # ----------------------------------------------------------------------
    # def RunFilter(self, wxGui,filenames, row=0):
    #     #lock.acquire(True)
    #     type = 'filter'
    #     files = [f for f in filenames if self.datafile in f]
    #     if len(files) > 0:
    #         total_files = len(files)
    #         tasks = []
    #         mm = Manager()
    #         q = mm.dict()
    #
    #         for i in range(total_files):
    #             print("Running %s script: %s (%d of %d)" % (type.title(), files[i], i, total_files))
    #             p = Process(target=self.processFilter, args=(files[i], q))
    #             tasks.append(p)
    #             p.start()
    #
    #         i=0
    #         for p in tasks:
    #             p.join()
    #             count = (i + 1 / total_files) * 100
    #             wx.PostEvent(wxGui, ResultEvent((count, row, i + 1, total_files, type)))
    #             i += 1
    #
    #         headers = ['Data', 'MSD', 'Total', 'Filtered', 'Total_MSD', 'Filtered_MSD']
    #         results = pd.DataFrame.from_dict(q, orient='index')
    #         results.columns = headers
    #         for i, row in results.iterrows():
    #             print("FILTER: %s\n\t%d of %d rows filtered\n\t%s\n\t%s\n" % (
    #                 i, row['Filtered'], row['Total'], row['Data'], row['MSD']))
    #         print("Complete")
    #         #lock.release()
    #     else:
    #         print("RunFilter: Cannot find any datafiles")
    #
    # # ----------------------------------------------------------------------
    # def RunHistogram(self, wxGui,filenames, row=0):
    #     #lock.acquire(True)
    #     type = 'histo'
    #     if len(filenames) > 0:
    #         total_files = len(filenames)
    #         tasks = []
    #         mm = Manager()
    #         q = mm.dict()
    #         for i in range(total_files):
    #             print("Running %s script: %s (%d of %d)" % (type.title(), filenames[i], i, total_files))
    #             count = (i + 1 / total_files) * 100
    #             wx.PostEvent(wxGui, ResultEvent((count, row, i + 1, total_files, type)))
    #             p = Process(target=self.processHistogram, args=(filenames[i], q))
    #             tasks.append(p)
    #             p.start()
    #
    #         for p in tasks:
    #             p.join()
    #
    #         headers = ['Figure', 'Histogram data']
    #         results = pd.DataFrame.from_dict(q, orient='index')
    #         results.columns = headers
    #         for i, row in results.iterrows():
    #             print("HISTOGRAM: %s\n\t%s\n\t%s\n" % (
    #                 i, row['Figure'], row['Histogram data']))
    #         print("Complete")
    #         #lock.release()
    #
    #     else:
    #         print("RunHistogram: Cannot find any datafiles")

    # ----------------------------------------------------------------------
    # def RunStats(self, wxGui,filenames, outputdir, expt=None, row=0):
    #     type = 'stats'
    #     if expt is None:
    #         expt = ''
    #     # loop through directory structure and locate prefixes with expt name
    #     try:
    #         groups = [self.group1,self.group2]
    #         total = len(groups)
    #         i = 1
    #         for group in groups:
    #             print("Running %s script: %s (%s)" % (type.title(), expt, group))
    #             fmsd = HistoStats(filenames, outputdir, group, expt, self.configfile)
    #             fmsd.compile()
    #             compiledfile = fmsd.runStats()
    #             # Split to Mobile/immobile fractions - output
    #             ratiofile = fmsd.splitMobile()
    #             count = (i/ total) * 100
    #             wx.PostEvent(wxGui, ResultEvent((count, row, i, total, type)))
    #             print("HISTOGRAM BATCH: %s: %s\n\t%s\n\t%s\n" % (expt, group, compiledfile, ratiofile))
    #             #self.result_stats.SetLabel("Complete - Close plot to continue")
    #             # Set the figure
    #             fig = plt.figure(figsize=(10, 5))
    #             axes1 = plt.subplot(121)
    #             fmsd.showPlots(axes1)
    #
    #             axes2 = plt.subplot(122)
    #             fmsd.showAvgPlot(axes2)
    #
    #             figtype = 'png'  # png, pdf, ps, eps and svg.
    #             figname = fmsd.compiledfile.replace('csv', figtype)
    #             plt.savefig(figname, facecolor='w', edgecolor='w', format=figtype)
    #             plt.show()
    #             i += 1
    #         wx.PostEvent(wxGui, ResultEvent((100, row, i-1, total, type)))
    #     except ValueError as e:
    #         print("Batch Histogram error: %s" % e)


    # ----------------------------------------------------------------------
    # def RunMSD(self, wxGui,filenames, outputdir, expt=None, row=0):
    #     type = 'msd'
    #     if expt is None:
    #         expt = ''
    #     try:
    #         groups = [self.group1, self.group2]
    #         total = len(groups)
    #         i = 1
    #         for group in groups:
    #             print("Running %s script: %s (%s)" % (type.title(), expt, group))
    #             fmsd = CompareMSD(filenames, outputdir, group, expt, self.configfile)
    #             compiledfile = fmsd.compile()
    #             count = (i / total) * 100
    #             wx.PostEvent(wxGui, ResultEvent((count, row, i, total, type)))
    #             #self.result_msd.SetLabel("Complete")
    #             #Set the figure
    #             fig = plt.figure(figsize=(10, 5))
    #             axes1 = plt.subplot(121)
    #             areasfile = fmsd.showPlotsWithAreas(axes1)
    #             print("MSD BATCH: %s: %s\n\t%s\t%s\n" % (expt, group, compiledfile, areasfile))
    #             axes2 = plt.subplot(122)
    #             fmsd.showAvgPlot(axes2)
    #
    #             figtype = 'png'  # png, pdf, ps, eps and svg.
    #             figname = fmsd.compiledfile.replace('csv', figtype)
    #             plt.savefig(figname, facecolor='w', edgecolor='w', format=figtype)
    #             plt.show()
    #             i+=1
    #         wx.PostEvent(wxGui, ResultEvent((100, row, i-1, total, type)))
    #     except ValueError as e:
    #         print("Batch MSD error: %s" % e)

    def msdplot(self, fmsd):
        fig = plt.figure(figsize=(10, 5))
        axes1 = plt.subplot(121)
        areasfile = fmsd.showPlotsWithAreas(axes1)
        axes2 = plt.subplot(122)
        fmsd.showAvgPlot(axes2)

        figtype = 'png'  # png, pdf, ps, eps and svg.
        figname = fmsd.compiledfile.replace('csv', figtype)
        plt.savefig(figname, facecolor='w', edgecolor='w', format=figtype)
        plt.show()

    def histplot(self,fmsd):
        # Set the figure
        fig = plt.figure(figsize=(10, 5))
        axes1 = plt.subplot(121)
        fmsd.showPlots(axes1)

        axes2 = plt.subplot(122)
        fmsd.showAvgPlot(axes2)

        figtype = 'png'  # png, pdf, ps, eps and svg.
        figname = fmsd.compiledfile.replace('csv', figtype)
        plt.savefig(figname, facecolor='w', edgecolor='w', format=figtype)
        plt.show()

    # ----------------------------------------------------------------------
    def RunCompare(self, wxGui, indirs, outputdir, prefixes, searchtext):
        if len(outputdir) <=0:
            outputdir=indirs[0] #default
        rs = MSDStats(indirs, outputdir, prefixes, self.configfile)
        results_df = rs.runTtests()
        print("RunCompare results:",results_df)
        wx.PostEvent(wxGui, DataEvent(results_df))
        # Show plots
        if len(searchtext)<=0:
            searchtext=" ".join(prefixes)
        rs.showPlots(searchtext + " comparison")



    # ----------------------------------------------------------------------
    def CheckFilenames(self,filenames, configfiles):
        """
        Check that filenames are appropriate for the script required
        :param filenames: list of full path filenames
        :param configfiles: matching filename for script as in config
        :return: filtered list
        """
        newfiles = []
        for conf in configfiles:
            for f in filenames:
                parts = split(f)
                if conf in parts[1]:
                    newfiles.append(f)
                else:
                    #extract directory and seek files
                    newfiles = newfiles + [y for y in iglob(join(parts[0], '**', conf), recursive=True)]
        #print("Checked: ",newfiles)
        return newfiles

    # ----------------------------------------------------------------------
    def RunProcess(self, wxGui,filenames, i,outputdir, expt, row=0):
        """
        Instantiate Thread with type for Process
        :param wxGui:
        :param filenames:
        :param type:
        :param row:
        :return:
        """
        type = self.processes[i]['href']
        pname = self.processes[i]['caption']
        filesIn = [self.config[f] for f in self.processes[i]['files'].split(", ")]
        checkedfilenames = self.CheckFilenames(filenames, filesIn)
        print("Checked by type: (", type, "): ", checkedfilenames)
        wx.PostEvent(wxGui, ResultEvent((0, row, 0, len(checkedfilenames), pname)))
        print("RunProcess Expt: ", expt)

        print("Running Threads - start: ", type)

        if type == 'filter':
            #lock.acquire(True)
            #exclude any MSD filenames
            files = [f for f in checkedfilenames if self.datafile in f]
            t = FilterThread(self, wxGui, files, type, row)
            t.start()
            #lock.release()
        elif type == 'histogram':
            #lock.acquire(True)
            t = HistogramThread(self, wxGui,checkedfilenames, type, row)
            t.start()
            #lock.release()
        elif type == 'stats':
            #lock.acquire(True)
            t = StatsThread(self, wxGui, checkedfilenames, outputdir, expt, [self.group1,self.group2], type, row)
            t.start()
            #self.RunStats(wxGui, checkedfilenames, outputdir, expt, row)
            #lock.release()
        elif type == 'msd':
            #lock.acquire(True)
            t= MsdThread(self, wxGui, checkedfilenames, outputdir, expt, [self.group1,self.group2],type, row)
            t.start()
            #self.RunMSD(wxGui, checkedfilenames, outputdir, expt, row)
            #lock.release()

        print("Running Thread - loaded: ", type)
        #print("Thread Results: ", self.results)


    # ----------------------------------------------------------------------
    def shutdown(self):
        logging.debug('Call to shutdown')
        print(sys.thread_info)
        for t in threading.enumerate():
            logging.debug('closing %s', t.getName())
            if t.is_alive():
                t.terminate()




