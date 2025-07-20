#!/usr/bin/env python
"""
Giggle - A powerful and flexible static site generator

Main entry point for the Giggle CLI.
"""

import os
import shutil
import logging
import click
from giggle import utils
from giggle import ssg
from giggle.cli.commands import cli
from giggle.__init__ import __version__


if __name__ == "__main__":
    cli()


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