#import images
import logging
import time
from glob import glob
from multiprocessing import Manager, Process
from os import access, R_OK, walk, mkdir
from os.path import join, expanduser, dirname, exists

import matplotlib.pyplot as plt
import pandas as pd
import wx
from configobj import ConfigObj
from collections import OrderedDict
from msdapp.guicontrollers import MSDController
from msdapp.msd.batchCompareMSD import CompareMSD
from msdapp.msd.batchHistogramStats import HistoStats
from msdapp.msd.filterMSD import FilterMSD
from msdapp.msd.histogramLogD import HistogramLogD
from noname import ConfigPanel, FilesPanel, ComparePanel, WelcomePanel, ProcessPanel


########################################################################
class HomePanel(WelcomePanel):
    """
    This will be the first notebook tab
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """"""

        super(HomePanel, self).__init__(parent)
        self.m_richText1.AddParagraph("Welcome to the MSD Automated Analysis App")
        self.m_richText1.AddParagraph(self.__loadContent())
        self.m_richText1.AddParagraph("Any queries, contact Liz Cooper-Williams e.cooperwilliams@uq.edu.au\nCopyright (2017) Apache license v2 (https://github.com/QBI-Software/MSDAnalysis)")

    def __loadContent(self):
        """
        Welcome text
        :return:
        """
        content = '''
        To process your files: 
            1. Check the Configuration options, particularly the column names and filenames used for matching
            2. Select Files to process either with AutoFind from a top level and/or Drag and Drop
            3. Select which processes to run and monitor their progress
            4. Run a statistical comparison of two groups after processing files have been generated
       
        '''
        return content

########################################################################
class MSDConfig(ConfigPanel):
    def __init__(self, parent):
        super(MSDConfig, self).__init__(parent)
        self.encoding = 'ISO-8859-1'
        if parent.loaded:
            self.__loadValues(parent)

    def __loadValues(self, parent):
        print("Config loaded")
        self.m_textCtrl15.SetValue(parent.datafile)
        self.m_textCtrl16.SetValue(parent.msdfile)
        self.m_textCtrl1.SetValue(parent.histofile)
        self.m_textCtrl2.SetValue(parent.filteredfname)
        self.m_textCtrl3.SetValue(parent.filtered_msd)
        self.m_textCtrl4.SetValue(parent.msdpoints)
        self.m_textCtrl5.SetValue(parent.timeint)
        self.m_textCtrl8.SetValue(parent.diffcolumn)
        self.m_textCtrl9.SetValue(parent.logcolumn)
        self.m_textCtrl10.SetValue(parent.minlimit)
        self.m_textCtrl11.SetValue(parent.maxlimit)
        self.m_textCtrl12.SetValue(parent.binwidth)
        self.m_textCtrl13.SetValue(parent.threshold)
        self.m_textCtrl161.SetValue(parent.allstats)
        self.m_textCtrl18.SetValue(parent.msdcompare)
        self.m_tcGroup1.SetValue(parent.group1)
        self.m_tcGroup2.SetValue(parent.group2)

    def OnSaveConfig(self, event):
        print("In config - onsave - saving to cfg file")
        config = ConfigObj()
        config.filename = join(expanduser('~'), '.msdcfg')
        config.encoding = self.encoding
        config['DATA_FILENAME'] = self.m_textCtrl15.GetValue()
        config['MSD_FILENAME'] = self.m_textCtrl16.GetValue()
        config['HISTOGRAM_FILENAME'] = self.m_textCtrl1.GetValue()
        config['FILTERED_FILENAME'] = self.m_textCtrl2.GetValue()
        config['FILTERED_MSD'] = self.m_textCtrl3.GetValue()
        config['LOG_COLUMN'] = self.m_textCtrl9.GetValue()
        config['DIFF_COLUMN'] = self.m_textCtrl8.GetValue()
        config['MSD_POINTS'] = self.m_textCtrl4.GetValue()
        config['MINLIMIT'] = self.m_textCtrl10.GetValue()
        config['MAXLIMIT'] = self.m_textCtrl11.GetValue()
        config['TIME_INTERVAL'] = self.m_textCtrl5.GetValue()
        config['BINWIDTH'] = self.m_textCtrl12.GetValue()
        config['THRESHOLD'] = self.m_textCtrl13.GetValue()
        config['ALLSTATS_FILENAME'] = self.m_textCtrl161.GetValue()
        config['AVGMSD_FILENAME'] = self.m_textCtrl18.GetValue()
        config['GROUP1'] = self.m_tcGroup1.GetValue()
        config['GROUP2'] = self.m_tcGroup2.GetValue()
        config.write()
        event.Skip()

    def OnLoadConfig(self,event):
        print("Load From Config dialog")
        openFileDialog = wx.FileDialog(self, "Open config file", "", "", "Config files (*.cfg)|*",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR)
        openFileDialog.SetDirectory(expanduser('~'))
        if openFileDialog.ShowModal() == wx.ID_OK:
            self.configfile = str(openFileDialog.GetPath())
            self.loaded = self.__loadConfig()
            self.statusbar.SetStatusText("Config Loaded: %s\n" % self.configfile)
            self.Warn("Save new Config from Config->Edit->Save")
        openFileDialog.Destroy()

########################################################################
class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, target):
        super(MyFileDropTarget, self).__init__()
        self.target = target

    def OnDropFiles(self, x, y, filenames):
        for fname in filenames:
            self.target.AppendItem([True,fname])
        return len(filenames)

########################################################################
class FileSelectPanel(FilesPanel):
    def __init__(self,parent):
        super(FileSelectPanel, self).__init__(parent)
        self.m_dataViewListCtrl1.GetColumn(0).SetMinWidth(20)
        self.m_dataViewListCtrl1.GetColumn(1).SetMinWidth(200)

        self.filedrop = MyFileDropTarget(self.m_dataViewListCtrl1)
        self.m_tcDragdrop.SetDropTarget(self.filedrop)
        self.datafile = parent.datafile

    def OnInputdir(self, e):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory containing input files")
        if dlg.ShowModal() == wx.ID_OK:
            self.inputdir = str(dlg.GetPath())
            #self.statusbar.SetStatusText("Loaded: %s" % self.inputdir)
            self.txtInputdir.SetValue(self.inputdir)
        dlg.Destroy()

    def OnOutputdir(self, e):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory for output files")
        if dlg.ShowModal() == wx.ID_OK:
            self.outputdir = str(dlg.GetPath())
            #self.statusbar.SetStatusText("Loaded: %s\n" % self.outputdir)
            self.txtOutputdir.SetValue(self.outputdir)
        dlg.Destroy()

    def OnAutofind(self, event):
        filenames = [y for x in walk(self.inputdir) for y in glob(join(x[0], self.datafile))]
        for fname in filenames:
            self.m_dataViewListCtrl1.AppendItem([True,fname])
        print("Total Files loaded: ", self.m_dataViewListCtrl1.GetItemCount())

    def OnSelectall(self, event):
        for i in range(0, self.m_dataViewListCtrl1.GetItemCount()):
            self.m_dataViewListCtrl1.SetToggleValue(event.GetSelection(),i,0)
        print("Toggled selections to: ", event.GetSelection())

    def OnClearlist(self, event):
        print("Clear items in list")
        self.m_dataViewListCtrl1.DeleteAllItems()

class ProcessRunPanel(ProcessPanel):
    def __init__(self, parent):
        super(ProcessRunPanel, self).__init__(parent)
        self.processes = list(parent.processes.values())
        #self.m_sProcess.AppendItems(self.processes)


########################################################################
class AppMain(wx.Listbook):
    """"""

    # ----------------------------------------------------------------------

    def __init__(self, parent):
        """Constructor"""
        wx.Listbook.__init__(self, parent, wx.ID_ANY, style=
        wx.BK_DEFAULT
                             # wx.BK_TOP
                             # wx.BK_BOTTOM
                             # wx.BK_LEFT
                             # wx.BK_RIGHT
                             )

        logging.basicConfig(filename='msdanalysis.log', level=logging.INFO, format='%(asctime)s %(message)s',
                            datefmt='%d-%m-%Y %I:%M:%S %p')
        self.encoding = 'ISO-8859-1'
        self.configfile = "msdapp\\msd.cfg" #join(expanduser('~'), '.msdcfg')
        self.loaded = self.__loadConfig()
        if self.loaded:
            self.prefixes = [self.group1, self.group2]
        else:
            self.prefixes = ['stim', 'nostim']  # default
        self.processes =OrderedDict({'filter':'Filter data','histo':'Generate Histograms','stats':'Compile All Histograms','msd':'Compile All MSD'})
        self.controller = MSDController(self.configfile)
        self.InitUI()
        self.Centre()
        self.Show()

    def __loadConfig(self):
        if self.configfile is not None:
            try:
                if access(self.configfile, R_OK):
                    print("Loading config file")
                    config = ConfigObj(self.configfile, encoding='ISO-8859-1')
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
                    return True

            except:
                raise IOError
        return False

    def InitUI(self):
        # make an image list using the LBXX images
        # il = wx.ImageList(32, 32)
        # # for x in [wx.ArtProvider.]:
        # #     obj = getattr(images, 'LB%02d' % (x + 1))
        # #     bmp = obj.GetBitmap()
        # #     il.Add(bmp)
        # bmp = wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_FRAME_ICON, (16, 16))
        # il.Add(bmp)
        # bmp = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_FRAME_ICON, (16, 16))
        # il.Add(bmp)
        # bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_FRAME_ICON, (16, 16))
        # il.Add(bmp)
        # self.AssignImageList(il)

        pages = [(HomePanel(self),"Welcome"),
                 (MSDConfig(self), "Configure"),
                 (FileSelectPanel(self), "Select Files"),
                 (ProcessPanel(self), "Run Processes"),
                 (ComparePanel(self),"Compare Groups")]
        imID = 0
        for page, label in pages:
            #self.AddPage(page, label, imageId=imID)
            self.AddPage(page, label)
            imID += 1

        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGING, self.OnPageChanging)

    # ----------------------------------------------------------------------
    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        msg = 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        print(msg)
        event.Skip()

    # ----------------------------------------------------------------------
    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        msg = 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        print(msg)
        event.Skip()
    def Warn(self, message, caption='Warning!'):
        dlg = wx.MessageDialog(self, message, caption, wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

    def ShowFeedBack(self, show, type):
        if type == 'filter':
            self.gauge_filter.Show(show)
        elif type == 'histo':
            self.gauge_histo.Show(show)
        elif type == 'stats':
            self.gauge_stats.Show(show)
        elif type == 'msd':
            self.gauge_msd.Show(show)
        # self.result.Show(not show)
        if show:
            self.timer.Start(250)
        else:
            self.timer.Stop()
        self.Layout()

    def OnRunScripts(self, e):
        """
        Run selected scripts sequentially - updating progress bars
        :param e:
        :return:
        """
        if len(self.txtInputdir.GetValue()) == 0:
            self.Warn("Input files not specified")
            return 0
        else:
            self.inputdir = self.txtInputdir.GetValue()
            if not access(self.inputdir, R_OK):
                self.Warn("Input directory is not accessible - check permissions")
                return 0
        if len(self.txtOutputdir.GetValue()) == 0:
            self.Warn("Output directory not specified")
            return 0
        else:
            self.outputdir = self.txtOutputdir.GetValue()
            if not access(self.outputdir, R_OK):
                self.Warn("Output directory is not accessible - check permissions")
                return 0
        expt = self.txtProtein.GetValue() + self.txtCelltype.GetValue()
        print("Expt:", expt)
        self.timer = wx.Timer(self)
        if self.cb1.GetValue():
            self.StatusBar.SetStatusText("Running Filter script")

            self.Bind(wx.EVT_TIMER,
                      lambda e: self.gauge_filter.Pulse(),
                      self.timer)
            self.RunFilter(e)

        if self.cb2.GetValue():
            self.StatusBar.SetStatusText("Running Histogram script")
            self.Bind(wx.EVT_TIMER,
                      lambda e: self.gauge_histo.Pulse(),
                      self.timer)
            self.RunHistogram(e)

        if self.cb3.GetValue():
            self.StatusBar.SetStatusText("Running Stats script")
            self.Bind(wx.EVT_TIMER,
                      lambda e: self.gauge_stats.Pulse(),
                      self.timer)
            self.RunStats(e, expt)

        if self.cb4.GetValue():
            self.StatusBar.SetStatusText("Running MSD compare script")
            self.Bind(wx.EVT_TIMER,
                      lambda e: self.gauge_msd.Pulse(),
                      self.timer)
            self.RunMSD(e, expt)

    def processFilter(self, datafile, q):
        """
        Activate filter process - multithreaded
        :param datafile:
        :param q:
        :return:
        """
        datafile_msd = datafile.replace(self.datafile, self.msdfile)
        outputdir = join(dirname(datafile), 'processed')  # subdir as inputfiles
        if not exists(outputdir):
            mkdir(outputdir)
        fmsd = FilterMSD(self.configfile, datafile, datafile_msd, outputdir, self.minlimit, self.maxlimit)
        q[datafile] = fmsd.runFilter()

    def processHistogram(self, datafile, q):
        outputdir = dirname(datafile)  # same dir as inputfile Filtered*
        fd = HistogramLogD(self.minlimit, self.maxlimit, self.binwidth, datafile, self.configfile)
        q[datafile] = fd.generateHistogram(outputdir)

    def RunFilter(self, event):
        type = 'filter'
        self.ShowFeedBack(True, type)
        # find datafile - assume same directory for msd file
        result = [y for x in walk(self.inputdir) for y in glob(join(x[0], self.datafile))]

        if len(result) > 0:
            total_tasks = len(result)
            tasks = []
            mm = Manager()
            q = mm.dict()

            for i in range(total_tasks):
                self.count = 1
                self.StatusBar.SetStatusText(
                    "Running %s script: %s (%d of %d)" % (type.title(), result[i], i, total_tasks))
                p = Process(target=self.processFilter, args=(result[i], q))
                tasks.append(p)
                p.start()

            for p in tasks:
                self.gauge_filter.SetFocus()
                while p.is_alive():
                    time.sleep(1)
                    self.count = self.count + 1
                    self.gauge_filter.SetValue(self.count)
                p.join()

            headers = ['Data', 'MSD', 'Total', 'Filtered', 'Total_MSD', 'Filtered_MSD']
            results = pd.DataFrame.from_dict(q, orient='index')
            results.columns = headers
            for i, row in results.iterrows():
                self.resultbox.AppendText("FILTER: %s\n\t%d of %d rows filtered\n\t%s\n\t%s\n" % (
                    i, row['Filtered'], row['Total'], row['Data'], row['MSD']))
            self.result_filter.SetLabel("Complete")

        else:
            self.Warn("Cannot find any datafiles: %s" % self.datafile)

        self.ShowFeedBack(False, type)

    def RunHistogram(self, event):
        type = 'histo'
        self.ShowFeedBack(True, type)
        # find datafile - assume same directory for msd file
        result = [y for x in walk(self.inputdir) for y in glob(join(x[0], self.filteredfname))]
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

    def RunStats(self, event,expt=None):
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
                self.resultbox.AppendText("HISTOGRAM BATCH: %s: %s\n\t%s\n\t%s\n" % (expt, prefix, compiledfile, ratiofile))
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

    def RunMSD(self, event,expt=None):
        type = 'msd'
        if expt is None:
            expt = ''
        self.ShowFeedBack(True, type)
        # loop through directory
        for prefix in self.prefixes:
            self.statusbar.SetStatusText("Running %s script: %s (%s)" % (type.title(),expt, prefix))
            self.gauge_msd.SetFocus()
            fmsd = CompareMSD(self.inputdir, self.outputdir, prefix, expt,self.configfile)
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



    def OnQuit(self, e):
        self.Close()

    def OnCloseWindow(self, e):

        dial = wx.MessageDialog(None, 'Are you sure you want to quit?', 'Question',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        ret = dial.ShowModal()

        if ret == wx.ID_YES:
            self.Destroy()
        else:
            e.Veto()

########################################################################
class MSDFrame(wx.Frame):
    """
    Frame that holds all other widgets
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "MSD Autoanalysis",
                          size=(700, 400)
                          )
        panel = wx.Panel(self)

        notebook = AppMain(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()

        self.Show()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = MSDFrame()
    app.MainLoop()