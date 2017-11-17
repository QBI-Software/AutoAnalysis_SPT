# -*- coding: utf-8 -*-
"""
MSD Analysis script: compareMSD
Compiles MSD data from directories - expects input format:

STIM OR NOSTIM
 | -- cell1                                         <-- uses this name as cell ID
        | -- celldata
                 | -- Filtered_MSD.csv files    <-- this name must match (generated from histogramLogD)

and compiles to top level as <prefix>_AllMSD.csv where prefix can be STIM, NOSTIM (example)

Analysis per run (prefix):
      1. All cells data with Mean, SEM, Count, STD per timepoint - appended to compiled file
      2. Overlay MSD vs timepoints -> Calculate Area Under Curve -> add to file
      3. Plot Avg MSD with SD
(Data files encoded in ISO-8859-1)


Created on Tue Sep 5 2017

@author: Liz Cooper-Williams, QBI
"""

import argparse
import logging
from collections import OrderedDict
from os.path import join

import matplotlib.pyplot as plt
import pandas as pd
from numpy import sqrt, trapz
from plotly import offline
from plotly.graph_objs import Layout, Scatter

from msdapp.msd.batchStats import BatchStats


class CompareMSD(BatchStats):
    def __init__(self, *args):
        self.datafield = 'FILTERED_MSD'
        super().__init__(*args)
        if self.config is not None:
            self.datafile = self.config['FILTERED_MSD']
            self.outputfile = self.config['AVGMSD_FILENAME']
            self.msdpoints = int(self.config['MSD_POINTS'])
            self.timeint = float(self.config['TIME_INTERVAL'])
            print("MSD: Config file loaded")
        else:  # defaults
            self.outputfile = 'Avg_MSD.csv'
            self.datafile = 'Filtered_MSD.csv'
            self.msdpoints = 10
            self.timeint = 0.02
            print("MSD: Using config defaults")

        self.compiledfile = join(self.outputdir, self.searchtext + "_" + self.outputfile)
        self.compiled = self.__compile()
        self.saveCompiled()

    def __compile(self):
        try:
            # Compile all selected files
            timepoints = [str(x) for x in range(1, self.msdpoints + 1)]
            cols = ['Cell', 'Stats'] + timepoints
            data = pd.DataFrame(columns=cols, dtype=float)
            ctr = 0

            for f in self.inputfiles:
                df = pd.read_csv(f)
                cell = self.generateID(f)
                stats = OrderedDict({'avgs': [cell, 'Mean'],
                                     'counts': [cell, 'Count'],
                                     'stds': [cell, 'Std'],
                                     'sems': [cell, 'SEM'],
                                     'medians': [cell, 'Median']})

                for i in timepoints:
                    stats['avgs'].append(df[i].mean())
                    stats['counts'].append(df[i].count())
                    stats['stds'].append(df[i].std())
                    stats['sems'].append(df[i].std() / sqrt(df[i].count()))
                    stats['medians'].append(df[i].median())

                for key in stats.keys():
                    data.loc[ctr] = stats[key]
                    ctr += 1

            # Calculate avgs of avg
            cell = 'ALL'
            stats = OrderedDict({'avgs': [cell, 'Mean'],
                                 'counts': [cell, 'Count'],
                                 'stds': [cell, 'Std'],
                                 'sems': [cell, 'SEM'],
                                 'medians': [cell, 'Median']})
            for i in timepoints:
                d = data.groupby(['Stats'])[i].mean()
                logging.debug(d)
                stats['avgs'].append(d['Mean'])
                stats['counts'].append(d['Count'])
                stats['stds'].append(d['Std'])
                stats['sems'].append(d['SEM'])
                stats['medians'].append(d['Median'])
            for key in stats.keys():
                data.loc[ctr] = stats[key]
                ctr += 1

            # Sort by Stats
            df1 = data.sort_values(by=['Stats', 'Cell'])
            return df1
        except Exception as e:
            raise e

    def saveCompiled(self):
        if not self.compiled.empty:
            self.compiled.to_csv(self.compiledfile, index=False)
            logging.info("BatchMSD: Data saved to " + self.compiledfile)

    def calculateAreas(self):
        print('Calculating Area under curve of MSDs')
        areasfile = join(self.outputdir, self.searchtext + "_areas.csv")
        if self.compiled is not None:
            df = self.compiled
            means = df.groupby('Stats').get_group('Mean')
            sems = df.groupby('Stats').get_group('SEM')
            x = [str(x) for x in range(1, self.msdpoints + 1)]
            xi = [x * self.timeint for x in range(1, self.msdpoints + 1)]
            labels = []
            areas = []
            for ctr in range(0, len(means)):
                labels.append(means['Cell'].iloc[ctr])
                areas.append(trapz(means[x].iloc[ctr], dx=self.timeint))
            # save areas to new file
            df_area = pd.DataFrame({'Cell': labels, 'MSD Area': areas}, columns=['Cell', 'MSD Area'])
            df_area.to_csv(areasfile, index=False)
            print('Areas under curve calculated: %s', areasfile)
        return areasfile

    def showPlotoverlays(self, ax=None):
        """
        Plots each cells MSD, calculates areas and saves to areas file
        :param ax:
        :return: areas
        """
        print('Show Overlay of MSDs')
        if self.compiled is not None:
            df = self.compiled
            if ax is None:
                fig, ax = plt.subplots()
            means = df.groupby('Stats').get_group('Mean')
            sems = df.groupby('Stats').get_group('SEM')
            x = [str(x) for x in range(1, self.msdpoints + 1)]
            xi = [x * self.timeint for x in range(1, self.msdpoints + 1)]
            labels = []
            for ctr in range(0, len(means)):
                labels.append(means['Cell'].iloc[ctr])
                plt.errorbar(xi, means[x].iloc[ctr], yerr=sems[x].iloc[ctr] )

            plt.legend(labels, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., fancybox=True)
            plt.xlabel('Time (s)')
            plt.ylabel(r'MSD ($\mu$m$^2$)')
            plt.title(self.searchtext.upper() + ' MSDs per cell')
            # plt.show()

        else:
            raise ValueError("No MSD data to show")

    def showAvgPlot(self, ax=None):
        """
        Plot of avg MSD
        :param ax:
        :return:
        """
        logging.info('Show Avg MSD')
        if self.compiled is not None:
            df = self.compiled
            width = 0.15
            if ax is None:
                fig, ax = plt.subplots()
            x = [str(x) for x in range(1, self.msdpoints + 1)]
            xi = [x * self.timeint for x in range(1, self.msdpoints + 1)]  # convert to times
            all = df.groupby('Cell').get_group('ALL')
            allmeans = all.groupby('Stats').get_group('Mean')
            allsems = all.groupby('Stats').get_group('SEM')
            plt.errorbar(xi, allmeans[x].iloc[0], yerr=allsems[x].iloc[0],
                         capsize=3,
                         elinewidth=1,
                         markeredgewidth=1
                         )
            plt.title(self.searchtext.upper() + ' Average MSD')
            plt.xlabel('Time (s)')
            plt.ylabel(r'MSD ($\mu$m$^2$)')
            # plt.show()
        else:
            logging.error("No MSD data to show")

    def showPlotly(self):
        # Plotly Offline
        if self.compiled is not None:
            x = [str(x) for x in range(1, self.msdpoints + 1)]
            xi = [x * self.timeint for x in range(1, self.msdpoints + 1)]
            means = self.compiled.groupby('Stats').get_group('Mean')
            sems = self.compiled.groupby('Stats').get_group('SEM')
            data = []
            title = self.expt + ' [' + self.prefix.upper() + '] MSD n=' + str(len(means))
            for i in range(len(means)):
                if means['Cell'].iloc[i] == 'ALL':
                    data.append(Scatter(y=means[x].iloc[i], x=xi,
                                        error_y=dict(array=sems[x].iloc[i], type='data', symmetric=True),
                                        name=means['Cell'].iloc[i], mode='lines+markers',
                                        marker=dict(size=10, color='rgba(152, 0, 0, .8)',
                                                    line=dict(width=2, color='rgb(0, 0, 0)'))
                                        ))
                else:
                    data.append(Scatter(y=means[x].iloc[i], x=xi, name=means['Cell'].iloc[i], mode='lines+markers',
                                        error_y=dict(array=sems[x].iloc[i], type='data', symmetric=True)))
            # Create plotly plot
            pfilename = join(self.outputdir, self.searchtext.upper() + '_MSD.html')
            offline.plot({"data": data,
                                 "layout": Layout(title=title,
                                                  xaxis={'title': 'Time (s)'},
                                                  yaxis={'title': 'MSD (&mu;m<sup>2</sup>)'})},
                                filename=pfilename)
            return pfilename
        else:
            logging.error("No MSD data to show - plotly")

    def msdplot(self, showplots):
        """
        Run plot functions which also output figs and areas.csv with option to display
        :param fmsd:
        :return:
        """
        # matplotlib
        plt.figure(figsize=(8, 10))
        axes1 = plt.subplot(221)
        self.showPlotoverlays(axes1)
        axes2 = plt.subplot(223)
        self.showAvgPlot(axes2)

        figtype = 'png'  # png, pdf, ps, eps and svg.
        figname = self.compiledfile.replace('csv', figtype)
        plt.savefig(figname, facecolor='w', edgecolor='w', format=figtype)
        if showplots:
            plt.show()
            # plotly
            fname = self.showPlotly()
            print('View plotly file: ', fname)


#################################################################################################
if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
            Compiles histogram data from a directory (recursively looks for Filtered_MSD.csv) into an output file with stats

             ''')
    parser.add_argument('--filedir', action='store', help='Directory containing files', default="data")
    parser.add_argument('--outputdir', action='store', help='Output directory', default="data")
    parser.add_argument('--prefix', action='store', help='Prefix for compiled file eg STIM or NOSTIM', default="")
    parser.add_argument('--expt', action='store', help='ProteinCelltype as shown on directory names',
                        default="ProteinCelltype")
    parser.add_argument('--config', action='store', help='Config file for parameters',
                        default="..\\..\\resources\\msd.cfg")
    args = parser.parse_args()

    print("Loading Input from :", args.filedir)

    try:
        fmsd = CompareMSD(args.filedir, args.outputdir, args.prefix, args.expt, args.config)
        areasfile =fmsd.calculateAreas()
        fmsd.msdplot(showplots=True)
        #fmsd.showPlotly()


    except IOError as e:
        print("IOError: ", e)
    except ValueError as e:
        print("Error: ", e)
