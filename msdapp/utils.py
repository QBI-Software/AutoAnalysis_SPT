import logging
from os import access, R_OK, getcwd
from os.path import join, abspath, dirname


##### Global functions
def findResourceDir():
    # resource dir is at top level of cwd
    base = getcwd()
    logging.debug('Base:', base)
    resource_dir = join(base, 'resources')
    ctr = 0
    # loop up x times
    while(ctr < 5 and not access(resource_dir,R_OK)):
        base = dirname(base)
        logging.debug('Base:', base)
        resource_dir = join(base, 'resources')
        ctr += 1
    # if still cannot find - raise error
    if not access(resource_dir,R_OK):
        msg = 'Cannot locate resources dir: %s' % abspath(resource_dir)
        raise ValueError(msg)
    else:
        msg = 'Resources dir located to: %s ' % abspath(resource_dir)
        logging.info(msg)
    return abspath(resource_dir)