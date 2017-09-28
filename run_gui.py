# -*- coding: utf-8 -*-

# center.py

import wx
from os.path import join, expanduser, dirname
from os import access, R_OK,walk, sep
from glob import glob
from noname import AppConfiguration
from msdapp.msd.filterMSD import FilterMSD
from msdapp.msd.batchCompareMSD import CompareMSD
from msdapp.msd.batchHistogramStats import HistoStats
#from msdapp.msd.histogramLogD import HistogramLogD
#from msdapp.msd.ratioStats import RatioStats
from configobj import ConfigObj
APP_EXIT = 1

############Config dialog
class MSDConfig(AppConfiguration):
    def __init__(self, parent):
        super(MSDConfig, self).__init__(parent)
        if parent.loaded:
            self.__loadValues(parent)


    def __loadValues(self,parent):
        print("Config loaded")
        self.m_textCtrl15.SetValue(parent.datafile)
        self.m_textCtrl16.SetValue(parent.msdfile)
        self.m_textCtrl1.SetValue(parent.histofile)
        self.m_textCtrl2.SetValue(parent.filteredfname)
        self.m_textCtrl3.SetValue(parent.filtered_msd)
        self.m_textCtrl4.SetValue(parent.msdpoints)
        self.m_textCtrl5.SetValue(parent.timeint)
        self.m_textCtrl6.SetValue(parent.encoding)
        self.m_textCtrl8.SetValue(parent.field)
        self.m_textCtrl9.SetValue(parent.diffcolumn)
        self.m_textCtrl10.SetValue(parent.minlimit)
        self.m_textCtrl11.SetValue(parent.maxlimit)
        self.m_textCtrl12.SetValue(parent.binwidth)
        self.m_textCtrl13.SetValue(parent.threshold)


    def OnSaveConfig(self, event):
        print("In config - onsave - saving to cfg file")
        config = ConfigObj()
        config.filename = join(expanduser('~'),'.msdcfg')
        config.encoding = self.m_textCtrl6.GetValue()
        config['DATA_FILENAME'] = self.m_textCtrl15.GetValue()
        config['MSD_FILENAME'] = self.m_textCtrl16.GetValue()
        config['HISTOGRAM_FILENAME'] = self.m_textCtrl1.GetValue()
        config['FILTERED_FILENAME'] = self.m_textCtrl2.GetValue()
        config['FILTERED_MSD'] = self.m_textCtrl3.GetValue()
        config['LOG_COLUMN'] = self.m_textCtrl8.GetValue()
        config['DIFF_COLUMN'] = self.m_textCtrl9.GetValue()
        config['ENCODING'] = self.m_textCtrl6.GetValue()
        config['MSD_POINTS'] = self.m_textCtrl4.GetValue()
        config['MINLIMIT'] = self.m_textCtrl10.GetValue()
        config['MAXLIMIT'] = self.m_textCtrl11.GetValue()
        config['TIME_INTERVAL'] = self.m_textCtrl5.GetValue()
        config['BINWIDTH'] = self.m_textCtrl12.GetValue()
        config['THRESHOLD'] = self.m_textCtrl13.GetValue()
        config.write()
        event.Skip()

####Main GUI
class ScriptController(wx.Frame):
    def __init__(self, parent, title):
        super(ScriptController, self).__init__(parent, title=title, size=(600, 800))
        self.configfile=join(expanduser('~'),'.msdcfg')
        self.loaded = self.__loadConfig()
        self.InitUI()
        self.Centre()
        self.Show()

    def __loadConfig(self):
        if self.configfile is not None:
            try:
                access(self.configfile, R_OK)
                config = ConfigObj(self.configfile, encoding='ISO-8859-1' )
                self.datafile = config['DATA_FILENAME'] #AllROI.txt
                self.msdfile = config['MSD_FILENAME'] #AllROI-MSD.txt
                self.filteredfname = config['FILTERED_FILENAME']
                self.filtered_msd = config['FILTERED_MSD']
                self.histofile = config['HISTOGRAM_FILENAME']
                self.diffcolumn = config['LOG_COLUMN']
                self.field = config['DIFF_COLUMN']
                self.encoding = config['ENCODING']
                self.msdpoints = config['MSD_POINTS']
                self.minlimit = config['MINLIMIT']
                self.maxlimit = config['MAXLIMIT']
                self.timeint = config['TIME_INTERVAL']
                self.binwidth = config['BINWIDTH']
                self.threshold = config['THRESHOLD']

                return True
            except:
                raise IOError
        else:
            return False



    def InitUI(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_NEW, '&New\tCtrl+N')
        fileMenu.Append(wx.ID_OPEN, '&Open\tCtrl+O')
        fileMenu.Append(wx.ID_SAVE, '&Save\tCtrl+S')
        fileMenu.AppendSeparator()
        #menu_quit = wx.MenuItem(fileMenu, APP_EXIT, '&Quit\tCtrl+Q')
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
        grid = wx.FlexGridSizer(5, 2, 10,10)
        self.cb1 = wx.CheckBox(panel, label='Filter log10 D')
        self.cb2 = wx.CheckBox(panel, label='Histogram log10 D')
        self.cb3 = wx.CheckBox(panel, label='Batch Histogram Stats')
        self.cb4 = wx.CheckBox(panel, label='Batch Compare MSD')
        #cb5 = wx.CheckBox(panel, label='Ratio Stats')

        st_cb = wx.StaticText(panel, label='Script')
        st_cb.SetFont(font_header)
        st_opt = wx.StaticText(panel, label='Processing')
        st_opt.SetFont(font_header)


        vbox.Add((-1, 10))
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        self.result_filter = wx.StaticText(panel,label='')
        self.gauge_filter = wx.Gauge(panel)
        self.gauge_histo = wx.Gauge(panel)
        self.gauge_stats = wx.Gauge(panel)
        self.gauge_msd = wx.Gauge(panel)
        flags = wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL
        hbox4.AddMany([self.result_filter,(self.gauge_filter,0,flags,5)])
        hbox5.Add(self.gauge_histo, 0, flags, 5)
        hbox6.Add(self.gauge_stats, 0, flags, 5)
        hbox7.Add(self.gauge_msd, 0, flags, 5)

        grid.AddMany([(st_cb, 0, wx.TOP | wx.LEFT, 12),
                      (st_opt, 0, wx.TOP | wx.RIGHT, 12),
                      (self.cb1, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 9),
                      (hbox4, 0, wx.ALIGN_LEFT, 9),
                      (self.cb2, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 9),
                      (hbox5, 0, wx.ALIGN_LEFT, 9),
                      (self.cb3, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 9),
                      (hbox6, 0, wx.ALIGN_LEFT, 9),
                      (self.cb4, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL,9),
                      (hbox7, 0, wx.ALIGN_LEFT, 9)
                      ])
        grid.AddGrowableCol(1, 1)
        vbox.Add(grid, flag=wx.LEFT, border=10)

        # options for Ratio stats
        # vbox.Add((-1, 25))
        #
        # hbox8a = wx.BoxSizer(wx.HORIZONTAL)
        # hbox8 = wx.BoxSizer(wx.HORIZONTAL)
        # hbox8c = wx.BoxSizer(wx.HORIZONTAL)
        # hbox8d = wx.BoxSizer(wx.HORIZONTAL)
        # st_rs = wx.StaticText(panel, label='Ratio Stats')
        # st_rs.SetFont(font_header)
        # st8a = wx.StaticText(panel, label='Group 1')
        # st8b = wx.StaticText(panel, label='Group 2')
        # in_group1 = wx.TextCtrl(panel, 4)
        # in_group2 = wx.TextCtrl(panel, 4)
        # btnfile1 = wx.Button(panel, label='File 1')
        # btnfile2 = wx.Button(panel, label='File 2')
        # self.in_ratiofile1 = wx.TextCtrl(panel)
        # self.in_ratiofile2 = wx.TextCtrl(panel)
        #
        # hbox8.Add(st_rs)
        # hbox8a.AddMany([st8a, in_group1, st8b, in_group2])
        # hbox8c.AddMany([btnfile1, self.in_ratiofile1])
        # hbox8d.AddMany([btnfile2, self.in_ratiofile2])
        #
        # vbox.AddMany([hbox8,hbox8a, hbox8c, hbox8d])

        ### OUTPUT panel
        vbox.Add((-1, 25))


        hbox9 = wx.BoxSizer(wx.HORIZONTAL)
        self.resultbox = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        hbox9.Add(self.resultbox, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox9, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND,
                 border=10)

        vbox.Add((-1, 25))

        hbox_btns = wx.BoxSizer(wx.HORIZONTAL)
        btnRun = wx.Button(panel, label='Run selected', size=(100, 30))
        hbox_btns.Add(btnRun)
        btn2 = wx.Button(panel, label='Close', size=(70, 30))
        hbox_btns.Add(btn2, flag=wx.LEFT | wx.BOTTOM, border=5)
        vbox.Add(hbox_btns, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)

        panel.SetSizer(vbox)
        #Actions
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_BUTTON, self.OnCloseWindow, btn2)
        self.Bind(wx.EVT_BUTTON, self.OnRunScripts, btnRun)
        self.Bind(wx.EVT_BUTTON, self.OnInputdir, self.btnInputdir)
        self.Bind(wx.EVT_BUTTON, self.OnOutputdir, self.btnOutputdir)
        # self.Bind(wx.EVT_BUTTON, self.OnRatiofile1, btnfile1)
        # self.Bind(wx.EVT_BUTTON, self.OnRatiofile2, btnfile2)

    def Warn(self, message, caption='Warning!'):
        dlg = wx.MessageDialog(self, message, caption, wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

    def ShowFeedBack(self, show):
        self.gauge_filter.Show(show)
        #self.result.Show(not show)
        if show:
            self.timer.Start(250)
        else:
            self.timer.Stop()
        self.Layout()

    def OnRunScripts(self,e):
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

        if self.cb1.GetValue():
            self.StatusBar.SetStatusText("Running Filter script")
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER,
                      lambda e: self.gauge_filter.Pulse(),
                      self.timer)
            self.RunFilter(e)

        if self.cb2.GetValue():
            self.StatusBar.SetStatusText("Running Histogram script")
        if self.cb3.GetValue():
            self.StatusBar.SetStatusText("Running Stats script")
        if self.cb4.GetValue():
            self.StatusBar.SetStatusText("Running MSD compare script")

    def RunFilter(self, event):
        self.ShowFeedBack(True)
        #loop through directory
        if access(self.inputdir, R_OK):
            #find datafile - assume same directory for msd file
            result = [y for x in walk(self.inputdir) for y in glob(join(x[0], self.datafile))]
            if len(result) > 0:
                for datafile in result:
                    self.StatusBar.SetStatusText("Running Filter script: %s" % datafile)
                    datafile_msd = datafile.replace(self.datafile, self.msdfile)
                    outputdir = dirname(datafile)
                    self.resultbox.AppendText("FILTER: Datafile: %s\n" % datafile)
                    self.resultbox.AppendText("FILTER: MSD: %s\n" % datafile_msd)
                    fmsd = FilterMSD(self.configfile, datafile, datafile_msd, outputdir, int(self.minlimit), int(self.maxlimit))
                    try:
                        results = fmsd.runFilter()
                        self.resultbox.AppendText("FILTER: Results:\n\t%d of %d rows filtered\n\t%s\n\t%s" % (results[3], results[2],results[0], results[1]))
                        self.result_filter.SetLabel("Complete")
                    except Exception as e:
                        self.Warn(e)

            else:
                self.Warn("Cannot find datafile: %s" % self.datafile)
        else:
            self.Warn("Cannot access input directory: %s" % self.inputdir)
        self.ShowFeedBack(False)

    def OnInputdir(self, e):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory containing input files")
        if dlg.ShowModal() == wx.ID_OK:
            self.dirname = str(dlg.GetPath())
            self.StatusBar.SetStatusText("Loaded: %s" % self.dirname)
            self.txtInputdir.SetValue(self.dirname)
        dlg.Destroy()

    def OnOutputdir(self, e):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory for output files")
        if dlg.ShowModal() == wx.ID_OK:
            self.dirname = str(dlg.GetPath())
            self.StatusBar.SetStatusText("Loaded: %s\n" % self.dirname)
            self.txtOutputdir.SetValue(self.dirname)
        dlg.Destroy()

    def OnRatiofile1(self, e):
        """ Open a file"""
        self.ratiofile1 = ''
        dlg = wx.FileDialog(self, "Choose a File for Group 1", self.ratiofile1)
        if dlg.ShowModal() == wx.ID_OK:
            self.ratiofile1 = str(dlg.GetPath())
            self.StatusBar.SetStatusText("Loaded: %s\n" % self.ratiofile1)
            self.in_ratiofile1.SetValue(self.ratiofile1)
        dlg.Destroy()

    def OnRatiofile2(self, e):
        """ Open a file"""
        self.ratiofile2 = ''
        dlg = wx.FileDialog(self, "Choose a File for Group 1", self.ratiofile2)
        if dlg.ShowModal() == wx.ID_OK:
            self.ratiofile2 = str(dlg.GetPath())
            self.StatusBar.SetStatusText("Loaded: %s\n" % self.ratiofile2)
            self.in_ratiofile2.SetValue(self.ratiofile2)
        dlg.Destroy()

    def OnQuit(self, e):
        self.Close()

    def OnConfig(self, e):
        configdlg = MSDConfig(self)
        self.Bind(wx.EVT_BUTTON, self.OnSaveConfig, configdlg.btnSave)
        configdlg.Show(True)

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
            self.StatusBar.SetStatusText("Config Loaded: %s\n" % self.configfile)
            self.__loadConfig()
        openFileDialog.Destroy()

    def OnSaveConfig(self, event):
        print("Save From Config dialog")
        self.configfile = join(expanduser('~'),'.msdcfg')
        self.loaded = self.__loadConfig()
        if self.loaded:
            self.StatusBar.SetStatusText("Config saved")
            #event.Veto()
        else:
            self.StatusBar.SetStatusText("ERROR: Save Config failed")


def main():
    app = wx.App()
    ScriptController(None, title='MSD Analysis')
    app.MainLoop()


####################################################################
if __name__ == '__main__':
    main()