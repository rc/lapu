#!/usr/bin/env python
"""
Copy all files used in a main LaTeX file to a given directory.

Requires git for LaTeX sources version control.
"""
from argparse import RawDescriptionHelpFormatter, ArgumentParser
import os
from functools import partial
import shutil
import subprocess

import soops as so

def get_srcs(filename):
    out = subprocess.run(
        r'git grep \input {}'.format(filename).split(), capture_output=True
    ).stdout.splitlines()

    srcs = [ii.decode() for ii in out]
    srcs = [ii.split(r'\input')[1].strip().strip('{').strip('}') for ii in srcs]

    if len(srcs):
        sub = srcs.copy()
        for src in srcs:
            sub += get_srcs(src)

        return sub

    else:
        return []

def get_figs(filename, exts=['.pdf', '.png']):
    import re

    search = re.compile(r'\\figdir/(.*[^\}])\}').search

    out = subprocess.run(
        r'git grep \figdir/ {}'.format(filename).split(), capture_output=True
    ).stdout.splitlines()

    _figs = [ii.decode() for ii in out]
    _figs = ['figures/' + search(ii).groups()[0] for ii in _figs]
    figs = []
    for name in _figs:
        ext = os.path.splitext(name)[1]
        if ext and os.path.exists(name):
            figs.append(name)

        else:
            for ext in exts:
                ename = name + ext
                if os.path.exists(ename):
                    figs.append(ename)
                    break

            else:
                print(f'figure {name} not found!')

    return figs

def main():
    parser = ArgumentParser(description=__doc__.rstrip(),
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('main_tex_file')
    parser.add_argument('output_dir')
    options = parser.parse_args()

    srcs = [options.main_tex_file] + get_srcs(options.main_tex_file)
    figs = []
    for src in srcs:
        if src.endswith('.tex'):
            figs += get_figs(src)

    indir = partial(os.path.join, options.output_dir)

    for src in srcs:
        so.ensure_path(indir(src))
        try:
            shutil.copy2(src, indir(src))

        except:
            src += '.tex'
            try:
                shutil.copy2(src, indir(src))

            except:
                pass

    exts = ['.pdf', '.png']
    for fig in figs:
        so.ensure_path(indir(fig))
        ext = os.path.splitext(fig)[1]
        if ext:
            try:
                shutil.copy2(fig, indir(fig))

            except:
                pass

        else:
            for ext in exts:
                efig = fig + ext
                try:
                    shutil.copy2(efig, indir(efig))
                    break

                except:
                    continue

if __name__ == '__main__':
    main()
