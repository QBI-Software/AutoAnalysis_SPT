from flask import Blueprint, request, render_template, abort, redirect, url_for
from jinja2 import TemplateNotFound
from msdapp.msd.forms import FilterMSDForm
from msdapp.msd.filterMSD import FilterMSD
from os.path import join, exists
from os import mkdir
from werkzeug.utils import secure_filename


simple_page = Blueprint('simple_page', __name__,
                        template_folder='templates')

navigation=[{'caption': 'Home', 'href':'index', 'description':'Home page', 'files': ''},
                    {'caption': '1. Filter MSD', 'href':'filter', 'description':'Filters log10 diffusion coefficient (log10D) for input files', 'files': 'AllROI-D.txt, AllROI-MSD.txt'},
                    {'caption': '2. Histogram LogD', 'href':'histogram','description':'Create frequency histogram data for individual cells and all cells', 'files': 'Filtered_AllROI-D.txt'},
                    {'caption': '3. Compare MSD', 'href': 'compare','description':'Compiles MSD data from cell directories (batch)', 'files': 'Filtered_AllROI-MSD.csv files'},
                    {'caption': '4. Histogram Stats', 'href': 'stats','description':'Compiles histogram data from cell directories (batch)', 'files': 'Histogram_log10D.csv files'},
                    {'caption': '5. Ratio Stats', 'href': 'ratio','description':'Compares mobile/immobile ratios for two groups', 'files': 'STIM_ratios.csv, NOSTIM_ratios.csv'}
                    ]

@simple_page.route('/', defaults={'page': 'index'})
@simple_page.route('/<page>',methods=['GET','POST'])
def show(page):
    try:
        result=None
        if page == 'filter':
            form = FilterMSDForm(minlimit=-4, maxlimit=1)
            if request.method == 'POST':
                uid = 'ph4rc23r8'
                data = request.files['datafile'].read()
                datafile = join('uploads', uid + request.files['datafile'].filename)
                open(datafile,'wb').write(data)
                data = request.files['datafile_msd'].read()
                datafile_msd = join('uploads', uid + request.files['datafile_msd'].filename)
                open(datafile_msd, 'wb').write(data)
                outputdir = join('uploads', uid) #create temp directory
                if (not exists(outputdir)):
                    mkdir(outputdir)
                minlimit = request.form['minlimit']
                maxlimit = request.form['maxlimit']

                config = None
                fmsd = FilterMSD(config, datafile, datafile_msd, outputdir, int(minlimit), int(maxlimit))
                (fdata, fmsd) = fmsd.runFilter()
                #TODO - zip files for download and delete temporary
                result = {'fdata': fdata, 'fmsd': fmsd}
        else:
            form = None



        return render_template('msd/%s.html' % page, navigation=navigation, page=page, form=form, result=result)
    except TemplateNotFound:
        abort(404)


