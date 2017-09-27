# -*- coding: utf-8 -*-

# center.py

import wx
APP_EXIT = 1

class ScriptController(wx.Frame):
    def __init__(self, parent, title):
        super(ScriptController, self).__init__(parent, title=title, size=(600, 800))
        self.InitUI()
        self.Centre()
        self.Show()

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
        configMenu.Append(wx.ID_NEW, '&New\tCtrl+N')
        configMenu.Append(wx.ID_OPEN, '&Open\tCtrl+O')

        menubar.Append(fileMenu, '&File')
        menubar.Append(configMenu, '&Config')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)

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
        self._inputdir = wx.Button(panel, label='Input directory')
        #st1.SetFont(font)
        hbox1.Add(self._inputdir, flag=wx.RIGHT, border=8)
        self.inputedit = wx.TextCtrl(panel)
        hbox1.Add(self.inputedit, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))
        ####Output directory
        hbox1a = wx.BoxSizer(wx.HORIZONTAL)
        self._outputdir = wx.Button(panel, label='Output directory')
        # st1.SetFont(font)
        hbox1a.Add(self._outputdir, flag=wx.RIGHT, border=8)
        self.outputdir = wx.TextCtrl(panel)
        hbox1a.Add(self.outputdir, proportion=1)
        vbox.Add(hbox1a, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='Processing scripts should run in sequence')
        st2.SetFont(font_description)
        hbox2.Add(st2)

        vbox.Add(hbox2, flag=wx.LEFT | wx.TOP, border=10)

        vbox.Add((-1, 10))
        #### Sequence scripts buttons
        grid = wx.GridSizer(rows=6, cols=2, hgap=5, vgap=5)
        cb1 = wx.CheckBox(panel, label='Filter log10 D')
        cb2 = wx.CheckBox(panel, label='Histogram log10 D')
        cb3 = wx.CheckBox(panel, label='Batch Histogram Stats')
        cb4 = wx.CheckBox(panel, label='Batch Compare MSD')
        cb5 = wx.CheckBox(panel, label='Ratio Stats')

        st_cb = wx.StaticText(panel, label='Script')
        st_cb.SetFont(font_header)
        st_opt = wx.StaticText(panel, label='Options')
        st_opt.SetFont(font_header)


        vbox.Add((-1, 10))
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        st4a = wx.StaticText(panel, label='Min')
        in_min = wx.TextCtrl(panel, 4)
        st4b = wx.StaticText(panel, label='Max')
        in_max = wx.TextCtrl(panel, 4)
        hbox4.AddMany([st4a,in_min, st4b,in_max])


        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        st5 = wx.StaticText(panel, label='Bin width')
        in_bw = wx.TextCtrl(panel, 4)
        hbox5.AddMany([st5, in_bw])

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        st6a = wx.StaticText(panel, label='Prefix')
        in_prefix = wx.TextCtrl(panel, 4)
        st6b = wx.StaticText(panel, label='Threshold')
        in_thresh = wx.TextCtrl(panel, 4)
        hbox6.AddMany([st6a, in_prefix, st6b, in_thresh])
        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        #Options  for Batch compare
        st7 = wx.StaticText(panel, label='')
        hbox7.Add(st7)
        hbox8 = wx.BoxSizer(wx.HORIZONTAL)
        st8a = wx.StaticText(panel, label='Group 1')
        in_group1 = wx.TextCtrl(panel, 4)
        st8b = wx.StaticText(panel, label='Group 2')
        in_group2 = wx.TextCtrl(panel, 4)
        hbox8.AddMany([st8a, in_group1, st8b, in_group2])

        grid.AddMany([(st_cb, 0, wx.TOP | wx.LEFT, 12),
                      (st_opt, 0, wx.TOP | wx.RIGHT, 12),
                      (cb1, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 9),
                      (hbox4, 0, wx.RIGHT, 9),
                      (cb2, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 9),
                      (hbox5, 0, wx.RIGHT, 9),
                      (cb3, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 9),
                      (hbox6, 0, wx.RIGHT, 9),
                      (cb4, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL,9),
                      (hbox7, 0, wx.RIGHT, 9),
                      (cb5, 0, wx.LEFT| wx.ALIGN_CENTER_VERTICAL, 9),
                      (hbox8, 0, wx.RIGHT, 9),])
        vbox.Add(grid, flag=wx.LEFT, border=10)

        vbox.Add((-1, 25))
        ### OUTPUT panel

        hbox9 = wx.BoxSizer(wx.HORIZONTAL)
        tc9 = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        hbox9.Add(tc9, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox9, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND,
                 border=10)

        vbox.Add((-1, 25))

        hbox_btns = wx.BoxSizer(wx.HORIZONTAL)
        btn1 = wx.Button(panel, label='Ok', size=(70, 30))
        hbox_btns.Add(btn1)
        btn2 = wx.Button(panel, label='Close', size=(70, 30))
        hbox_btns.Add(btn2, flag=wx.LEFT | wx.BOTTOM, border=5)
        vbox.Add(hbox_btns, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)

        panel.SetSizer(vbox)
        #Actions
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_BUTTON, self.OnCloseWindow, btn2)
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self._inputdir)
        self.Bind(wx.EVT_BUTTON, self.OnOutput, self._outputdir)

    def OnOpen(self, e):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.DirDialog(self, "Choose a directory containing input files", self.dirname)
        if dlg.ShowModal() == wx.ID_OK:
            self.dirname = str(dlg.GetPath())
            self.StatusBar.SetStatusText("Loaded: %s\n" % self.dirname)
            self.inputedit.SetValue(self.dirname)
        dlg.Destroy()

    def OnOutput(self, e):
        """ Open a file"""
        self.outputdirname = ''
        dlg = wx.DirDialog(self, "Choose a directory for output files", self.outputdirname)
        if dlg.ShowModal() == wx.ID_OK:
            self.outputdirname = str(dlg.GetPath())
            self.StatusBar.SetStatusText("Loaded: %s\n" % self.outputdirname)
            self.outputdir.SetValue(self.outputdirname)
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


def main():
    app = wx.App()
    ScriptController(None, title='MSD Analysis')
    app.MainLoop()

if __name__ == '__main__':
    main()