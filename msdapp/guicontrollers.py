import time
from multiprocessing import Manager, Process, freeze_support
from os import access, R_OK, mkdir
from os.path import join, dirname, exists
from threading import Thread

import matplotlib.pyplot as plt
import pandas as pd
import wx
from configobj import ConfigObj

from msdapp.msd.batchCompareMSD import CompareMSD
from msdapp.msd.batchHistogramStats import HistoStats
from msdapp.msd.filterMSD import FilterMSD
from msdapp.msd.histogramLogD import HistogramLogD

freeze_support()
# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()


def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

def EVT_CANCEL(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)



class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

########################################################################
class FilterThread(Thread):
    """Test Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, controller,wxObject, filenames, row):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self.controller = controller
        self.wxObject = wxObject
        self.filenames = filenames
        self.row = row
        self.start()  # start the thread

    # ----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.
        total_tasks = len(self.filenames)
        results = []

        if total_tasks > 0:
            print("Running thread")
            tasks = []
            try:
                self.controller.mm = Manager()
                q = self.controller.mm.dict()
                count = 1
                for i in range(total_tasks):
                    p = Process(target=self.controller.processFilter, args=(self.filenames[i], q))
                    p.start()
                    tasks.append(p)
                    # while p.is_alive():
                    #     time.sleep(5)
                    #     wx.PostEvent(self.wxObject, ResultEvent((count, self.row)))
                    #     count += 10
                n = 1
                for p in tasks:
                    p.join()
                    count = (n / total_tasks) * 100
                    wx.PostEvent(self.wxObject, ResultEvent((count, self.row)))
                    n += 1

                #self.controller.results = pd.DataFrame.from_dict(q, orient='index')
                wx.PostEvent(self.wxObject, ResultEvent((100,self.row)))
                print("Thread ended")
            except KeyboardInterrupt:
                print("Keyboard interrupt in THREAD")

            finally:
                # to be safe -- explicitly shutting down the manager
                self.controller.mm.shutdown()
        #return results

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
            {'caption': '4. Compile MSD', 'href': 'compare',
             'description': 'Compiles MSD data from all cell directories (batch) into one file in output directory with statistics',
             'files': 'FILTERED_MSD',
             'filesout': 'AVGMSD_FILENAME'}
        ]
        self.configfile = configfile
        self.loaded = self.loadConfig()
        self.timer = wx.Timer()

        #Multiprocessing settings
        # multiprocessing.log_to_stderr()
        # logger = multiprocessing.get_logger()
        # logger.setLevel(logging.INFO)


    def loadConfig(self, config=None):
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

    def processFilter(self, datafile, q):
        """
        Activate filter process - multithreaded
        :param datafile:
        :param q:
        :return:
        """
        try:
            datafile_msd = datafile.replace(self.datafile, self.msdfile)
            outputdir = join(dirname(datafile), 'processed')  # subdir as inputfiles
            if not exists(outputdir):
                mkdir(outputdir)
            fmsd = FilterMSD(self.configfile, datafile, datafile_msd, outputdir, self.minlimit, self.maxlimit)
            q[datafile] = fmsd.runFilter()
        except KeyboardInterrupt:
            print("Keyboard interrupt in process: ", datafile)
        finally:
            print("cleaning up thread", datafile)

    def processHistogram(self, datafile, q):
        outputdir = dirname(datafile)  # same dir as inputfile Filtered*
        fd = HistogramLogD(self.minlimit, self.maxlimit, self.binwidth, datafile, self.configfile)
        q[datafile] = fd.generateHistogram(outputdir)

    def ShowFeedBack(self, show):
        # self.result.Show(not show)
        if show:
            self.timer.Start(250)
        else:
            self.timer.Stop()

    def processTest(self,datafile,q):
        result = 0
        for i in range(10):
            result += i
        q[datafile] = result

    def RunFilterThread(self, wxGui,filenames, row=0):
        print("Running Filter Thread - start")
        FilterThread(self,wxGui,filenames, row)
        print("Running Filter Thread - complete")
        return len(filenames)


    def RunFilter(self, filenames, progressfunc=None,row=None):
        """

        :param event:
        :param filenames:
        :return:
        """
        if len(filenames) > 0:
            total_tasks = len(filenames)
            tasks = []
            mm = Manager()
            self.ShowFeedBack(True)
            try:
                q = mm.dict()
                for i in range(total_tasks):
                    self.count = 1
                    p = Process(target=self.processTest, args=(filenames[i], q))
                    p.start()
                    tasks.append(p)

                    print('loop1: timer is running=', self.timer.IsRunning())
                try:
                    for p in tasks:
                        p.join()
                        self.count = self.count + 10
                        wx.CallAfter(progressfunc, self.count, row, 1)

                        print('loop2: timer is running=', self.timer.IsRunning())

                except KeyboardInterrupt:
                    print("Keyboard interrupt in main")

                headers = ['Data', 'MSD', 'Total', 'Filtered', 'Total_MSD', 'Filtered_MSD']
                results = pd.DataFrame.from_dict(q, orient='index')
                #results.columns = headers
                self.ShowFeedBack(False)
                return results
            finally:
                # to be safe -- explicitly shutting down the manager
                mm.shutdown()
        else:
            #logger("Error:Cannot find any datafiles: %s" % self.datafile)
            return 0



    def RunHistogram(self, event, result):
        type = 'histo'
        self.ShowFeedBack(True)
        # find datafile - assume same directory for msd file
        #result = [y for x in walk(self.inputdir) for y in glob(join(x[0], self.filteredfname))]
        if len(result) > 0:
            total_tasks = len(result)
            tasks = []
            mm = Manager()
            q = mm.dict()
            for i in range(total_tasks):
                self.count = 1
                self.StatusBar.SetStatusText(
                    "Running %s script: %s (%d of %d)" % (type.title(), result[i], i, total_tasks))
                p = Process(target=self.processHistogram, args=(result[i], q))

                tasks.append(p)
                p.start()

            for p in tasks:
                self.gauge_histo.SetFocus()
                while p.is_alive():
                    time.sleep(1)
                    self.count = self.count + 1
                    self.gauge_histo.SetValue(self.count)
                p.join()

            headers = ['Figure', 'Histogram data']
            results = pd.DataFrame.from_dict(q, orient='index')
            results.columns = headers
            for i, row in results.iterrows():
                self.resultbox.AppendText("HISTOGRAM: %s\n\t%s\n\t%s\n" % (
                    i, row['Figure'], row['Histogram data']))
            self.result_histo.SetLabel("Complete")

        else:
            self.Warn("Cannot find any datafiles: %s" % self.filteredfname)

        self.ShowFeedBack(False, type)

    def RunStats(self, event, expt=None):
        type = 'stats'
        if expt is None:
            expt = ''
        self.ShowFeedBack(True, type)
        # loop through directory structure and locate prefixes with expt name
        try:
            for prefix in self.prefixes:
                print("Group:", prefix)
                self.statusbar.SetStatusText("Running %s script: %s (%s)" % (type.title(), expt, prefix))
                self.gauge_stats.SetFocus()
                fmsd = HistoStats(self.inputdir, self.outputdir, prefix, expt, self.configfile)
                fmsd.compile()
                compiledfile = fmsd.runStats()
                # Split to Mobile/immobile fractions - output
                ratiofile = fmsd.splitMobile()
                self.resultbox.AppendText(
                    "HISTOGRAM BATCH: %s: %s\n\t%s\n\t%s\n" % (expt, prefix, compiledfile, ratiofile))
                self.result_stats.SetLabel("Complete - Close plot to continue")
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
        except ValueError as e:
            self.Warn("Batch Histogram error: %s" % e.message)

        self.ShowFeedBack(False, type)

    def RunMSD(self, event, expt=None):
        type = 'msd'
        if expt is None:
            expt = ''
        self.ShowFeedBack(True, type)
        # loop through directory
        for prefix in self.prefixes:
            self.statusbar.SetStatusText("Running %s script: %s (%s)" % (type.title(), expt, prefix))
            self.gauge_msd.SetFocus()
            fmsd = CompareMSD(self.inputdir, self.outputdir, prefix, expt, self.configfile)
            compiledfile = fmsd.compile()
            self.resultbox.AppendText("MSD BATCH: %s: %s\n\t%s\n\t%s\n" % (expt, prefix, compiledfile, areasfile))
            self.result_msd.SetLabel("Complete")
            # Set the figure
            fig = plt.figure(figsize=(10, 5))
            axes1 = plt.subplot(121)
            areasfile = fmsd.showPlotsWithAreas(axes1)

            axes2 = plt.subplot(122)
            fmsd.showAvgPlot(axes2)

            figtype = 'png'  # png, pdf, ps, eps and svg.
            figname = fmsd.compiledfile.replace('csv', figtype)
            plt.savefig(figname, facecolor='w', edgecolor='w', format=figtype)
            plt.show()

        self.ShowFeedBack(False, type)
