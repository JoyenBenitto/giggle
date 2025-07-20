# ============================================================================
# INCORE SEMICONDUCTORS PVT. LTD. Confidential
# Copyright (c) 2022-2024, INCORE SEMICONDUCTORS PVT. LTD.
# Project Name: device_manager 
# Project URL : https://gitlab.incoresemi.com/soc-utils/device_manager
# ============================================================================
#
# In the following text COMPANY refers to INCORE SEMICONDUCTORS PVT. LTD.
#
# The information contained herein is the proprietary and confidential 
# information of COMPANY or its licensors, and is supplied subject to, and may 
# be used only in accordance with, previously executed agreements with incore.        
#
# Except as may otherwise be agreed in writing: 
#
# (1) All materials furnished by COMPANY hereunder are provided "as is" 
#     without warranty of any kind. 
# (2) COMPANY specifically disclaims any warranty  relating to  fitness for a
#     particular purpose or merchantability or infringement of any patent, 
#     copyright or other intellectual property right. and 
# (3) COMPANY will not be liable for any costs of procurement of substitutes, 
#     loss of profits, interruption of business, or for any other special, 
#     consequential or incidental damages, however caused, whether for breach 
#     of warranty, contract, tort, negligence, strict liability or otherwise.
# ============================================================================


import os
import shutil
import click
import logging
from giggle import utils
from giggle import ssg
from giggle.__init__ import __version__

here = os.path.abspath(os.path.dirname(__file__))

# Top level group
@click.group()
@click.version_option(version=__version__)
def cli():
    ''' Command-line interface for bsv wrapper Generator '''

@click.version_option(version=__version__)

@click.option(
    '--recipe',
    help = 'Path to the giggle recipe',
    required = True
)

@click.option(
    '--verbose',
    '-v',
    default = 'info',
    show_default = True,
    help = 'Set verbose level for the console logs',
    type = click.Choice(['info', 'error', 'debug'])
)


@click.option(
    '--build-dir',
    '-bd',
    help = 'This argument sets the directory where the output files are stored',
    default='./build',
    show_default = True,
    required = False
)

@click.option(
    '--no_clear',
    is_flag=True,
    help= "Disables clone and clearing the dir"
)

@cli.command()
def gen_static_site(build_dir, recipe, verbose, no_clear):
    """Generate the static website"""

    logging.root.setLevel(verbose.upper())
    logger = logging.getLogger()
    logger.handlers = []
    ch = logging.StreamHandler()
    ch.setFormatter(utils.ColoredFormatter())
    logger.addHandler(ch)

    logger.info('************ Giggle Static Site Generator ************ ')
    logger.info('\n\n')

    #directory setup
    utils.directory_setup(build_dir, recipe)
    #Creating the build directory
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    logger.info("building...")
    os.makedirs(build_dir,exist_ok=True)
    recipe= utils.load_yaml(recipe)
    # utils.mover(f"{here}/other_const/.htaccess", f"{build_dir}/.htaccess")
    # utils.mover(f"{here}/other_const/vercel.json`", f"{build_dir}/vercel.json`")
    ssg_inst= ssg.ssg(recipe=recipe,
                      build=build_dir)
    ssg_inst.generate()

if __name__ == '__main__':
    main()