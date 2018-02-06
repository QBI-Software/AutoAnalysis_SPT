# import images
# import logging
import csv
import re
import time
from glob import iglob
from os import access, R_OK
from os.path import join, expanduser, isdir, sep
#maintain this order of matplotlib
# TkAgg causes Runtime errors in Thread
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('seaborn-paper')
import wx
import wx.html2

from configobj import ConfigObj
from msdapp.guicontrollers import EVT_RESULT, EVT_DATA
from msdapp.guicontrollers import MSDController
from noname import ConfigPanel, FilesPanel, ComparePanel, WelcomePanel, ProcessPanel
__version__='1.2.0'

########################################################################
class HomePanel(WelcomePanel):
    """
    This will be the first notebook tab
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        super(HomePanel, self).__init__(parent)
        img = wx.EmptyBitmap(1, 1)
        img.LoadFile(join('resources', 'MSDPlots.bmp'), wx.BITMAP_TYPE_BMP)

        self.m_richText1.BeginFontSize(14)
        welcome = "Welcome to the MSD Automated Analysis App (v.%s)"% __version__
        self.m_richText1.WriteText(welcome)
        self.m_richText1.EndFontSize()
        self.m_richText1.Newline()
        # self.m_richText1.BeginLeftIndent(20)
        self.m_richText1.BeginItalic()
        self.m_richText1.WriteText("developed by Liz Cooper-Williams, QBI Software, The University of Queensland")
        self.m_richText1.EndItalic()
        # self.m_richText1.EndLeftIndent()
        self.m_richText1.Newline()
        self.m_richText1.WriteImage(img)
        self.m_richText1.Newline()
        self.m_richText1.WriteText(
            r'''This is a multi-threaded application designed to automate analysis of single particle tracking data.''')
        self.m_richText1.Newline()
        # self.m_richText1.BeginNumberedBullet(1, 0.2, 0.2, wx.TEXT_ATTR_BULLET_STYLE)
        self.m_richText1.BeginBold()
        self.m_richText1.WriteText("Configure")
        self.m_richText1.EndBold()
        self.m_richText1.Newline()
        # self.m_richText1.BeginLeftIndent(20)
        self.m_richText1.WriteText(
            'All filenames, column names, groups, threshold and binwidth options can be specifically configured and multiple configurations saved and reloaded.')
        self.m_richText1.Newline()
        self.m_richText1.BeginBold()
        self.m_richText1.WriteText("Select Files")
        self.m_richText1.EndBold()
        # self.m_richText1.BeginLeftIndent(20)
        self.m_richText1.Newline()
        self.m_richText1.WriteText(
            "Select a top level directory containing the required data files and/or use the Drag'n'Drop for individual files. Only files checked in the file list will be included in the analysis. Compiled output will be put in the output directory whereas individually processed files will be put in a subfolder in the input directory structure. It is recommended to provide a prefix (which should be a known search text) to group experiments for later comparison.")
        self.m_richText1.Newline()
        self.m_richText1.BeginBold()
        self.m_richText1.WriteText("Run Processes")
        self.m_richText1.EndBold()
        # self.m_richText1.BeginLeftIndent(20)
        self.m_richText1.Newline()
        self.m_richText1.WriteText(
            r"Each process is described with the required input files (which need to be available in the input directory structure) and the output files which it produces. These are multi-threaded processes which will run in sequence as listed and once running their progress can be monitored. A log file is produced in the user's home directory. Interactive plots can also be produced during processing.")
        # self.m_richText1.EndLeftIndent()
        self.m_richText1.Newline()
        self.m_richText1.BeginBold()
        self.m_richText1.WriteText("Compare Groups")
        self.m_richText1.EndBold()
        # self.m_richText1.BeginLeftIndent(20)
        self.m_richText1.Newline()
        self.m_richText1.WriteText(
            "Once the appropriate files have been generated in the output folder, a statistical comparison of two groups can be run and an interactive plot generated.")
        # self.m_richText1.EndLeftIndent()
        self.m_richText1.Newline()
        self.m_richText1.AddParagraph(
            "The requirements of this application have been provided by Ravi Kasula, Meunier Lab, QBI. The modular design of this application allows for additional processes with minimal effort.  The interactive plots can be saved and shared online via plot.ly if required.  Any issues can be logged via the github repository.")
        self.m_richText1.BeginItalic()
        self.m_richText1.AddParagraph(
            r"Copyright (2017) https://github.com/QBI-Software/MSDAnalysis")
        self.m_richText1.EndItalic()

    def loadController(self):
        pass


########################################################################
class MSDConfig(ConfigPanel):
    def __init__(self, parent):
        super(MSDConfig, self).__init__(parent)
        self.encoding = 'ISO-8859-1'
        self.currentconfig= join(expanduser('~'), '.msdcfg')
        if parent.controller.loaded:
            self.__loadValues(parent.controller)

    def loadController(self):
        pass

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
        self.m_tcCellid.SetValue(parent.cellid)
        self.m_txtAlllogdfilename.SetValue(parent.batchd)
        msg = "Config file: %s" % parent.configfile
        print(msg)
        self.m_status.SetLabel(msg)

    def OnSaveConfig(self, event, configfile=None):
        config = ConfigObj()
        if configfile is not None:
            config.filename = configfile
        else:
            config.filename = self.currentconfig
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
        config['CELLID'] = self.m_tcCellid.GetValue()
        config['BATCHD_FILENAME'] = self.m_txtAlllogdfilename.GetValue()
        config.write()
        # Reload to parent
        try:
            self.Parent.controller = MSDController(config.filename)
            if self.Parent.controller.loaded:
                self.prefixes = [self.Parent.controller.group1, self.Parent.controller.group2]
                self.Parent.prefixes = self.prefixes
                for fp in self.Parent.Children:
                    if isinstance(fp, wx.Panel):
                        fp.loadController()
            msg = "Config file: %s" % config.filename
            print(msg)
            self.m_status.SetLabel(msg)
        except IOError as e:
            self.Parent.Warn("Config error:" + e.args[0])

    def OnSaveNew(self, event):
        openFileDialog = wx.FileDialog(self, "Save config file", "", "", "Config files (*.cfg)|*",
                                       wx.FD_SAVE | wx.FD_CHANGE_DIR)
        openFileDialog.SetDirectory(expanduser('~'))
        if openFileDialog.ShowModal() == wx.ID_OK:
            configfile = str(openFileDialog.GetPath())
            self.currentconfig = configfile
            self.OnSaveConfig(event, configfile)

    def OnLoadConfig(self, event):
        print("Load From Config dialog")
        openFileDialog = wx.FileDialog(self, "Open config file", "", "", "Config files (*.cfg)|*",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR)
        openFileDialog.SetDirectory(expanduser('~'))
        if openFileDialog.ShowModal() == wx.ID_OK:
            configfile = str(openFileDialog.GetPath())
            try:
                config = ConfigObj(configfile, encoding='ISO-8859-1')
                self.Parent.controller.loadConfig(config)
                self.currentconfig=configfile
                #self.Parent.controller.config.filename = join(expanduser('~'), '.msdcfg')  # save over existing?
                #self.Parent.controller.config.write()
                self.__loadValues(self.Parent.controller)
                self.m_status.SetLabel("Config file: %s" % configfile)
            except IOError as e:
                self.Parent.Warn("Config error:" + e.args[0])
        openFileDialog.Destroy()


########################################################################
class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, target):
        super(MyFileDropTarget, self).__init__()
        self.target = target

    def OnDropFiles(self, x, y, filenames):
        group = ''
        for fname in filenames:
            self.target.AppendItem([True, group, fname])
        # Update status bar
        status = 'Total files loaded: %s' % self.target.Parent.m_dataViewListCtrl1.GetItemCount()
        self.target.Parent.m_status.SetLabelText(status)
        return len(filenames)


########################################################################
class FileSelectPanel(FilesPanel):
    def __init__(self, parent):
        super(FileSelectPanel, self).__init__(parent)
        self.col_file.SetMinWidth(200)
        self.loadController()
        self.filedrop = MyFileDropTarget(self.m_dataViewListCtrl1)
        self.m_tcDragdrop.SetDropTarget(self.filedrop)
        #self.col_file.SetSortable(True)
        #self.col_group.SetSortable(True)


    def OnColClick(self, event):
        print("header clicked: ", event.GetColumn())
        # colidx = event.GetColumn()
        # self.m_dataViewListCtrl1.GetModel().Resort()


    def loadController(self):
        self.controller = self.Parent.controller
        self.m_cbGroups.SetItems([self.Parent.prefixes[0], self.Parent.prefixes[1]])
        self.datafile = self.controller.datafile

    def OnInputdir(self, e):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory containing input files")
        if dlg.ShowModal() == wx.ID_OK:
            self.inputdir = str(dlg.GetPath())
            self.txtInputdir.SetValue(self.inputdir)
        dlg.Destroy()

    def OnOutputdir(self, e):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory for output files")
        if dlg.ShowModal() == wx.ID_OK:
            self.outputdir = str(dlg.GetPath())
            self.txtOutputdir.SetValue(self.outputdir)
            # initialize Compare Panel with outputdir
            cpanel = self.getComparePanel()
            if cpanel is not None:
                cpanel.m_tcGp1Files.SetValue(self.outputdir)
                cpanel.m_tcGp2Files.SetValue(self.outputdir)
        dlg.Destroy()

    def OnAssignGroup(self, event):
        """
        Allow user to assign groups to selected files
        :param event:
        :return:
        """
        num_files = self.m_dataViewListCtrl1.GetItemCount()
        group = self.m_cbGroups.GetStringSelection()
        for i in range(0, num_files):
            if self.m_dataViewListCtrl1.GetToggleValue(i, 0):
                self.m_dataViewListCtrl1.SetValue(group, i, 1)
                print('Setting %s with group %s', self.m_dataViewListCtrl1.GetValue(i, 2), group)

    def OnSaveList(self, event):
        """
        Save selected files to csv
        :param event:
        :return:
        """
        num_files = self.m_dataViewListCtrl1.GetItemCount()
        try:
            openFileDialog = wx.FileDialog(self, "Save file list", "", "", "CSV files (*.csv)|*",
                                           wx.FD_SAVE | wx.FD_CHANGE_DIR)
            if openFileDialog.ShowModal() == wx.ID_OK:
                savefile = str(openFileDialog.GetPath())
                with open(savefile, 'w') as csvfile:
                    swriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                    for i in range(0, num_files):
                        if self.m_dataViewListCtrl1.GetToggleValue(i, 0):
                            swriter.writerow(
                                [self.m_dataViewListCtrl1.GetValue(i, 1), self.m_dataViewListCtrl1.GetValue(i, 2)])
        except Exception as e:
            self.Parent.Warn("Save list error:" + e.args[0])
        finally:
            print('Save list complete')

    def OnLoadList(self, event):
        """
        Load saved list
        :param event:
        :return:
        """
        try:
            openFileDialog = wx.FileDialog(self, "Open file list", "", "", "CSV files (*.csv)|*",
                                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR)

            if openFileDialog.ShowModal() == wx.ID_OK:
                savefile = str(openFileDialog.GetPath())
                with open(savefile, 'r') as csvfile:
                    sreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                    self.m_dataViewListCtrl1.DeleteAllItems()
                    for row in sreader:
                        if len(row) > 0:
                            self.m_dataViewListCtrl1.AppendItem([True, row[0], row[1]])
                msg = "Total Files loaded: %d" % self.m_dataViewListCtrl1.GetItemCount()
                self.m_status.SetLabelText(msg)
        except Exception as e:
            print(e.args[0])
            self.Parent.Warn("Load list error:" + e.args[0])
        finally:
            print("Load list complete")

    def OnAutofind(self, event):
        """
        Find all matching files in top level directory
        :param event:
        :return:
        """
        self.btnAutoFind.Disable()
        fullsearch = self.m_cbMatchAny.GetValue()
        self.m_status.SetLabelText("Finding files ... please wait")
        if fullsearch:
            allfiles = [y for y in iglob(join(self.inputdir, '**', '*'+self.datafile), recursive=True)]
        else:
            allfiles = [y for y in iglob(join(self.inputdir, '**', self.datafile), recursive=True)]
        searchtext = self.m_tcSearch.GetValue()
        if (len(searchtext) > 0):
            filenames = [f for f in allfiles if re.search(searchtext, f, flags=re.IGNORECASE)]
        else:
            filenames = allfiles

        for fname in filenames:
            group = ''
            # group as directory name ONLY
            for pfix in self.Parent.prefixes:
                group = ''
                if pfix.upper() in fname.upper().split(sep):
                    group = pfix
                    break
                elif len(searchtext) > 0 and re.search(searchtext + pfix, fname, flags=re.IGNORECASE):
                    group = pfix
                    break

            self.m_dataViewListCtrl1.AppendItem([True, group, fname])

        self.col_file.SetMinWidth(wx.LIST_AUTOSIZE)
        msg = "Total Files loaded: %d" % self.m_dataViewListCtrl1.GetItemCount()
        self.m_status.SetLabelText(msg)
        self.btnAutoFind.Enable(True)

    def OnSelectall(self, event):
        for i in range(0, self.m_dataViewListCtrl1.GetItemCount()):
            self.m_dataViewListCtrl1.SetToggleValue(event.GetSelection(), i, 0)
        print("Toggled selections to: ", event.GetSelection())

    def OnClearlist(self, event):
        print("Clear items in list")
        self.m_dataViewListCtrl1.DeleteAllItems()

    def getComparePanel(self):
        """
        Get access to panel
        :return:
        """
        panel = None
        for fp in self.Parent.Children:
            if isinstance(fp, CompareRunPanel):
                panel = fp
                break
        return panel


########################################################################
class ProcessRunPanel(ProcessPanel):
    def __init__(self, parent):
        super(ProcessRunPanel, self).__init__(parent)
        self.loadController()
        # self.controller = parent.controller
        # Bind timer event
        # self.Bind(wx.EVT_TIMER, self.progressfunc, self.controller.timer)
        # processes = [p['caption'] for p in self.controller.processes]
        # self.m_checkListProcess.AppendItems(processes)
        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.progressfunc)
        # EVT_CANCEL(self, self.stopfunc)
        # Set timer handler
        self.start = {}

    def loadController(self):
        self.controller = self.Parent.controller
        processes = [p['caption'] for p in self.controller.processes]
        self.m_checkListProcess.Clear()
        self.m_checkListProcess.AppendItems(processes)

    def OnShowDescription(self, event):
        print(event.String)
        desc = [p['description'] for p in self.controller.processes if p['caption'] == event.String]
        filesIn = [p['files'] for p in self.controller.processes if p['caption'] == event.String]
        filesOut = [p['filesout'] for p in self.controller.processes if p['caption'] == event.String]
        # Load from Config
        filesIn = [self.controller.config[f] for f in filesIn[0].split(", ")]
        filesOut = [self.controller.config[f] for f in filesOut[0].split(", ")]
        # Load to GUI
        self.m_stTitle.SetLabelText(event.String)
        self.m_stDescription.SetLabelText(desc[0])
        self.m_stFilesin.SetLabelText(", ".join(filesIn))
        self.m_stFilesout.SetLabelText(", ".join(filesOut))
        self.Layout()

    def progressfunc(self, msg):
        """
        Update progress bars in table - multithreaded
        :param count:
        :param row:
        :param col:
        :return:
        """
        (count, row, i, total, process) = msg.data
        print("\nProgress updated: ", time.ctime())
        print('count = ', count)
        status = "%d of %d files " % (i, total)
        if count == 0:
            self.m_dataViewListCtrlRunning.AppendItem([process, count, "Pending"])
            self.start[process] = time.time()
        elif count < 0:
            self.m_dataViewListCtrlRunning.SetValue("ERROR in process - see log file", row=row, col=2)
            self.m_btnRunProcess.Enable()
        elif count < 100:
            self.m_dataViewListCtrlRunning.SetValue(count, row=row, col=1)
            self.m_dataViewListCtrlRunning.SetValue("Running " + status, row=row, col=2)
            self.m_stOutputlog.SetLabelText("Running: %s ...please wait" % process)
        else:
            if process in self.start:
                endtime = time.time() - self.start[process]
                status = "%s (%d secs)" % (status, endtime)
            print(status)
            self.m_dataViewListCtrlRunning.SetValue(count, row=row, col=1)
            self.m_dataViewListCtrlRunning.SetValue("Done " + status, row=row, col=2)
            self.m_btnRunProcess.Enable()
            self.m_stOutputlog.SetLabelText("Completed process %s" % process)

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

    def OnCancelScripts(self, event):
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
        # Clear processing window
        self.m_dataViewListCtrlRunning.DeleteAllItems()
        # Disable Run button
        # self.m_btnRunProcess.Disable()
        btn = event.GetEventObject()
        btn.Disable()
        # Get selected processes
        selections = self.m_checkListProcess.GetCheckedStrings()
        print("Processes selected: ", len(selections))
        showplots = self.m_cbShowplots.GetValue()
        indivplots = self.m_cbIndivplots.GetValue()
        # Get data from other panels
        filepanel = self.getFilePanel()
        filenames = {'all': [], self.Parent.prefixes[0]: [], self.Parent.prefixes[1]: []}
        num_files = filepanel.m_dataViewListCtrl1.GetItemCount()
        outputdir = filepanel.txtOutputdir.GetValue()  # for batch processes

        expt = filepanel.m_tcSearch.GetValue()
        # reload logging to output to outputdir
        if len(outputdir) > 0:
            self.controller.loadLogger(outputdir, expt)
        if len(expt) <= 0:
            msg = 'No prefix for batch files. If required, enter in Files panel - prefix and re-run.'
            self.Parent.Warn(msg)

        print('All Files:', num_files)
        try:
            if len(selections) > 0 and num_files > 0:
                for i in range(0, num_files):
                    if filepanel.m_dataViewListCtrl1.GetToggleValue(i, 0):
                        fname = filepanel.m_dataViewListCtrl1.GetValue(i, 2)
                        group = filepanel.m_dataViewListCtrl1.GetValue(i, 1)
                        if not isdir(fname):
                            filenames['all'].append(fname)
                            if len(group) > 0:
                                filenames[group].append(fname)

                print('Selected Files:', len(filenames))
                if len(filenames) <= 0:
                    raise ValueError(
                        "No files selected - please go to Files Panel and add files (not directories) to list")

                row = 0
                # For each process
                for p in selections:
                    i = [i for i in range(len(self.controller.processes)) if p == self.controller.processes[i]['caption']][0]
                    if self.controller.processes[i]['ptype'] == 'indiv':
                        self.controller.RunProcess(self, filenames['all'], i, outputdir, expt, row, indivplots)
                    else:
                        self.controller.RunProcess(self, filenames, i, outputdir, expt, row, showplots)
                    row = row + 1
                    print('Next process: row=', row)

            else:
                if len(selections) <= 0:
                    raise ValueError("No processes selected")
                else:
                    raise ValueError("No files selected - please go to Files Panel and add to list")
        except ValueError as e:
            self.Parent.Warn(e.args[0])
            # Enable Run button
            self.m_btnRunProcess.Enable()


########################################################################
class CompareRunPanel(ComparePanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.loadDefaults()
        self.loadController()
        self.controller = parent.controller
        EVT_DATA(self, self.updateResults)

    def loadController(self):
        self.controller = self.Parent.controller

    def OnLoadDefaults(self, event):
        """
        callback
        :param event:
        :return:
        """
        self.loadDefaults()

    def loadDefaults(self):
        """
        Initialise group fields from config and file panels
        :return:
        """
        fpanel = self.getFilePanel()
        if fpanel is not None:
            prefix = fpanel.m_tcSearch.GetValue()
            self.m_tcGp1Files.SetValue(fpanel.txtOutputdir.GetValue())
            self.m_tcGp2Files.SetValue(fpanel.txtOutputdir.GetValue())
        else:
            prefix = ''
        cpanel = self.getConfigPanel()
        if cpanel is not None:
            self.m_tcGp1.SetValue(prefix + cpanel.m_tcGroup1.GetValue())
            self.m_tcGp2.SetValue(prefix + cpanel.m_tcGroup2.GetValue())

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

    def OnBrowseGp1(self, event):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory containing data files")
        if dlg.ShowModal() == wx.ID_OK:
            # self.inputdir1 = str(dlg.GetPath())
            self.m_tcGp1Files.SetValue(str(dlg.GetPath()))
        dlg.Destroy()

    def OnBrowseGp2(self, event):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory containing data files")
        if dlg.ShowModal() == wx.ID_OK:
            # self.inputdir2 = str(dlg.GetPath())
            self.m_tcGp2Files.SetValue(str(dlg.GetPath()))
        dlg.Destroy()

    def OnCompareRun(self, event):
        inputdirs = [self.m_tcGp1Files.GetValue(), self.m_tcGp2Files.GetValue()]
        prefixes = [self.m_tcGp1.GetValue(), self.m_tcGp2.GetValue()]
        try:
            for d in inputdirs:
                if not isdir(d) or not access(d, R_OK):
                    raise ValueError("Please select directories containing files for comparison")
            if prefixes[0] == prefixes[1]:
                raise ValueError("Groups are the same")
            if len(prefixes[0]) <= 0 or len(prefixes[1]) <= 0:
                raise ValueError("Two groups are required - matching the prefixes of compiled files")
            outputdir = self.getFilePanel().txtOutputdir.GetValue()
            searchtext = self.getFilePanel().m_tcSearch.GetValue()

            self.controller.RunCompare(self, inputdirs, outputdir, prefixes, searchtext)
        except ValueError as e:
            self.Parent.Warn(e.args[0])

    def OnCompareStop(self, event):
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

    def getConfigPanel(self):
        """
        Get access to filepanel
        :return:
        """
        filepanel = None

        for fp in self.Parent.Children:
            if isinstance(fp, MSDConfig):
                filepanel = fp
                break
        return filepanel


########################################################################
class AppMain(wx.Listbook):
    def __init__(self, parent):
        """Constructor"""
        wx.Listbook.__init__(self, parent, wx.ID_ANY, style=wx.BK_DEFAULT)

        # logging.basicConfig(filename='msdanalysis.log', level=logging.INFO, format='%(asctime)s %(message)s',
        #                     datefmt='%d-%m-%Y %I:%M:%S %p')
        self.encoding = 'ISO-8859-1'
        self.configfile = join(expanduser('~'), '.msdcfg')
        if not access(self.configfile, R_OK):
            # use local file in resources
            self.configfile = join('resources', 'msd.cfg')
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

        pages = [(HomePanel(self), "Welcome"),
                 (MSDConfig(self), "Configure"),
                 (FileSelectPanel(self), "Select Files"),
                 (ProcessRunPanel(self), "Run Processes"),
                 (CompareRunPanel(self), "Compare Groups")]
        imID = 0
        for page, label in pages:
            # self.AddPage(page, label, imageId=imID)
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
                          size=(900, 700)
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
