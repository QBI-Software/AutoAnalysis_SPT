import logging
import sys
import threading
from glob import iglob
from multiprocessing import freeze_support, Pool
from os import access, R_OK, mkdir
from os.path import join, dirname, exists, split

import matplotlib.pyplot as plt
import wx
from configobj import ConfigObj

from msdapp.msd.batchCompareMSD import CompareMSD
from msdapp.msd.batchHistogramStats import HistoStats
from msdapp.msd.filterMSD import FilterMSD
from msdapp.msd.histogramLogD import HistogramLogD
from msdapp.msd.msdStats import MSDStats

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
event = threading.Event()
hevent = threading.Event()


class FilterThread(threading.Thread):
    """Multi Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, controller, wxObject, filenames, filesin, type, row, processname):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self.controller = controller
        self.wxObject = wxObject
        self.filenames = filenames
        self.filesIn = filesin
        self.row = row
        self.type = type
        self.processname = processname

        # self.start()  # start the thread

    # ----------------------------------------------------------------------
    def run(self):
        try:
            event.set()
            lock.acquire(True)
            # Do work
            q = dict()
            checkedfilenames = self.controller.CheckFilenames(self.filenames, self.filesIn)
            print("Checked by type: (", self.processname, "): ", checkedfilenames)
            files = [f for f in checkedfilenames if self.controller.datafile in f]
            total_files = len(files)
            for i in range(total_files):
                count = ((i + 1) * 100) / total_files
                print("FilterThread.run: count=", count)
                wx.PostEvent(self.wxObject, ResultEvent((count, self.row, i + 1, total_files, self.processname)))
                self.processFilter(files[i], q)

            # self.controller.results[self.type] = pd.DataFrame.from_dict(q, orient='index')
            wx.PostEvent(self.wxObject, ResultEvent((100, self.row, total_files, total_files, self.processname)))

        except KeyboardInterrupt:
            print("Keyboard interrupt in FilterThread")
            self.terminate()
        finally:
            print('Finished FilterThread')
            lock.release()
            event.clear()

    # ----------------------------------------------------------------------
    def processFilter(self, filename, q):
        """
        Activate filter process - multithreaded
        :param datafile:
        :param q:
        :return:
        """
        print("Process Filter with file:", filename)
        datafile_msd = filename.replace(self.controller.datafile, self.controller.msdfile)
        if not access(datafile_msd, R_OK):
            raise IOError("Cannot find msd file: %s" % datafile_msd)
        # create local subdir for output
        outputdir = join(dirname(filename), 'processed')
        if not exists(outputdir):
            mkdir(outputdir)
        fmsd = FilterMSD(self.controller.configfile, filename, datafile_msd, outputdir)
        q[filename] = fmsd.runFilter()

    # ----------------------------------------------------------------------
    def terminate(self):
        print("Terminating Filter Thread")
        self.terminate()

########################################################################
class HistogramThread(threading.Thread):
    """Multi Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, controller, wxObject, filenames, filesIn, type, row, pname):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self.controller = controller
        self.wxObject = wxObject
        self.filenames = filenames
        self.filesIn = filesIn
        self.row = row
        self.type = type
        self.pname = pname
        # self.start()  # start the thread after

    # ----------------------------------------------------------------------
    def run(self):
        try:
            hevent.set()
            lock.acquire(True)
            q = dict()
            checkedfilenames = self.controller.CheckFilenames(self.filenames, self.filesIn)
            print("Checked by type: (", self.pname, "): ", checkedfilenames)
            total_files = len(checkedfilenames)
            for i in range(total_files):
                count = (i + 1 / total_files) * 100
                wx.PostEvent(self.wxObject, ResultEvent((count, self.row, i + 1, total_files, self.type)))
                datafile = checkedfilenames[i]
                print("Process histogram with file:", datafile)
                outputdir = dirname(datafile)
                fd = HistogramLogD(datafile, self.controller.configfile)
                q[datafile] = fd.generateHistogram(outputdir)

            wx.PostEvent(self.wxObject, ResultEvent((100, self.row, total_files, total_files, self.pname)))

        except KeyboardInterrupt:
            print("Keyboard interrupt in HistogramThread")
            self.terminate()
        finally:
            print('Finished HistogramThread')
            lock.release()
            hevent.clear()

    # ----------------------------------------------------------------------
    def terminate(self):
        print("Terminating Histogram Thread")
        self.terminate()

##########################################################################################################
class StatsThread(threading.Thread):
    """Multi Worker Thread Class."""
    # ----------------------------------------------------------------------
    def __init__(self, controller, wxObject, filenames, filesIn, outputdir, expt, groups, type, row, pname):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self.controller = controller
        self.wxObject = wxObject
        self.filenames = filenames
        self.filesIn = filesIn
        self.row = row
        self.type = type
        self.expt = expt
        self.groups = groups
        self.outputdir = outputdir
        self.pname = pname
        # self.start()  # start the thread after

    # ----------------------------------------------------------------------
    def run(self):
        try:
            lock.acquire(True)
            q = dict()
            total = len(self.groups)
            checkedfilenames = self.controller.CheckFilenames(self.filenames, self.filesIn)
            print("Checked by type: (", self.pname, "): ", checkedfilenames)
            i = 1
            pool = Pool()
            fmsds = []
            for group in self.groups:
                print("Running %s script: %s (%s)" % (self.type.title(), self.expt, group))
                fmsd = HistoStats(checkedfilenames, self.outputdir, group, self.expt, self.controller.configfile)
                fmsd.compile()
                compiledfile = fmsd.runStats()
                # Split to Mobile/immobile fractions - output
                ratiofile = fmsd.splitMobile()
                count = (i / total) * 100
                wx.PostEvent(self.wxObject, ResultEvent((count, self.row, i, total, self.pname)))
                print("HISTOGRAM BATCH: %s: %s\n\t%s\n\t%s\n" % (self.expt, group, compiledfile, ratiofile))
                fmsds.append(fmsd)
                i += 1
            # Set the figures
            pool.map(self.controller.histplot, fmsds)
            # self.controller.results[self.type] = pd.DataFrame.from_dict(q, orient='index')
            wx.PostEvent(self.wxObject, ResultEvent((100, self.row, i - 1, total, self.pname)))
        except KeyboardInterrupt:
            print("Keyboard interrupt in StatsThread")
            self.terminate()
        finally:
            print('Finished StatsThread')
            lock.release()

    # ----------------------------------------------------------------------
    def terminate(self):
        print("Terminating Stats Thread")
        self.terminate()

############################################################################
class MsdThread(threading.Thread):
    """Multi Worker Thread Class."""
    # ----------------------------------------------------------------------
    def __init__(self, controller, wxObject, filenames, filesIn, outputdir, expt, groups, type, row, pname):
        """Init Worker Thread Class."""
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        self.controller = controller
        self.wxObject = wxObject
        self.filenames = filenames
        self.filesIn = filesIn
        self.row = row
        self.type = type
        self.expt = expt
        self.groups = groups
        self.outputdir = outputdir
        self.pname = pname
        # self.start()  # start the thread after

    # ----------------------------------------------------------------------
    def run(self):
        try:
            lock.acquire(True)
            q = dict()
            checkedfilenames = self.controller.CheckFilenames(self.filenames, self.filesIn)
            print("Checked by type: (", self.pname, "): ", checkedfilenames)
            total = len(self.groups)
            i = 1
            pool = Pool()
            fmsds = []
            for group in self.groups:
                print("Running %s script: %s (%s)" % (self.pname.title(), self.expt, group))
                fmsd = CompareMSD(checkedfilenames, self.outputdir, group, self.expt, self.controller.configfile)
                compiledfile = fmsd.compile()
                count = (i / total) * 100
                wx.PostEvent(self.wxObject, ResultEvent((count, self.row, i, total, self.pname)))
                print("MSD BATCH: %s: %s\n\t%s\n" % (self.expt, group, compiledfile))
                i += 1
                fmsds.append(fmsd)

            # Set the figure
            pool.map(self.controller.msdplot, fmsds)
            wx.PostEvent(self.wxObject, ResultEvent((100, self.row, i - 1, total, self.pname)))
        except KeyboardInterrupt:
            print("Keyboard interrupt in MsdThread")
            self.terminate()
        finally:
            print('Finished MsdThread')
            lock.release()

    # ----------------------------------------------------------------------
    def terminate(self):
        print("Terminating MSD Thread")
        self.terminate()

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

        # Multiprocessing settings
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
    def processTest(self, datafile, q):
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

    def histplot(self, fmsd):
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

    def compareplot(self, data):
        # Show plots
        (rs, searchtext) = data
        rs.showPlots(searchtext + " comparison")

    # ----------------------------------------------------------------------
    def RunCompare(self, wxGui, indirs, outputdir, prefixes, searchtext):
        if len(outputdir) <= 0:
            outputdir = indirs[0]  # default
        rs = MSDStats(indirs, outputdir, prefixes, self.configfile)
        results_df = rs.runTtests()
        print("RunCompare results:", results_df)
        wx.PostEvent(wxGui, DataEvent(results_df))
        # # Show plots
        # if len(searchtext) <= 0:
        #     searchtext = " ".join(prefixes)
        # rs.showPlots(searchtext + " comparison")
        pool = Pool()
        if len(searchtext) <= 0:
            searchtext = " ".join(prefixes)
        pool.map(self.compareplot, [(rs, searchtext)])

    # ----------------------------------------------------------------------
    def CheckFilenames(self, filenames, configfiles):
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
                    # extract directory and seek files
                    newfiles = newfiles + [y for y in iglob(join(parts[0], '**', conf), recursive=True)]
        # print("Checked: ",newfiles)
        return newfiles

    # ----------------------------------------------------------------------
    def RunProcess(self, wxGui, filenames, i, outputdir, expt, row):
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
        print("Running Threads - start: ", type, " Expt: ", expt)
        wx.PostEvent(wxGui, ResultEvent((0, row, 0, len(filenames), pname)))
        if type == 'filter':
            t = FilterThread(self, wxGui, filenames, filesIn, type, row, pname)
            t.start()
        elif type == 'histogram':
            event.wait()
            t = HistogramThread(self, wxGui, filenames, filesIn, type, row, pname)
            t.start()
        elif type == 'stats':
            event.wait()
            hevent.wait()
            t = StatsThread(self, wxGui, filenames, filesIn, outputdir, expt, [self.group1, self.group2], type, row,
                            pname)
            t.start()
        elif type == 'msd':
            event.wait()
            t = MsdThread(self, wxGui, filenames, filesIn, outputdir, expt, [self.group1, self.group2], type, row,
                          pname)
            t.start()

        print("Running Thread - loaded: ", type)
        # print("Thread Results: ", self.results)

    # ----------------------------------------------------------------------
    def shutdown(self):
        logging.debug('Call to shutdown')
        print(sys.thread_info)
        for t in threading.enumerate():
            logging.debug('closing %s', t.getName())
            if t.is_alive():
                t.terminate()
