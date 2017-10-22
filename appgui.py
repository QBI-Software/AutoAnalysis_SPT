#import images
import logging
import time
from glob import glob, iglob
from multiprocessing import Manager, Process
import threading
from os import access, R_OK, walk, mkdir
from os.path import join, expanduser, dirname, exists, split, isdir
import re
from queue import Queue
import matplotlib.pyplot as plt
import pandas as pd
import wx
import wx.html2
from configobj import ConfigObj
from collections import OrderedDict
from msdapp.guicontrollers import MSDController
from msdapp.msd.batchCompareMSD import CompareMSD
from msdapp.msd.batchHistogramStats import HistoStats
from msdapp.msd.filterMSD import FilterMSD
from msdapp.msd.histogramLogD import HistogramLogD
from noname import ConfigPanel, FilesPanel, ComparePanel, WelcomePanel, ProcessPanel
from msdapp.guicontrollers import EVT_RESULT,EVT_DATA, EVT_RESULT_ID,ResultEvent


########################################################################
class HomePanel(WelcomePanel):
    """
    This will be the first notebook tab
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        super(HomePanel, self).__init__(parent)
        # hbox = wx.BoxSizer(wx.HORIZONTAL)
        # text = wx.TextCtrl(self, style=wx.TE_MULTILINE,value=self.__loadContent())
        # hbox.Add(text, proportion=1, flag=wx.EXPAND)
        # self.SetSizer(hbox)
        self.m_richText1.AddParagraph(r'''***Welcome to the MSD Automated Analysis App***''')
        self.m_richText1.AddParagraph(r''' To process your files: ''')
        #self.m_richText1.BeginNumberedBullet(1, 0.2, 0.2, wx.TEXT_ATTR_BULLET_STYLE)
        self.m_richText1.AddParagraph(r'1. Check the Configuration options, particularly the column names and filenames used for matching')
        self.m_richText1.AddParagraph(r"2. Select Files to process either with AutoFind from a top level directory and/or Drag and Drop")
        self.m_richText1.AddParagraph(r"3. Select which processes to run and monitor their progress")
        self.m_richText1.AddParagraph(r"4. Choose Compare Groups to run a statistical comparison of two groups after processing files have been generated")
        self.m_richText1.AddParagraph(r"Any queries, contact Liz Cooper-Williams e.cooperwilliams@uq.edu.au")
        self.m_richText1.AddParagraph(r"Copyright (2017) Apache license v2 (https://github.com/QBI-Software/MSDAnalysis)")

    def __loadContent(self):
        """
        Welcome text
        :return:
        """
        content = '''***Welcome to the MSD Automated Analysis App***
        To process your files: 
            1. Check the Configuration options, particularly the column names and filenames used for matching
            2. Select Files to process either with AutoFind from a top level directory and/or Drag and Drop
            3. Select which processes to run and monitor their progress
            4. Choose Compare Groups to run a statistical comparison of two groups after processing files have been generated
       
        '''
        return content

########################################################################
class MSDConfig(ConfigPanel):
    def __init__(self, parent):
        super(MSDConfig, self).__init__(parent)
        self.encoding = 'ISO-8859-1'
        if parent.controller.loaded:
            self.__loadValues(parent.controller)

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
        #Reload to parent
        try:
            self.Parent.controller.loadConfig(config)
            self.m_status.SetLabel("Config updated")
        except IOError as e:
            self.Parent.Warn("Config error:", e.message)

    def OnLoadConfig(self,event):
        print("Load From Config dialog")
        openFileDialog = wx.FileDialog(self, "Open config file", "", "", "Config files (*.cfg)|*",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR)
        openFileDialog.SetDirectory(expanduser('~'))
        if openFileDialog.ShowModal() == wx.ID_OK:
            configfile = str(openFileDialog.GetPath())
            try:
                config = ConfigObj(configfile, encoding='ISO-8859-1')
                self.Parent.controller.loadConfig(config)
                self.Parent.controller.config.filename = join(expanduser('~'), '.msdcfg') #save over existing?
                self.Parent.controller.config.write()
                self.__loadValues(self.Parent.controller)
                self.m_status.SetLabel("Config Loaded: %s" % configfile)
            except IOError as e:
                self.Parent.Warn("Config error:", e.message)
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
        self.col_file.SetMinWidth(200)

        self.filedrop = MyFileDropTarget(self.m_dataViewListCtrl1)
        self.m_tcDragdrop.SetDropTarget(self.filedrop)
        self.datafile = parent.controller.datafile

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
        """
        Find all matching files in top level directory
        :param event:
        :return:
        """

        allfiles = [y for y in iglob(join(self.inputdir, '**', self.datafile), recursive=True)]
        searchtext = self.m_tcSearch.GetValue()
        if (len(searchtext) > 0):
            filenames = [f for f in allfiles if re.search(searchtext,f, flags=re.IGNORECASE)]
        else:
            filenames = allfiles

        for fname in filenames:
            self.m_dataViewListCtrl1.AppendItem([True,fname])

        self.col_file.SetMinWidth(wx.LIST_AUTOSIZE)
        print("Total Files loaded: ", self.m_dataViewListCtrl1.GetItemCount())

    def OnSelectall(self, event):
        for i in range(0, self.m_dataViewListCtrl1.GetItemCount()):
            self.m_dataViewListCtrl1.SetToggleValue(event.GetSelection(),i,0)
        print("Toggled selections to: ", event.GetSelection())

    def OnClearlist(self, event):
        print("Clear items in list")
        self.m_dataViewListCtrl1.DeleteAllItems()

########################################################################
class ProcessRunPanel(ProcessPanel):
    def __init__(self, parent):
        super(ProcessRunPanel, self).__init__(parent)
        self.controller = parent.controller
        # Bind timer event
        #self.Bind(wx.EVT_TIMER, self.progressfunc, self.controller.timer)
        processes = [p['caption'] for p in self.controller.processes]
        self.m_checkListProcess.AppendItems(processes)
        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.progressfunc)
        #EVT_CANCEL(self, self.stopfunc)

    def OnShowDescription( self, event ):
        print(event.String)
        desc = [p['description'] for p in self.controller.processes if p['caption']==event.String]
        filesIn = [p['files'] for p in self.controller.processes if p['caption']==event.String]
        filesOut = [p['filesout'] for p in self.controller.processes if p['caption']==event.String]
        #Load from Config
        filesIn = [self.controller.config[f] for f in filesIn[0].split(", ")]
        filesOut = [self.controller.config[f] for f in filesOut[0].split(", ")]
        #Load to GUI
        self.m_stTitle.SetLabelText(event.String)
        self.m_stDescription.SetLabelText(desc[0])
        self.m_stFilesin.SetLabelText(", ".join(filesIn))
        self.m_stFilesout.SetLabelText(", ".join(filesOut))



    def progressfunc(self, msg):
        """
        Update progress bars in table - multithreaded
        :param count:
        :param row:
        :param col:
        :return:
        """
        (count, row,i,total, process) = msg.data
        print("\nProgress updated: ", time.ctime())
        print('count = ', count)
        status = "%d of %d files " % (i, total)
        if count ==0:
            self.m_dataViewListCtrlRunning.AppendItem([process, count, "Pending"])
            self.start[process] = time.time()
        elif count < 100:
            self.m_dataViewListCtrlRunning.SetValue(count, row=row, col=1)
            self.m_dataViewListCtrlRunning.SetValue("Running " + status, row=row, col=2)
        else:
            endtime = time.time() - self.start[process]
            status = "%s (%d secs)" % (status, round(endtime,4))
            print(status)
            self.m_dataViewListCtrlRunning.SetValue(count, row=row, col=1)
            self.m_dataViewListCtrlRunning.SetValue("Done "+ status, row=row, col=2)


    def getFilePanel(self):
        """
        Get access to filepanel
        :return:
        """
        filepanel = None

        for fp in self.Parent.Children:
            if isinstance(fp, FileSelectPanel):
                filepanel = fp
                break
        return filepanel

    def OnCancelScripts( self, event ):
        """
        Find a way to stop processes
        :param event:
        :return:
        """
        self.controller.shutdown()
        print("Cancel multiprocessor")
        event.Skip()

    def OnRunScripts(self, event):
        """
        Run selected scripts sequentially - updating progress bars
        :param e:
        :return:
        """
        #Clear processing window
        self.m_dataViewListCtrlRunning.DeleteAllItems()
        #Disable Run button
        #self.m_btnRunProcess.Disable()
        btn = event.GetEventObject()
        btn.Disable()
        #Get selected processes
        selections = self.m_checkListProcess.GetCheckedStrings()
        print("Processes selected: ", len(selections))
        #Get data from other panels
        filepanel = self.getFilePanel()
        if filepanel is None:
            self.Parent.Warn("Cannot locate other panels - exiting")
        filenames = []
        num_files = filepanel.m_dataViewListCtrl1.GetItemCount()
        print('All Files:', num_files)
        for i in range(0, num_files):
            if filepanel.m_dataViewListCtrl1.GetToggleValue(i,0):
                filenames.append(filepanel.m_dataViewListCtrl1.GetValue(i,1))
        print('Selected Files:', len(filenames))
        outputdir = filepanel.txtOutputdir.GetValue() #for batch processes
        expt = filepanel.m_tcSearch.GetValue()
        print("Expt:", expt)
        row = 0
        #For each process
        for p in selections:
            print("Running:", p)
            i = [i for i in range(len(self.controller.processes)) if p == self.controller.processes[i]['caption']][0]
            self.controller.RunProcess(self, filenames, i, outputdir, expt, row)
            row = row+1
            print('Next process: row=', row)

        print("Completed processes")
        # Enable Run button
        self.m_btnRunProcess.Enable()

########################################################################
class CompareRunPanel(ComparePanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.controller = parent.controller
        EVT_DATA(self, self.updateResults)

    def updateResults(self, msg):
        (df) = msg.data
        print("\nProgress updated: ", time.ctime())
        print('data = ', df)
        cols = df.columns.tolist()
        self.m_tcResults.AppendText("Independent paired T-Test results\n***********\n")
        for i, row in df.iterrows():
            for col in cols:
                msg = "%s: %s\n" % (col, str(row[col]))
                print(msg)
                self.m_tcResults.AppendText(msg)
            self.m_tcResults.AppendText("\n***********\n")


    def OnBrowseGp1( self, event ):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory containing data files")
        if dlg.ShowModal() == wx.ID_OK:
            self.inputdir1 = str(dlg.GetPath())
            self.m_tcGp1Files.SetValue(self.inputdir1)
        dlg.Destroy()

    def OnBrowseGp2( self, event ):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory containing data files")
        if dlg.ShowModal() == wx.ID_OK:
            self.inputdir2 = str(dlg.GetPath())
            self.m_tcGp2Files.SetValue(self.inputdir2)
        dlg.Destroy()

    def OnCompareRun( self, event ):
        inputdirs = [self.inputdir1, self.inputdir2]
        for d in inputdirs:
            if not isdir(d) or not access(d, R_OK):
                self.Parent.Warn("Please check input directories are entered")
        outputdir = self.getFilePanel().txtOutputdir.GetValue()
        searchtext = self.getFilePanel().m_tcSearch.GetValue()
        prefixes = [self.m_tcGp1.GetValue(),self.m_tcGp2.GetValue()]
        self.controller.RunCompare(self, inputdirs, outputdir, prefixes,searchtext)

    def OnCompareStop( self, event ):
            print('Stopping process')

    def getFilePanel(self):
        """
        Get access to filepanel
        :return:
        """
        filepanel = None

        for fp in self.Parent.Children:
            if isinstance(fp, FileSelectPanel):
                filepanel = fp
                break
        return filepanel

########################################################################
class AppMain(wx.Listbook):

    def __init__(self, parent):
        """Constructor"""
        wx.Listbook.__init__(self, parent, wx.ID_ANY, style=wx.BK_DEFAULT)

        logging.basicConfig(filename='msdanalysis.log', level=logging.INFO, format='%(asctime)s %(message)s',
                            datefmt='%d-%m-%Y %I:%M:%S %p')
        self.encoding = 'ISO-8859-1'
        self.configfile = join(expanduser('~'), '.msdcfg')
        self.controller = MSDController(self.configfile)
        if self.controller.loaded:
            self.prefixes = [self.controller.group1, self.controller.group2]
        else:
            self.prefixes = ['stim', 'nostim']  # default

        self.InitUI()
        self.Centre(wx.BOTH)
        self.Show()



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
                 (ProcessRunPanel(self), "Run Processes"),
                 (CompareRunPanel(self),"Compare Groups")]
        imID = 0
        for page, label in pages:
            #self.AddPage(page, label, imageId=imID)
            self.AddPage(page, label)
            imID += 1

        self.GetListView().SetColumnWidth(0, wx.LIST_AUTOSIZE)

        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGING, self.OnPageChanging)

    # ----------------------------------------------------------------------
    def OnPageChanged(self, event):
        # old = event.GetOldSelection()
        # new = event.GetSelection()
        # sel = self.GetSelection()
        # msg = 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        # print(msg)
        event.Skip()

    # ----------------------------------------------------------------------
    def OnPageChanging(self, event):
        # old = event.GetOldSelection()
        # new = event.GetSelection()
        # sel = self.GetSelection()
        # msg = 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        # print(msg)
        event.Skip()

    def Warn(self, message, caption='Warning!'):
        dlg = wx.MessageDialog(self, message, caption, wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

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
                          size=(800, 700)
                          )

        # self.timer = wx.Timer(self)
        # self.Bind(wx.EVT_TIMER, self.update, self.timer)
        panel = wx.Panel(self)

        notebook = AppMain(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()
        self.Center(wx.BOTH)
        self.Show()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = MSDFrame()
    app.MainLoop()