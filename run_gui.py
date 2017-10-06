# -*- coding: utf-8 -*-

# center.py

import time
from glob import glob
from multiprocessing import Manager, Process
from os import access, R_OK, walk, mkdir
from os.path import join, expanduser, dirname, exists, split

import matplotlib.pyplot as plt
import pandas as pd
import wx
from configobj import ConfigObj

from msdapp.msd.batchCompareMSD import CompareMSD
from msdapp.msd.batchHistogramStats import HistoStats
from msdapp.msd.filterMSD import FilterMSD
from msdapp.msd.histogramLogD import HistogramLogD
from msdapp.msd.ratioStats import RatioStats
from noname import AppConfiguration, RatioStatsDialog

APP_EXIT = 1

############Config dialog
class MSDConfig(AppConfiguration):
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
        config.write()
        event.Skip()

class RatioApp(RatioStatsDialog):
    def __init__(self, parent):
        super(RatioApp, self).__init__(parent)
        self.outputdir = parent.outputdir
        self.Bind(wx.EVT_BUTTON, self.OnRatiofile1, self.m_btnGp1)
        self.Bind(wx.EVT_BUTTON, self.OnRatiofile2, self.m_btnGp2)
        self.Bind(wx.EVT_BUTTON, self.OnRun, self.m_btnRatioRun)

    def OnRatiofile1(self, e):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a File for Group 1", self.outputdir)
        if dlg.ShowModal() == wx.ID_OK:
            filename = str(dlg.GetPath())
            self.m_tcRatioFile1.SetValue(filename)
        dlg.Destroy()

    def OnRatiofile2(self, e):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a File for Group 2", self.outputdir)
        if dlg.ShowModal() == wx.ID_OK:
            filename = str(dlg.GetPath())
            self.m_tcRatioFile2.SetValue(filename)
        dlg.Destroy()

    def OnRun(self,e):
        """
        Run Ratio Analysis
        :param e:
        :return:
        """
        file1 = self.m_tcRatioFile1.GetValue()
        file2 = self.m_tcRatioFile2.GetValue()
        label1 = self.m_textCtrlGp1.GetValue()
        label2 = self.m_textCtrlGp2.GetValue()
        self.m_tcResults.AppendText("T-test on TWO RELATED samples of scores\nSignificance of 0.05\n--------------------------------------\n")
        rs = RatioStats(file1, file2,label1, label2)
        (dstats, p) = rs.runStats()
        results="T-test\t\t\tp-value\t\t\tsignificance\n%s\t\t\t%s\t\t\t%s\n" % (dstats, str(p), str(p < 0.05))
        self.m_tcResults.AppendText(results)

    def OnClose(self, e):
        self.Close()

####Main GUI
class ScriptController(wx.Frame):
    def __init__(self, parent, title):
        super(ScriptController, self).__init__(parent, title=title, size=(600, 800))
        self.encoding = 'ISO-8859-1'
        self.configfile = join(expanduser('~'), '.msdcfg')
        self.loaded = self.__loadConfig()
        self.InitUI()
        self.Centre()
        self.Show()

    def __loadConfig(self):
        if self.configfile is not None:
            try:
                if access(self.configfile, R_OK):
                    print("Loading config file")
                    config = ConfigObj(self.configfile, encoding='ISO-8859-1')
                    self.datafile = config['DATA_FILENAME']  # AllROI.txt
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
                    return True

            except:
                raise IOError
        return False

    def InitUI(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_NEW, '&New\tCtrl+N')
        fileMenu.Append(wx.ID_OPEN, '&Open\tCtrl+O')
        fileMenu.Append(wx.ID_SAVE, '&Save\tCtrl+S')
        fileMenu.AppendSeparator()
        # menu_quit = wx.MenuItem(fileMenu, APP_EXIT, '&Quit\tCtrl+Q')
        fitem = fileMenu.Append(wx.ID_EXIT, '&Quit\tCtrl+Q', 'Quit application')

        configMenu = wx.Menu()
        menu_load = wx.MenuItem(configMenu, wx.ID_ANY, '&Load\tCtrl+L')
        menu_config = wx.MenuItem(configMenu, wx.ID_ANY, '&Edit\tCtrl+E')
        configMenu.Append(menu_load)
        configMenu.Append(menu_config)

        menubar.Append(fileMenu, '&File')
        menubar.Append(configMenu, '&Config')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
        self.Bind(wx.EVT_MENU, self.OnConfig, menu_config)
        self.Bind(wx.EVT_MENU, self.OnLoadConfig, menu_load)
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('Ready')

        ######Main content
        panel = wx.Panel(self)
        ##Fonts
        font_header = wx.Font(14, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        font_description = wx.Font(10, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        #####Input files
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.btnInputdir = wx.Button(panel, label='Input directory')
        hbox1.Add(self.btnInputdir, flag=wx.RIGHT, border=8)
        self.txtInputdir = wx.TextCtrl(panel)
        hbox1.Add(self.txtInputdir, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))
        ####Output directory
        hbox1a = wx.BoxSizer(wx.HORIZONTAL)
        self.btnOutputdir = wx.Button(panel, label='Output directory')
        hbox1a.Add(self.btnOutputdir, flag=wx.RIGHT, border=8)
        self.txtOutputdir = wx.TextCtrl(panel)
        hbox1a.Add(self.txtOutputdir, proportion=1)
        vbox.Add(hbox1a, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='Processing scripts should run in sequence')
        st2.SetFont(font_description)
        hbox2.Add(st2)

        vbox.Add(hbox2, flag=wx.LEFT | wx.TOP, border=10)

        vbox.Add((-1, 10))
        #### Sequence scripts buttons
        grid = wx.FlexGridSizer(5, 2, 10, 10)
        self.cb1 = wx.CheckBox(panel, label='Filter log10 D')
        self.cb2 = wx.CheckBox(panel, label='Histogram log10 D')
        self.cb3 = wx.CheckBox(panel, label='Batch Histogram Stats')
        self.cb4 = wx.CheckBox(panel, label='Batch Compare MSD')
        # cb5 = wx.CheckBox(panel, label='Ratio Stats')

        st_cb = wx.StaticText(panel, label='Script')
        st_cb.SetFont(font_header)
        st_opt = wx.StaticText(panel, label='Processing')
        st_opt.SetFont(font_header)

        vbox.Add((-1, 10))
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        self.result_filter = wx.StaticText(panel, label='1')
        self.gauge_filter = wx.Gauge(panel)
        self.result_histo = wx.StaticText(panel, label='2')
        self.gauge_histo = wx.Gauge(panel)
        self.result_stats = wx.StaticText(panel, label='3')
        self.gauge_stats = wx.Gauge(panel)
        self.result_msd = wx.StaticText(panel, label='4')
        self.gauge_msd = wx.Gauge(panel)
        flags = wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL
        hbox4.AddMany([(self.result_filter,flags), (5,5),(self.gauge_filter, 0, flags, 5)])
        hbox5.AddMany([(self.result_histo,flags), (5,5),(self.gauge_histo, 0, flags, 5)])
        hbox6.AddMany([(self.result_stats,flags), (5,5),(self.gauge_stats, 0, flags, 5)])
        hbox7.AddMany([(self.result_msd,flags), (5,5),(self.gauge_msd, 0, flags, 5)])

        grid.AddMany([(st_cb, 0, wx.TOP | wx.LEFT, 12),
                      (st_opt, 0, wx.TOP | wx.RIGHT, 12),
                      (self.cb1, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 9),
                      (hbox4, 0, wx.ALIGN_LEFT, 9),
                      (self.cb2, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 9),
                      (hbox5, 0, wx.ALIGN_LEFT, 9),
                      (self.cb3, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 9),
                      (hbox6, 0, wx.ALIGN_LEFT, 9),
                      (self.cb4, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 9),
                      (hbox7, 0, wx.ALIGN_LEFT, 9)
                      ])
        grid.AddGrowableCol(1, 1)
        vbox.Add(grid, flag=wx.LEFT, border=10)

        ### OUTPUT panel
        vbox.Add((-1, 25))

        hbox9 = wx.BoxSizer(wx.HORIZONTAL)
        self.resultbox = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        hbox9.Add(self.resultbox, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox9, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND,
                 border=10)

        vbox.Add((-1, 25))

        hbox_btns = wx.BoxSizer(wx.HORIZONTAL)
        btnRatio = wx.Button(panel, label='Ratio Stats (STIM vs NOSTIM)', size=(200, 30))
        hbox_btns.Add(btnRatio, flag=wx.LEFT, border=5)
        btnRun = wx.Button(panel, label='Run selected', size=(100, 30))
        hbox_btns.Add(btnRun)
        btn2 = wx.Button(panel, label='Close', size=(70, 30))
        hbox_btns.Add(btn2, flag=wx.LEFT | wx.BOTTOM, border=5)
        vbox.Add(hbox_btns, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)

        panel.SetSizer(vbox)
        # Actions
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_BUTTON, self.OnCloseWindow, btn2)
        self.Bind(wx.EVT_BUTTON, self.OnRunScripts, btnRun)
        self.Bind(wx.EVT_BUTTON, self.OnInputdir, self.btnInputdir)
        self.Bind(wx.EVT_BUTTON, self.OnOutputdir, self.btnOutputdir)
        self.Bind(wx.EVT_BUTTON, self.OnRatios, btnRatio)

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

        if len(self.txtOutputdir.GetValue()) == 0:
            self.Warn("Output directory not specified")
            return 0
        else:
            self.outputdir = self.txtOutputdir.GetValue()
        self.timer = wx.Timer(self)
        if self.cb1.GetValue():
            self.StatusBar.SetStatusText("Running Filter script")

            self.Bind(wx.EVT_TIMER,
                      lambda e: self.gauge_filter.Pulse(),
                      self.timer)
            self.RunFilter(e)

        if self.cb2.GetValue():
            self.StatusBar.SetStatusText("Running Histogram script")
            # self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER,
                      lambda e: self.gauge_histo.Pulse(),
                      self.timer)
            self.RunHistogram(e)

        if self.cb3.GetValue():
            self.StatusBar.SetStatusText("Running Stats script")
            self.Bind(wx.EVT_TIMER,
                      lambda e: self.gauge_stats.Pulse(),
                      self.timer)
            self.RunStats(e)

        if self.cb4.GetValue():
            self.StatusBar.SetStatusText("Running MSD compare script")
            self.Bind(wx.EVT_TIMER,
                      lambda e: self.gauge_msd.Pulse(),
                      self.timer)
            self.RunMSD(e)

    def processFilter(self, datafile, q):
        datafile_msd = datafile.replace(self.datafile, self.msdfile)
        outputdir = join(dirname(datafile), 'output')  # subdir as inputfiles
        if not exists(outputdir):
            mkdir(outputdir)
        fmsd = FilterMSD(self.configfile, datafile, datafile_msd, outputdir, int(self.minlimit), int(self.maxlimit))
        q[datafile] = fmsd.runFilter()

    def processHistogram(self, datafile, q):
        outputdir = dirname(datafile)  # same dir as inputfile
        fd = HistogramLogD(self.minlimit, self.maxlimit, self.binwidth, datafile, self.configfile)
        q[datafile] = fd.generateHistogram(outputdir)

    def RunFilter(self, event):
        type = 'filter'
        self.ShowFeedBack(True, type)
        # loop through directory
        if access(self.inputdir, R_OK):
            # find datafile - assume same directory for msd file
            result = [y for x in walk(self.inputdir) for y in glob(join(x[0], self.datafile))]

            if len(result) > 0:
                total_tasks = len(result)
                tasks = []
                mm = Manager()
                q = mm.dict()
                self.count = 1
                for i in range(total_tasks):
                    self.StatusBar.SetStatusText("Running %s script: %s" % (type.title(), result[i]))
                    p = Process(target=self.processFilter, args=(result[i], q))
                    self.result_filter.SetLabel("%d of %d" % (i, total_tasks))
                    tasks.append(p)
                    p.start()
                    self.gauge_filter.FindFocus()
                    while p.is_alive():
                        time.sleep(1)
                        self.count = self.count + 1
                        self.gauge_filter.SetValue(self.count)
                    self.count = 1

                for p in tasks:
                    p.join()

                headers = ['Data', 'MSD', 'Total', 'Filtered', 'Total_MSD', 'Filtered_MSD']
                results = pd.DataFrame.from_dict(q, orient='index')
                results.columns = headers
                for i, row in results.iterrows():
                    self.resultbox.AppendText("FILTER: %s\n\t%d of %d rows filtered\n\t%s\n\t%s\n" % (
                        i, row['Filtered'], row['Total'], row['Data'], row['MSD']))
                self.result_filter.SetLabel("Complete")

            else:
                self.Warn("Cannot find datafile: %s" % self.datafile)
        else:
            self.Warn("Cannot access input directory: %s" % self.inputdir)
        self.ShowFeedBack(False, type)

    def RunHistogram(self, event):
        type = 'histo'
        self.ShowFeedBack(True, type)
        # loop through directory
        if access(self.inputdir, R_OK):
            # find datafile - assume same directory for msd file
            result = [y for x in walk(self.inputdir) for y in glob(join(x[0], self.filteredfname))]
            if len(result) > 0:
                total_tasks = len(result)
                tasks = []
                mm = Manager()
                q = mm.dict()
                self.count = 1
                for i in range(total_tasks):
                    self.StatusBar.SetStatusText("Running %s script: %s" % (type.title(), result[i]))
                    p = Process(target=self.processHistogram, args=(result[i], q))
                    self.result_histo.SetLabel("%d of %d" % (i, total_tasks))
                    tasks.append(p)
                    p.start()
                    self.gauge_histo.FindFocus()
                    while p.is_alive():
                        time.sleep(1)
                        self.count = self.count + 1
                        self.gauge_histo.SetValue(self.count)
                    self.count = 1

                for p in tasks:
                    p.join()

                headers = ['Figure', 'Histogram data']
                results = pd.DataFrame.from_dict(q, orient='index')
                results.columns = headers
                for i, row in results.iterrows():
                    self.resultbox.AppendText("HISTOGRAM: %s\n\t%s\n\t%s\n" % (
                        i, row['Figure'], row['Histogram data']))
                self.result_histo.SetLabel("Complete")

            else:
                self.Warn("Cannot find datafile: %s" % self.filteredfname)
        else:
            self.Warn("Cannot access input directory: %s" % self.inputdir)
        self.ShowFeedBack(False, type)

    def RunStats(self, event):
        type = 'stats'
        self.ShowFeedBack(True, type)
        # loop through directory
        if access(self.inputdir, R_OK):
            prefix = split(self.inputdir)[1]
            if len(prefix) == 0:
                self.statusbar.SetStatusText("Prefix not found - using ALL")
                prefix = 'ALL'
            self.statusbar.SetStatusText("Running %s script: %s" % (type.title(), prefix))
            self.gauge_stats.FindFocus()
            fmsd = HistoStats(self.inputdir, self.outputdir, float(self.threshold), prefix,
                              self.configfile)
            fmsd.compile()
            compiledfile = fmsd.runStats()
            # Split to Mobile/immobile fractions - output
            ratiofile = fmsd.splitMobile()
            self.resultbox.AppendText("HISTOGRAM STATS: %s\n\t%s\n\t%s\n" % (prefix, compiledfile, ratiofile))
            self.result_stats.SetLabel("Complete")
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

        else:
            self.Warn("Cannot access input directory: %s" % self.inputdir)
        self.ShowFeedBack(False, type)

    def RunMSD(self, event):
        type = 'msd'
        self.ShowFeedBack(True, type)
        # loop through directory
        if access(self.inputdir, R_OK):
            prefix = split(self.inputdir)[1]
            if len(prefix) == 0:
                self.statusbar.SetStatusText("Prefix not found - using ALL")
                prefix = 'ALL'
            self.statusbar.SetStatusText("Running %s script: %s" % (type.title(), prefix))
            self.gauge_msd.FindFocus()
            fmsd = CompareMSD(self.inputdir, self.outputdir, prefix, self.configfile)
            compiledfile = fmsd.compile()

            self.resultbox.AppendText("MSD STATS: %s\n\t%s\n" % (prefix, compiledfile))
            self.result_msd.SetLabel("Complete")

        else:
            self.Warn("Cannot access input directory: %s" % self.inputdir)
        self.ShowFeedBack(False, type)

    def OnInputdir(self, e):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory containing input files")
        if dlg.ShowModal() == wx.ID_OK:
            self.inputdir = str(dlg.GetPath())
            self.statusbar.SetStatusText("Loaded: %s" % self.inputdir)
            self.txtInputdir.SetValue(self.inputdir)
        dlg.Destroy()

    def OnOutputdir(self, e):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory for output files")
        if dlg.ShowModal() == wx.ID_OK:
            self.outputdir = str(dlg.GetPath())
            self.statusbar.SetStatusText("Loaded: %s\n" % self.outputdir)
            self.txtOutputdir.SetValue(self.outputdir)
        dlg.Destroy()


    def OnQuit(self, e):
        self.Close()

    def OnConfig(self, e):
        configdlg = MSDConfig(self)
        self.Bind(wx.EVT_BUTTON, self.OnSaveConfig, configdlg.btnSave)
        configdlg.Show(True)

    def OnRatios(self, e):
        dlg = RatioApp(self)
        dlg.Show(True)

    def OnCloseWindow(self, e):

        dial = wx.MessageDialog(None, 'Are you sure you want to quit?', 'Question',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        ret = dial.ShowModal()

        if ret == wx.ID_YES:
            self.Destroy()
        else:
            e.Veto()

    ###Propagated from config dialog
    def OnLoadConfig(self, event):
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

    def OnSaveConfig(self, event):
        print("Save From Config dialog")
        self.configfile = join(expanduser('~'), '.msdcfg')
        self.loaded = self.__loadConfig()
        if self.loaded:
            self.statusbar.SetStatusText("Config saved")
            # event.Veto()
        else:
            self.statusbar.SetStatusText("ERROR: Save Config failed")


def main():
    app = wx.App()
    ScriptController(None, title='MSD Analysis')
    app.MainLoop()


####################################################################
if __name__ == '__main__':
    main()
