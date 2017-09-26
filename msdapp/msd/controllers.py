from flask import Blueprint, request, render_template, abort, redirect, url_for, send_from_directory
from jinja2 import TemplateNotFound
from msdapp.msd.forms import FilterMSDForm
from msdapp.msd.filterMSD import FilterMSD
from os.path import join, exists
from os import mkdir
from datetime import datetime
from msdapp import app
from zipfile import ZipFile
from werkzeug.utils import secure_filename

UPLOAD_PATH = app.config['UPLOAD_FOLDER']

simple_page = Blueprint('simple_page', __name__,
                        template_folder='templates',
                        static_folder=UPLOAD_PATH,
                        static_url_path="")

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
            form = FilterMSDForm(request.form)
            if request.method == 'POST' and form.validate():
                #form = FilterMSDForm(meta={'csrf_context': request.session})
                uid = datetime.today().strftime('%Y%m%d%H%M')
                data = request.files['datafile'].read()
                print("Uploads to: ",UPLOAD_PATH)
                outputdir = join(UPLOAD_PATH, uid) #create temp directory
                if (not exists(outputdir)):
                    mkdir(outputdir)
                datafile = join(outputdir, request.files['datafile'].filename)
                open(datafile,'wb').write(data)
                data = request.files['datafile_msd'].read()
                datafile_msd = join(outputdir,request.files['datafile_msd'].filename)
                open(datafile_msd, 'wb').write(data)

                minlimit = request.form['minlimit']
                maxlimit = request.form['maxlimit']
                #Run script class - should make this subprocess
                config = None
                fmsd = FilterMSD(config, datafile, datafile_msd, outputdir, int(minlimit), int(maxlimit))
                (fdata, fmsd, d1, d2, m1,m2) = fmsd.runFilter()
                datazipfile = join(outputdir, uid + "_filteredfiles.zip")
                with ZipFile(datazipfile, 'w') as myzip:
                    myzip.write(fdata)
                    myzip.write(fmsd)
                    myzip.write(datafile)
                    myzip.write(datafile_msd)
                result = {'fdata': fdata, 'fmsd': fmsd, 'd1':d1, 'd2':d2, 'm1':m1, 'm2':m2, 'zip': datazipfile}
        else:
            form = None

        return render_template('msd/%s.html' % page, navigation=navigation, page=page, form=form, result=result)
    except TemplateNotFound:
        abort(404)


@app.route('/uploads/<path:filename>', methods=['GET'])
def download(filename):
    # parts = filename.split('/')
    # print(parts)
    # downloadfile = join(app.config['UPLOAD_FOLDER'], parts[0])#,parts[1])
    print("Downloading: ", filename)
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'],filename=filename)
#https://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
