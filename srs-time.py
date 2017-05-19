#!/usr/bin/env python
# encoding: utf-8
"""
 srstime.py

 This program will extract and plot the time taken at each step in an SRS run.

 Created by Chuck Wooters (wooters@icsi.berkeley.edu)
 Copyright (c) 2013 ICSI. All rights reserved.
"""
import os
import sys
import logging
import argparse
import shlex
import subprocess
import glob
from dateutil import parser as dparser
import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple

#
# Process the command line
#


def process_command_line():
    """
    Return a command line parser object
    """

    # initialize the command-line parser
    # for more info see: http://docs.python.org/library/argparse.html
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Compute the amount of time taken during each step in an SRS run.",
        epilog="")

    #
    # Required (positional) args
    #    (note: no "-" in arg name indicates that it is required)
    #
    parser.add_argument("srsdir", help="get time info from SRSDIR")

    #
    # Optional args:
    #
    parser.add_argument("-p", "--plot", default=False, action="store_true",
                        help="Plot a bar chart.")

    cmdline = parser.parse_args()

    # when all done with command line processing
    return cmdline


# Pretty print table of data
# taken from:
#   http://stackoverflow.com/questions/5909873/python-pretty-printing-ascii-tables
#
def pprinttable(rows):
    if len(rows) > 1:
        headers = rows[0]._fields
        lens = []
        for i in range(len(rows[0])):
            lens.append(
                len(max([x[i] for x in rows] + [headers[i]], key=lambda x: len(str(x)))))
        formats = []
        hformats = []
        for i in range(len(rows[0])):
            if isinstance(rows[0][i], int):
                formats.append("%%%dd" % lens[i])
            else:
                formats.append("%%-%ds" % lens[i])
            hformats.append("%%-%ds" % lens[i])
        pattern = " | ".join(formats)
        hpattern = " | ".join(hformats)
        separator = "-+-".join(['-' * n for n in lens])
        print hpattern % tuple(headers)
        print separator
        for line in rows:
            print pattern % tuple(line)
    elif len(rows) == 1:
        row = rows[0]
        hwidth = len(max(row._fields, key=lambda x: len(x)))
        for i in range(len(row)):
            print "%*s = %s" % (hwidth, row._fields[i], row[i])


#
# Main
#
def main():
    """
    Main processing loop of srstime.py
    """

    #
    # Read and process the command line
    #
    cmdline = process_command_line()

    # get a list of the "TIMES" log files
    timefiles = glob.glob(
        os.path.join(cmdline.srsdir, "SRS-GO", "logs", "TIMES.*"))

    # Extract time info from each time log
    timedata = []
    for tf in timefiles:
        lab = os.path.basename(tf)
        lab = lab.replace('TIMES.', '')
        with open(tf) as fh:
            times = fh.readlines()
        if len(times) == 2:
            st = dparser.parse(times[0])
            et = dparser.parse(times[1])
            dur = (et - st).seconds  # (et-st) is a datetime.timedelta object
            timedata.append((dur, lab))
        else:
            timedata.append((-1.0, lab))

    # Sort from largest to smallest
    timedata.sort(reverse=True)
    tothrs = sum([x[0] for x in timedata]) / 3600.0  # total time in hours
    totsecs = float(sum([x[0] for x in timedata]))

    # print results
    Row = namedtuple('Row', ['Step', 'Seconds', 'Hours', 'Percent'])
    data = []
    for s, l in timedata:
        data.append(Row(Step=l,
                        Seconds=s,
                        Hours='{0:5.2f}'.format(s / 3600.0),
                        Percent='{0:6.2f}%'.format(100.0 * s / totsecs)))

    print "Total time: {0:0.2f} hrs ({1:0.2f} days)".format(tothrs, tothrs / 24.0)
    print
    pprinttable(data)

    # If requested, plot the data
    if cmdline.plot:
        y_pos = np.arange(len(timedata))
        plt.barh(y_pos, [x[0] / totsecs for x in timedata], align='center')
        plt.yticks(y_pos, [x[1].replace(".", "\n") for x in timedata])
        plt.xlabel('% of total time')

        plt.title('Total Time: {0:0.2f} hrs'.format(tothrs))

        plt.show()

    return 0        # success


if __name__ == '__main__':
    sys.exit(main())
