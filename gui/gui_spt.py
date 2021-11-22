# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Dec 21 2016)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.dataview
import wx.richtext

###########################################################################
## Class ConfigPanel
###########################################################################

class ConfigPanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer1 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer1.SetFlexibleDirection( wx.VERTICAL )
		fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_scrolledWindow1 = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.m_scrolledWindow1.SetScrollRate( 5, 5 )
		self.m_scrolledWindow1.SetMinSize( wx.Size( 600,500 ) )
		
		fgSizer6 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer6.SetFlexibleDirection( wx.BOTH )
		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_Title = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Configuration", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.m_Title.Wrap( -1 )
		self.m_Title.SetFont( wx.Font( 14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		
		fgSizer6.Add( self.m_Title, 0, wx.ALIGN_LEFT|wx.ALL, 5 )
		
		self.m_status = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Settings for processing scripts", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_status.Wrap( -1 )
		self.m_status.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		
		fgSizer6.Add( self.m_status, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.m_staticline8 = wx.StaticLine( self.m_scrolledWindow1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		fgSizer6.Add( self.m_staticline8, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_staticline9 = wx.StaticLine( self.m_scrolledWindow1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		fgSizer6.Add( self.m_staticline9, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_staticText18 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Data Filename (eg AllROI-D.txt)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText18.Wrap( -1 )
		fgSizer6.Add( self.m_staticText18, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl15 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer6.Add( self.m_textCtrl15, 0, wx.ALL, 5 )
		
		self.m_staticText19 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"MSD Filename (eg AllROI-MSD.txt)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText19.Wrap( -1 )
		fgSizer6.Add( self.m_staticText19, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl16 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer6.Add( self.m_textCtrl16, 0, wx.ALL, 5 )
		
		self.m_staticText191 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Encoding (default ISO-8859-1)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText191.Wrap( -1 )
		fgSizer6.Add( self.m_staticText191, 0, wx.ALL, 5 )
		
		self.m_textCtrl162 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer6.Add( self.m_textCtrl162, 0, wx.ALL, 5 )
		
		self.m_staticline81 = wx.StaticLine( self.m_scrolledWindow1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		fgSizer6.Add( self.m_staticline81, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_staticline91 = wx.StaticLine( self.m_scrolledWindow1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		fgSizer6.Add( self.m_staticline91, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_staticText4 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Filtered Filename (generated)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		fgSizer6.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl2 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer6.Add( self.m_textCtrl2, 0, wx.ALL, 5 )
		
		self.m_staticText5 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Filtered MSD (generated)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )
		fgSizer6.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl3 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer6.Add( self.m_textCtrl3, 0, wx.ALL, 5 )
		
		self.m_staticText65 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"All Log10D Filename (generated)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText65.Wrap( -1 )
		fgSizer6.Add( self.m_staticText65, 0, wx.ALL, 5 )
		
		self.m_txtAlllogdfilename = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer6.Add( self.m_txtAlllogdfilename, 0, wx.ALL, 5 )
		
		self.m_staticText3 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Histogram Filename (generated)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		fgSizer6.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl1 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer6.Add( self.m_textCtrl1, 0, wx.ALL, 5 )
		
		self.m_staticText181 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"All Histogram Statistics Filename (generated)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText181.Wrap( -1 )
		fgSizer6.Add( self.m_staticText181, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl161 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer6.Add( self.m_textCtrl161, 0, wx.ALL, 5 )
		
		self.m_staticText20 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"All Avg MSD Filename (generated)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText20.Wrap( -1 )
		fgSizer6.Add( self.m_staticText20, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl18 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer6.Add( self.m_textCtrl18, 0, wx.ALL, 5 )
		
		self.m_staticline10 = wx.StaticLine( self.m_scrolledWindow1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		fgSizer6.Add( self.m_staticline10, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_staticline11 = wx.StaticLine( self.m_scrolledWindow1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		fgSizer6.Add( self.m_staticline11, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_staticText7 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"MSD points", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )
		fgSizer6.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl4 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrl4, 0, wx.ALL, 5 )
		
		self.m_staticText8 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Time Interval", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )
		fgSizer6.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl5 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrl5, 0, wx.ALL, 5 )
		
		self.m_staticText10 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"D column label (exact match)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText10.Wrap( -1 )
		fgSizer6.Add( self.m_staticText10, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl8 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrl8, 0, wx.ALL, 5 )
		
		self.m_staticText11 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Log column label (generated)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )
		fgSizer6.Add( self.m_staticText11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl9 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrl9, 0, wx.ALL, 5 )
		
		self.m_staticText12 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Min limit", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )
		fgSizer6.Add( self.m_staticText12, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl10 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrl10, 0, wx.ALL, 5 )
		
		self.m_staticText13 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Max limit", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText13.Wrap( -1 )
		fgSizer6.Add( self.m_staticText13, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl11 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrl11, 0, wx.ALL, 5 )
		
		self.m_staticText14 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Binwidth", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText14.Wrap( -1 )
		fgSizer6.Add( self.m_staticText14, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl12 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrl12, 0, wx.ALL, 5 )
		
		self.m_staticText15 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Mobile Threshold", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText15.Wrap( -1 )
		fgSizer6.Add( self.m_staticText15, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_textCtrl13 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrl13, 0, wx.ALL, 5 )
		
		self.m_staticline12 = wx.StaticLine( self.m_scrolledWindow1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		fgSizer6.Add( self.m_staticline12, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_staticline13 = wx.StaticLine( self.m_scrolledWindow1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		fgSizer6.Add( self.m_staticline13, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_staticText21 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Group 1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText21.Wrap( -1 )
		fgSizer6.Add( self.m_staticText21, 0, wx.ALL, 5 )
		
		self.m_tcGroup1 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_tcGroup1, 0, wx.ALL, 5 )
		
		self.m_staticText22 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Group 2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText22.Wrap( -1 )
		fgSizer6.Add( self.m_staticText22, 0, wx.ALL, 5 )
		
		self.m_tcGroup2 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_tcGroup2, 0, wx.ALL, 5 )
		
		self.m_staticText61 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Cell ID (from this number of subfolders)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText61.Wrap( -1 )
		self.m_staticText61.SetToolTipString( u"Generates a unique ID for each cell from specified number of foldernames" )
		
		fgSizer6.Add( self.m_staticText61, 0, wx.ALL, 5 )
		
		self.m_tcCellid = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, u"3", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_tcCellid, 0, wx.ALL, 5 )
		
		self.m_staticText66 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Group By ROI", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText66.Wrap( -1 )
		fgSizer6.Add( self.m_staticText66, 0, wx.ALL, 5 )
		
		self.m_cbROI = wx.CheckBox( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_cbROI, 0, wx.ALL, 5 )
		
		
		self.m_scrolledWindow1.SetSizer( fgSizer6 )
		self.m_scrolledWindow1.Layout()
		fgSizer6.Fit( self.m_scrolledWindow1 )
		fgSizer1.Add( self.m_scrolledWindow1, 1, wx.EXPAND |wx.ALL, 5 )
		
		bSizer22 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btnLoadConfig = wx.Button( self, wx.ID_ANY, u"Load From File", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer22.Add( self.btnLoadConfig, 0, wx.ALL, 5 )
		
		self.btnSaveNew = wx.Button( self, wx.ID_ANY, u"Save As", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer22.Add( self.btnSaveNew, 0, wx.ALL, 5 )
		
		self.btnSave = wx.Button( self, wx.ID_ANY, u"Save Changes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnSave.SetDefault() 
		self.btnSave.SetForegroundColour( wx.Colour( 255, 255, 0 ) )
		self.btnSave.SetBackgroundColour( wx.Colour( 0, 128, 0 ) )
		
		bSizer22.Add( self.btnSave, 0, wx.ALL, 5 )
		
		
		fgSizer1.Add( bSizer22, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer1 )
		self.Layout()
		fgSizer1.Fit( self )
		
		# Connect Events
		self.btnLoadConfig.Bind( wx.EVT_BUTTON, self.OnLoadConfig )
		self.btnSaveNew.Bind( wx.EVT_BUTTON, self.OnSaveNew )
		self.btnSave.Bind( wx.EVT_BUTTON, self.OnSaveConfig )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnLoadConfig( self, event ):
		event.Skip()
	
	def OnSaveNew( self, event ):
		event.Skip()
	
	def OnSaveConfig( self, event ):
		event.Skip()
	

###########################################################################
## Class ProcessPanel
###########################################################################

class ProcessPanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL )
		
		bSizer19 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText85 = wx.StaticText( self, wx.ID_ANY, u"Run Selected Processes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText85.Wrap( -1 )
		self.m_staticText85.SetFont( wx.Font( 14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		
		bSizer19.Add( self.m_staticText85, 0, wx.ALL, 5 )
		
		self.m_staticline7 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer19.Add( self.m_staticline7, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizer20 = wx.BoxSizer( wx.HORIZONTAL )
		
		m_checkListProcessChoices = []
		self.m_checkListProcess = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkListProcessChoices, wx.LB_MULTIPLE )
		self.m_checkListProcess.SetMinSize( wx.Size( 300,200 ) )
		
		bSizer20.Add( self.m_checkListProcess, 0, wx.ALL, 5 )
		
		bSizer15 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_stTitle = wx.StaticText( self, wx.ID_ANY, u"TITLE", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stTitle.Wrap( -1 )
		self.m_stTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		
		bSizer15.Add( self.m_stTitle, 0, wx.ALL, 5 )
		
		self.m_stDescription = wx.StaticText( self, wx.ID_ANY, u"Process Description", wx.DefaultPosition, wx.Size( -1,80 ), 0|wx.FULL_REPAINT_ON_RESIZE )
		self.m_stDescription.Wrap( -1 )
		self.m_stDescription.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		
		bSizer15.Add( self.m_stDescription, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText57 = wx.StaticText( self, wx.ID_ANY, u"FILES IN", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText57.Wrap( -1 )
		self.m_staticText57.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		
		bSizer15.Add( self.m_staticText57, 0, wx.ALL, 5 )
		
		self.m_stFilesin = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stFilesin.Wrap( -1 )
		bSizer15.Add( self.m_stFilesin, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText59 = wx.StaticText( self, wx.ID_ANY, u"FILES OUT", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText59.Wrap( -1 )
		self.m_staticText59.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		
		bSizer15.Add( self.m_staticText59, 0, wx.ALL, 5 )
		
		self.m_stFilesout = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stFilesout.Wrap( -1 )
		bSizer15.Add( self.m_stFilesout, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5 )
		
		bSizer16 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_cbIndivplots = wx.CheckBox( self, wx.ID_ANY, u"Display Individual popup plots", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_cbIndivplots.SetToolTipString( u"Individual plots can be displayed for each file - this pauses the process until the plot is closed. On some systems, security settings may prevent these being displayed but they are also generated as PNG." )
		
		bSizer16.Add( self.m_cbIndivplots, 0, wx.ALL, 5 )
		
		self.m_cbShowplots = wx.CheckBox( self, wx.ID_ANY, u"Display Interactive Plots", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_cbShowplots.SetValue(True) 
		self.m_cbShowplots.SetToolTipString( u"Interactive plots are generated as HTML so may require an open browser or accept security warning to display" )
		
		bSizer16.Add( self.m_cbShowplots, 0, wx.ALL, 5 )
		
		bSizer17 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_btnRunProcess = wx.Button( self, wx.ID_ANY, u"Run", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnRunProcess.SetForegroundColour( wx.Colour( 255, 255, 0 ) )
		self.m_btnRunProcess.SetBackgroundColour( wx.Colour( 0, 128, 0 ) )
		
		bSizer17.Add( self.m_btnRunProcess, 0, wx.ALL, 5 )
		
		self.m_btnLog = wx.Button( self, wx.ID_ANY, u"View Log file", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.m_btnLog, 0, wx.ALL, 5 )
		
		
		bSizer16.Add( bSizer17, 1, wx.EXPAND, 5 )
		
		
		bSizer15.Add( bSizer16, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer20.Add( bSizer15, 1, wx.EXPAND, 5 )
		
		
		bSizer19.Add( bSizer20, 1, wx.EXPAND, 5 )
		
		bSizer21 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_dataViewListCtrlRunning = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_ROW_LINES )
		self.m_dataViewListCtrlRunning.SetMinSize( wx.Size( -1,400 ) )
		
		self.m_dataViewListColumnProcess = self.m_dataViewListCtrlRunning.AppendTextColumn( u"Process" )
		self.m_dataViewListColumnStatus = self.m_dataViewListCtrlRunning.AppendProgressColumn( u"Status" )
		self.m_dataViewListColumnOutput = self.m_dataViewListCtrlRunning.AppendTextColumn( u"Output" )
		bSizer21.Add( self.m_dataViewListCtrlRunning, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer19.Add( bSizer21, 1, wx.EXPAND, 5 )
		
		self.m_stOutputlog = wx.StaticText( self, wx.ID_ANY, u"View processing output in log file", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stOutputlog.Wrap( -1 )
		bSizer19.Add( self.m_stOutputlog, 0, wx.ALL, 5 )
		
		
		self.SetSizer( bSizer19 )
		self.Layout()
		bSizer19.Fit( self )
		
		# Connect Events
		self.m_checkListProcess.Bind( wx.EVT_LISTBOX, self.OnShowDescription )
		self.m_checkListProcess.Bind( wx.EVT_CHECKLISTBOX, self.OnShowDescription )
		self.m_btnRunProcess.Bind( wx.EVT_BUTTON, self.OnRunScripts )
		self.m_btnLog.Bind( wx.EVT_BUTTON, self.OnShowLog )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnShowDescription( self, event ):
		event.Skip()
	
	
	def OnRunScripts( self, event ):
		event.Skip()
	
	def OnShowLog( self, event ):
		event.Skip()
	

###########################################################################
## Class ComparePanel
###########################################################################

class ComparePanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 781,1025 ), style = wx.SIMPLE_BORDER|wx.TAB_TRAVERSAL )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText18 = wx.StaticText( self, wx.ID_ANY, u"Comparison of Group Statistics", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText18.Wrap( -1 )
		self.m_staticText18.SetFont( wx.Font( 14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		
		bSizer1.Add( self.m_staticText18, 0, wx.ALIGN_LEFT|wx.ALL, 5 )
		
		self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline1, 0, wx.EXPAND, 5 )
		
		self.m_staticText62 = wx.StaticText( self, wx.ID_ANY, u"Statistical comparison as independent t-tests for mobile/immobile ratios and areas. ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText62.Wrap( -1 )
		bSizer1.Add( self.m_staticText62, 0, wx.ALL, 5 )
		
		self.m_staticText58 = wx.StaticText( self, wx.ID_ANY, u"Data is compared from generated files for ratios, areas, avg MSD and avg Log10D for each group. Provide matching prefix as group name or use Load Group Prefixes button. A four panel plot will be generated.", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
		self.m_staticText58.Wrap( 650 )
		self.m_staticText58.SetFont( wx.Font( 9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		
		bSizer1.Add( self.m_staticText58, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_btnDefaults = wx.Button( self, wx.ID_ANY, u"Load Group Prefixes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnDefaults.SetToolTipString( u"Load fields with defaults from configuration and files panel" )
		
		bSizer1.Add( self.m_btnDefaults, 0, wx.ALL, 5 )
		
		fgSizer2 = wx.FlexGridSizer( 3, 4, 0, 0 )
		fgSizer2.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_NONE )
		
		self.m_staticText19 = wx.StaticText( self, wx.ID_ANY, u"Group 1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText19.Wrap( -1 )
		fgSizer2.Add( self.m_staticText19, 0, wx.ALL, 5 )
		
		self.m_tcGp1 = wx.TextCtrl( self, wx.ID_ANY, u"STIM", wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer2.Add( self.m_tcGp1, 0, wx.ALL, 5 )
		
		self.m_tcGp1Files = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 256,-1 ), 0 )
		fgSizer2.Add( self.m_tcGp1Files, 0, wx.ALL, 5 )
		
		self.m_btnGp1 = wx.Button( self, wx.ID_ANY, u"Browse", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer2.Add( self.m_btnGp1, 0, wx.ALL, 5 )
		
		self.m_staticText20 = wx.StaticText( self, wx.ID_ANY, u"Group 2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText20.Wrap( -1 )
		fgSizer2.Add( self.m_staticText20, 0, wx.ALL, 5 )
		
		self.m_tcGp2 = wx.TextCtrl( self, wx.ID_ANY, u"NOSTIM", wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer2.Add( self.m_tcGp2, 0, wx.ALL, 5 )
		
		self.m_tcGp2Files = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 256,-1 ), 0 )
		fgSizer2.Add( self.m_tcGp2Files, 0, wx.ALL, 5 )
		
		self.m_btnGp2 = wx.Button( self, wx.ID_ANY, u"Browse", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer2.Add( self.m_btnGp2, 0, wx.ALL, 5 )
		
		self.m_btnCompareRun = wx.Button( self, wx.ID_ANY, u"Run", wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
		self.m_btnCompareRun.SetForegroundColour( wx.Colour( 255, 255, 0 ) )
		self.m_btnCompareRun.SetBackgroundColour( wx.Colour( 0, 128, 64 ) )
		
		fgSizer2.Add( self.m_btnCompareRun, 0, wx.ALL, 5 )
		
		
		bSizer1.Add( fgSizer2, 1, wx.ALL, 5 )
		
		bSizer18 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_tcResults = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 500,350 ), wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP|wx.SIMPLE_BORDER )
		bSizer18.Add( self.m_tcResults, 0, wx.EXPAND, 5 )
		
		
		bSizer1.Add( bSizer18, 1, wx.ALIGN_TOP|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		# Connect Events
		self.m_btnDefaults.Bind( wx.EVT_BUTTON, self.OnLoadDefaults )
		self.m_btnGp1.Bind( wx.EVT_BUTTON, self.OnBrowseGp1 )
		self.m_btnGp2.Bind( wx.EVT_BUTTON, self.OnBrowseGp2 )
		self.m_btnCompareRun.Bind( wx.EVT_BUTTON, self.OnCompareRun )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnLoadDefaults( self, event ):
		event.Skip()
	
	def OnBrowseGp1( self, event ):
		event.Skip()
	
	def OnBrowseGp2( self, event ):
		event.Skip()
	
	def OnCompareRun( self, event ):
		event.Skip()
	

###########################################################################
## Class WelcomePanel
###########################################################################

class WelcomePanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL )
		
		bSizer18 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText23 = wx.StaticText( self, wx.ID_ANY, u"Automated Analysis for SPT", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText23.Wrap( -1 )
		self.m_staticText23.SetFont( wx.Font( 14, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		
		bSizer18.Add( self.m_staticText23, 0, wx.ALL, 5 )
		
		self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer18.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY|wx.NO_BORDER|wx.WANTS_CHARS, wx.DefaultValidator, u"welcome" )
		bSizer18.Add( self.m_richText1, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer18 )
		self.Layout()
		bSizer18.Fit( self )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class FilesPanel
###########################################################################

class FilesPanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 771,747 ), style = wx.TAB_TRAVERSAL )
		
		bSizer5 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText23 = wx.StaticText( self, wx.ID_ANY, u"Select Files for analysis", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText23.Wrap( -1 )
		self.m_staticText23.SetFont( wx.Font( 14, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		
		bSizer5.Add( self.m_staticText23, 0, wx.ALL, 5 )
		
		self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, u"Browse to top level directory then AutoFind and/or manually add initial data files with Drag N Drop. ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText25.Wrap( -1 )
		self.m_staticText25.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		
		bSizer5.Add( self.m_staticText25, 0, wx.ALL, 5 )
		
		self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer5.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )
		
		fgSizer4 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer4.SetFlexibleDirection( wx.BOTH )
		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_NONE )
		
		self.m_staticText26 = wx.StaticText( self, wx.ID_ANY, u"Top level directory", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText26.Wrap( -1 )
		fgSizer4.Add( self.m_staticText26, 0, wx.ALL, 5 )
		
		self.txtInputdir = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
		fgSizer4.Add( self.txtInputdir, 0, wx.ALL, 5 )
		
		self.m_button18 = wx.Button( self, wx.ID_ANY, u"Browse", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.m_button18, 0, wx.ALL, 5 )
		
		self.m_staticText67 = wx.StaticText( self, wx.ID_ANY, u"Output directory (batch output)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText67.Wrap( -1 )
		self.m_staticText67.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		
		fgSizer4.Add( self.m_staticText67, 0, wx.ALL, 5 )
		
		self.txtOutputdir = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
		fgSizer4.Add( self.txtOutputdir, 0, wx.ALL, 5 )
		
		self.m_button19 = wx.Button( self, wx.ID_ANY, u"Browse", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.m_button19, 0, wx.ALL, 5 )
		
		self.m_staticText27 = wx.StaticText( self, wx.ID_ANY, u"Expt prefix (search text)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText27.Wrap( -1 )
		self.m_staticText27.SetToolTipString( u"Select files with this search text (eg experiment code).  This is used as the prefix for batch compiled files." )
		
		fgSizer4.Add( self.m_staticText27, 0, wx.ALL, 5 )
		
		self.m_tcSearch = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
		fgSizer4.Add( self.m_tcSearch, 0, wx.ALL, 5 )
		
		self.btnAutoFind = wx.Button( self, wx.ID_ANY, u"AutoFind", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnAutoFind.SetForegroundColour( wx.Colour( 255, 255, 0 ) )
		self.btnAutoFind.SetBackgroundColour( wx.Colour( 0, 128, 64 ) )
		
		fgSizer4.Add( self.btnAutoFind, 0, wx.ALL, 5 )
		
		self.m_cbSelectall = wx.CheckBox( self, wx.ID_ANY, u"Select All", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_cbSelectall.SetValue(True) 
		fgSizer4.Add( self.m_cbSelectall, 0, wx.ALL, 5 )
		
		self.m_tcDragdrop = wx.TextCtrl( self, wx.ID_ANY, u"Drag data files here (eg AllROI-D.txt)", wx.DefaultPosition, wx.Size( 300,100 ), wx.TE_READONLY|wx.TE_WORDWRAP )
		self.m_tcDragdrop.SetBackgroundColour( wx.Colour( 191, 191, 255 ) )
		
		fgSizer4.Add( self.m_tcDragdrop, 0, 0, 5 )
		
		self.m_cbMatchAny = wx.CheckBox( self, wx.ID_ANY, u"AutoFind Match Any ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_cbMatchAny.SetToolTipString( u"Match Any Filename ending with Datafile filename" )
		
		fgSizer4.Add( self.m_cbMatchAny, 0, wx.ALL, 5 )
		
		self.m_staticText63 = wx.StaticText( self, wx.ID_ANY, u"Assign Group to selected files", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText63.Wrap( -1 )
		fgSizer4.Add( self.m_staticText63, 0, wx.ALL, 5 )
		
		m_cbGroupsChoices = []
		self.m_cbGroups = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 200,-1 ), m_cbGroupsChoices, 0 )
		self.m_cbGroups.SetSelection( 0 )
		fgSizer4.Add( self.m_cbGroups, 0, wx.ALL, 5 )
		
		self.m_button181 = wx.Button( self, wx.ID_ANY, u"Assign", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.m_button181, 0, wx.ALL, 5 )
		
		self.m_staticText64 = wx.StaticText( self, wx.ID_ANY, u"Store Selected File List", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText64.Wrap( -1 )
		fgSizer4.Add( self.m_staticText64, 0, wx.ALL, 5 )
		
		bSizer17 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button21 = wx.Button( self, wx.ID_ANY, u"Load list", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.m_button21, 0, wx.ALL, 5 )
		
		self.m_button20 = wx.Button( self, wx.ID_ANY, u"Save list", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.m_button20, 0, wx.ALL, 5 )
		
		self.btnClearlist = wx.Button( self, wx.ID_ANY, u"Clear list", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.btnClearlist, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		
		fgSizer4.Add( bSizer17, 1, wx.EXPAND, 5 )
		
		
		bSizer5.Add( fgSizer4, 1, wx.ALIGN_TOP|wx.EXPAND, 5 )
		
		bSizer18 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_dataViewListCtrl1 = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.dataview.DV_MULTIPLE )
		self.m_dataViewListCtrl1.SetMinSize( wx.Size( -1,300 ) )
		
		self.col_selected = self.m_dataViewListCtrl1.AppendToggleColumn( u"Select" )
		self.col_group = self.m_dataViewListCtrl1.AppendTextColumn( u"Group" )
		self.col_file = self.m_dataViewListCtrl1.AppendTextColumn( u"File" )
		bSizer18.Add( self.m_dataViewListCtrl1, 0, wx.ALIGN_TOP|wx.ALL|wx.EXPAND, 5 )
		
		self.m_status = wx.StaticText( self, wx.ID_ANY, u"Select required files then go to Run Processes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_status.Wrap( -1 )
		bSizer18.Add( self.m_status, 0, wx.ALL, 5 )
		
		
		bSizer5.Add( bSizer18, 1, wx.ALIGN_TOP|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer5 )
		self.Layout()
		
		# Connect Events
		self.m_button18.Bind( wx.EVT_BUTTON, self.OnInputdir )
		self.m_button19.Bind( wx.EVT_BUTTON, self.OnOutputdir )
		self.btnAutoFind.Bind( wx.EVT_BUTTON, self.OnAutofind )
		self.m_cbSelectall.Bind( wx.EVT_CHECKBOX, self.OnSelectall )
		self.m_button181.Bind( wx.EVT_BUTTON, self.OnAssignGroup )
		self.m_button21.Bind( wx.EVT_BUTTON, self.OnLoadList )
		self.m_button20.Bind( wx.EVT_BUTTON, self.OnSaveList )
		self.btnClearlist.Bind( wx.EVT_BUTTON, self.OnClearlist )
		self.m_dataViewListCtrl1.Bind( wx.dataview.EVT_DATAVIEW_COLUMN_HEADER_CLICK, self.OnColClick, id = wx.ID_ANY )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnInputdir( self, event ):
		event.Skip()
	
	def OnOutputdir( self, event ):
		event.Skip()
	
	def OnAutofind( self, event ):
		event.Skip()
	
	def OnSelectall( self, event ):
		event.Skip()
	
	def OnAssignGroup( self, event ):
		event.Skip()
	
	def OnLoadList( self, event ):
		event.Skip()
	
	def OnSaveList( self, event ):
		event.Skip()
	
	def OnClearlist( self, event ):
		event.Skip()
	
	def OnColClick( self, event ):
		event.Skip()
	

###########################################################################
## Class dlgLogViewer
###########################################################################

class dlgLogViewer ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Log viewer", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer18 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_txtLog = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP )
		self.m_txtLog.SetMinSize( wx.Size( 400,500 ) )
		
		bSizer18.Add( self.m_txtLog, 0, wx.ALL, 5 )
		
		
		self.SetSizer( bSizer18 )
		self.Layout()
		bSizer18.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

