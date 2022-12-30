#!/usr/bin/env python
r"""
Copy all files used in a main LaTeX file to a given directory.

- Requires git for LaTeX sources version control.
- Figures need to be included as::

  \def\figdir{<dirname>}
  ...
  \includegraphics[...]{\figdir/<filename>}
"""
from argparse import RawDescriptionHelpFormatter, ArgumentParser
import os
from functools import partial
import shutil
import subprocess

import soops as so

def _get_arg_of_command(filename, command, ext, single=True):
    out = subprocess.run(
        r'git grep \{} {}'.format(command, filename).split(),
        capture_output=True
    ).stdout.splitlines()

    srcs = []
    for _line in out:
        line = _line.decode().strip()
        if not line.startswith('%'):
            arg = line.split(command)[1].strip().strip('{')
            if '}' in arg:
                arg = arg[:arg.index('}')]

            srcs.append(arg + ext)
            if single:
                break

    return srcs

def get_srcs(filename):
    srcs = _get_arg_of_command(filename, r'\input', '', single=False)
    if len(srcs):
        sub = srcs.copy()
        for src in srcs:
            sub += get_srcs(src)

        return sub

    else:
        return []

def get_extra(filename):
    extra = []
    extra.extend(_get_arg_of_command(filename, r'\documentclass', '.cls',
                                     single=True))
    extra.extend(_get_arg_of_command(filename, r'\bibliographystyle', '.bst',
                                     single=True))
    extra.extend(_get_arg_of_command(filename, r'\bibliography{', '.bib',
                                     single=False))
    return extra

def get_figs(filename, exts=['.pdf', '.png']):
    aux = _get_arg_of_command(filename, r'\figdir', '', single=False)
    figdir = aux.pop(0)
    _figs = [os.path.join(figdir, ii[1:]) for ii in aux]
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

    srcs = (
        [options.main_tex_file]
        + get_srcs(options.main_tex_file)
        + get_extra(options.main_tex_file)
    )

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
