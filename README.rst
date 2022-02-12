Line Profiler GUI
-----------------
.. image:: https://img.shields.io/github/license/Nodd/lineprofilergui
  :target: https://github.com/Nodd/lineprofilergui/blob/master/LICENSE.txt
.. image:: https://img.shields.io/pypi/v/line-profiler-gui.svg
  :target: https://pypi.python.org/pypi/line-profiler-gui/
.. image:: https://github.com/Nodd/lineprofilergui/actions/workflows/python-package.yml/badge.svg
  :target: https://github.com/Nodd/lineprofilergui/actions/workflows/python-package.yml
.. image:: https://codecov.io/gh/Nodd/lineprofilergui/branch/master/graph/badge.svg?token=9O1RMPUNEU
  :target: https://codecov.io/gh/Nodd/lineprofilergui

This is a Qt GUI for the line_profiler_ python utility.

It allows to run and display the profiling results using an interactive interface.
It is functionnaly equivalent to the ``kernprof`` script, which is used to invoque ``line_profiler`` from the command line.

.. image:: https://raw.githubusercontent.com/Nodd/lineprofilergui/master/images/screenshot_main.png
  :alt: Screenshot of Line Profier GUI main window
  :align: center

.. contents::


Features
========

* **Command line**: Configure and run from the command line, just like ``kernprof``,
* **GUI**: Configure and run from the GUI, just like ``kernprof`` but with buttons,
* **Colors**: Highlight lines based on the percentage of time spent on them to easily spot the lines to be optimised,
* **Configuration**: Setup warmup script, environment variables, and more!
* **History**: Compare timing with previous profiling runs,
* **Viewer**: Display data from any .lprof file by ``kernprof``,
* **Editor**: Double-click on any line to edit it with your favorite editor.

.. image:: https://raw.githubusercontent.com/Nodd/lineprofilergui/master/images/screenshot_config.png
  :alt: Screenshot of Line Profier GUI profiling configuration window
  :align: center

.. image:: https://raw.githubusercontent.com/Nodd/lineprofilergui/master/images/screenshot_settings.png
  :alt: Screenshot of Line Profier GUI application settings window
  :align: center


Installation
============

Line Profiler GUI can be installed from pypi using pip::

  $ pip install line-profiler-gui

Line Profiler GUI can use anyon of the Qt python bindings by using QtPy_: PyQt5, PyQt6, PySide2 or PySide6.
You can install the Qt python bindings of your choice in one go by specifying it between square brackets::

  $ pip install line-profiler-gui[PySide2]
  $ pip install line-profiler-gui[PyQt5]

Source releases can be downloaded from PyPI_. To check out the development sources, you can use Git_::

  $ git clone https://github.com/Nodd/lineprofilergui.git


Usage
=====

Users should be familiar with the line_profiler `line_profiler documentation <https://github.com/pyutils/line_profiler#id2>`_, but here is a quick reminder.
Since the line by line profiling slown down the execution, not all functions are profiled.
The functions to be profiled have to be marked with a ``@profile`` decorator (see the ``example/`` directory for more examples):

.. code-block:: python

    @profile
    def my_slow_function():
        ...

No import is needed, ``profile`` is added to the python builtins for the execution.
Don't forget to remove the added decorators afterwards!

Once the profilng is done, the following data will be disaplyed for each line of the decorated functions:

* **Line #**: The line number in the file.
* **Hits**: The number of times that line was executed.
* **Time**: The total amount of time spent executing the line.
* **Per Hit**: The average amount of time spent executing the line once.
* **% Time**: The percentage of time spent on that line relative to the total
  amount of recorded time spent in the function.
* **Line Contents**: The actual source code. Note that this is always read from
  disk when the formatted results are viewed, *not* when the code was
  executed. If you have edited the file in the meantime, the lines will not
  match up, and the formatter may not even be able to locate the function
  for display.

In the displayed table, the lines are higlighted depending on their `% Time`.
This allows to easily spot the lines to be optimised, and to not be distracted by the rest od the code.


Command line arguments
======================

.. code:: console

    $ lineprofilergui -h
    usage: lineprofilergui [-h] [-V] [-l LPROF] [-r] [-o OUTFILE] [-s SETUP]
                        [script] ...

    Run, profile a python script and display results.

    positional arguments:
    script                The python script file to run
    args                  Optional script arguments

    options:
    -h, --help            show this help message and exit
    -V, --version         show program's version number and exit
    -l LPROF, --lprof LPROF
                            Display data from a .lprof file
    -r, --run             Profile the python script on launch
    -o OUTFILE, --outfile OUTFILE
                            Save stats to OUTFILE (default: 'scriptname.lprof')
    -s SETUP, --setup SETUP
                            Python script to execute before the code to profile


See also
========

* `Spyder plugin <https://github.com/spyder-ide/spyder-line-profiler>`_
* `PyCharm plugin <https://plugins.jetbrains.com/plugin/16536-line-profiler>`_


.. _pypi: http://pypi.python.org/pypi/line-profiler-gui
.. _line_profiler: https://pypi.org/project/line_profiler/
.. _QtPy: https://pypi.org/project/QtPy/
.. _git: http://git-scm.com/
