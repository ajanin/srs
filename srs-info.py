#!/usr/bin/env python
# encoding: utf-8
"""
 srs-info.py

 This program extracts information from an SRS experiment directory.

 Created by Chuck Wooters (wooters@icsi.berkeley.edu)
 Copyright (c) 2013 ICSI. All rights reserved.
"""
import os
import sys
import re
import argparse
import subprocess
import glob
import string
import datetime
from dateutil import parser as dparser
from collections import defaultdict, Counter

ConfDict = {}  # Holds all config variables
VarRegExps = {}  # Holds compiled regexps for all config variables
Steps_Per_Var = {}  # For each variable, what steps use it

# Background colors to use at each nesting level of the steps
Level_Colors = ['#FFFFFF', '#FBF7F2', '#F3E7D7', '#E3D0B7', '#D6BEA0',
                '#CCAD88', '#BE9A6F', '#B18A5B', '#A17A4B', '#90693A']

# Beginning of the HTML doc that will be output
HTML_top = '''
<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset="utf-8">
<title>SRS-INFO</title>

<link rel="stylesheet" href="http://www.icsi.berkeley.edu/~wooters/highlightjs/default.min.css">
<link rel="stylesheet" href="http://www.icsi.berkeley.edu/~wooters/select2/select2.css"/>
<script src="http://www.icsi.berkeley.edu/~wooters/highlightjs/highlight.min.js"></script>
<script src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
<script src="http://code.jquery.com/jquery-migrate-1.2.1.min.js"></script>
<script src="http://www.icsi.berkeley.edu/~wooters/select2/select2.js"></script>
<script>
  $(document).ready(function() {
      $("#varsrch").select2();
      $("#varsrch").on("change", function(e) {
           window.location = "#"+e.val;
         });
  });
</script>
<script>
  hljs.tabReplace = '    ';
  hljs.initHighlightingOnLoad();
</script>

<style>
* {margin: 0px;}
#wrapper {
  margin: 0 auto;
  overflow: scroll;
}

#content {
  padding-top: 10px;
  padding-left: 350px;
  background-color: #FFF;
  word-wrap: break-word;
}

#nav li {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 18px;
  color: #725d4c;
  display: inline;
  padding-right: 35px;
  list-style-type: none;
}
#nav {float: left; width: 335px; padding-top: 85px;}
#nav li a {color: #725d4c; text-decoration: none;}
#nav li a:visited {color: #725d4c;}
#nav li a:hover {color: #FFF;}

#sidebar {
  position: fixed;
  background-color: #FBF7F2;
  width: 340px;
  height: 100%;
}
#main_sidebar {width: 249px; padding-top: 10px; padding-left: 10px;}
#main_sidebar p {
  font-family: Verdana, Geneva, sans-serif;
  font-size: 12px;
  line-height: 18px;
  color: #787d80;
  padding-bottom: 20px;
}
#main_sidebar li a {color: #725d4c; text-decoration: none;}
#main_sidebar li a:hover {color: #997b63;}
#main_sidebar ol ul {
  font-family: Verdana, Geneva, sans-serif;
  color: #725d4c;
}
#main_sidebar h2 {
  font-family: Verdana, Geneva, sans-serif;
  font-size: 18px;
  font-weight: 100;
  text-transform: uppercase;
  color: #7a6453;
  letter-spacing: 1px;
  padding-bottom: 10px;
}

.steppath {
  font-family: Verdana, Geneva, sans-serif;
  padding-left: 10px;
  padding-bottom: 10px;
}

.dirstep {
  position: relative;
  top: 15px;
  left: 20px;
  padding-top: 10px;
  padding-bottom: 25px;
  border-left-style: solid;
  border-bottom-style: dotted;
  overflow: wrap;
}

.step {
  position: relative;
  top: 15px;
  left: 20px;
  padding-top: 10px;
  padding-bottom: 25px;
  border-left-style: solid;
  border-bottom-style: dotted;
  overflow: wrap;
}

.textfile {
  font-family: "Courier New", Courier, monospace;
  font-size: 12px;
  padding: 10px;
}

#cvars {
  position: relative;
  top: 15px;
  left: 20px;
  padding-top: 20px;
  padding-bottom: 20px;
  overflow: scroll;
}

.cvar {
  padding-top: 10px;
  padding-bottom: 10px;
  border-bottom-style: dotted;
}

.configval {
  background-color: #eae6e6;
  margin-left: 20px;
}

.configvar {
  font-size: 18px;
}

dfn {
  font-weight: bold;
}

.newvar {
  color: #66CC00;
}

.changedvar {
  color: red;
}

.success {
  color: #66CC00;
}

.fail {
  color: red;
}

</style>

</head>


<body>

<div id="wrapper">

'''
# In the <style> section, use '#' for ids and '.' for classes


# Closing part of the HTML output
HTML_bot = '''
</div>
</body>
</html>
'''

class Step(object):

    """An object representing an SRS step"""

    # Regex pattern for searching for variables
    var_pat = r"(^|[^/w_-]){0}([^/w_-]|$)"

    def __init__(self, step_path):
        """
        Arguments:
        - `step_path`: the file path name of the SRS step
        """
        self.path = step_path
        self.contents = None  # contents of the step file
        self.readme = None  # contents of the README
        self.dfltcfg = None  # contents of default.config
        self.cmdline_config = None  # the command line config file
        self.subs = None    # sub-steps
        self.cfg = None     # all config vars (whether used or not)
        self.icfg = None     # used config vars at start of step (inputs)
        self.ocfg = None     # used config vars at end of step (outputs)
        self.duration = None  # duration in seconds for this step

        print >> sys.stderr, "Analyzing step: {0}".format(step_path)

        try:
            self.readme = open(os.path.join(step_path, 'README')).read()
        except:
            pass

        if os.path.isdir(step_path):

            # try to get the name of the command line config file
            dfltcfg_path = os.path.join(step_path, "default.config")
            try:
                self.dfltcfg = open(dfltcfg_path).read()
            except:
                pass

            # try to get the name of the command line config file
            cmdlinecfg = os.path.join(
                self.path, 'SRS-GO', 'config', 'COMMANDLINE.config')
            if os.path.exists(cmdlinecfg):
                for line in open(cmdlinecfg):
                    if line.startswith('config'):
                        self.cmdline_config = line.strip().split()[1]

            # build sub steps
            self._build_sub_steps()

        else:
            self.contents = open(step_path).read()

        # compute the duration of this step
        self._compute_duration()

        # make a dict containing *all* of variables used in this step,
        # and their values at the end of the step
        self.get_used_output_config_vars()

    def __str__(self):
        return self.path

    def _build_sub_steps(self):
        """Build all sub steps of this step"""
        if os.path.isdir(self.path):
            step_names = sorted(glob.glob(os.path.join(self.path, "step*")))
            self.subs = [Step(s) for s in step_names]

    def _compute_duration(self):
        """Return the total amount of time (in seconds) that this step
        took to execute."""

        if self.duration is not None:
            return

        if self.subs is None:  # a file step
            st, et = self.get_times()
            if st is None or et is None:
                self.duration = -1.0
            else:
                self.duration = (et - st).seconds
            return

        # Must be a dir step
        #  the elapsed time is equal to the sum of the
        #  elapsed times of the sub steps.
        subtimes = [s.get_duration() for s in self.subs]

        tot_bad_time = sum([abs(x) for x in subtimes if x < 0.0])
        if tot_bad_time > 0.0:
            self.completed = False

        self.duration = sum(subtimes) + tot_bad_time

    def get_duration(self):
        """Return the duration (execution time) of this step"""

        if self.duration is None:
            self._compute_duration()

        return self.duration

    def did_fail(self):
        """Return whether or not this step failed to run."""

        if self.subs is None:  # a file step
            if self.get_duration() < 0.0:
                return True
            return False

        return any([s.did_fail() for s in self.subs])

    def get_time_file(self):
        """Return the name of the timing file for this step"""
        bname = os.path.basename(self.path)
        return os.path.join(
            os.path.dirname(self.path), 'SRS-GO', 'logs', 'TIMES.'+bname)

    def get_times(self):
        """Return the start time and end time for this step"""
        try:
            with open(self.get_time_file()) as fh:
                times = fh.readlines()
        except IOError:
            return (None, None)

        try:
            st = dparser.parse(times[0])
        except IndexError:
            st = None

        try:
            et = dparser.parse(times[1])
        except IndexError:
            et = None

        return (st, et)

    def get_output_config_file(self):
        """Return the name of the output config file for this step. If
        this is a dir step, then the output config is the output
        config of the last file step that was executed. If no output
        config file was produced, it will return None."""

        if self.subs is None:          # must be a file step
            basecfg = 'OUTCONFIG.' + os.path.basename(self.path)
            cfg = os.path.join(
                os.path.dirname(self.path), 'SRS-GO', 'config', basecfg)
            if os.path.exists(cfg):
                return cfg
            else:
                return None

        # find last-executed step, starting from the end
        for s in reversed(self.subs):
            cfgname = s.get_output_config_file()
            if cfgname is not None:
                return cfgname

        return None

    def get_output_config_vars(self):
        """Return a dict containing *all* of the config variables and
        values at the end of this step."""

        if self.cfg is not None:  # short circuit if we have already read them
            return self.cfg

        self.cfg = {}
        cfgfile = self.get_output_config_file()
        if cfgfile is not None:
            self.cfg = read_config_vars(cfgfile)

        return self.cfg

    def get_used_output_config_vars(self):
        """Return a dict containing only the config variables that
        were used in this step and their values at the end of the step
        (output)."""

        if self.ocfg is not None:
            return self.ocfg

        allcfgs = self.get_output_config_vars()
        self.ocfg = {k: v for k, v in allcfgs.viewitems() if self.has_var(k)}

        return self.ocfg

    def has_var(self, var):
        """Returns true if the given variable is used in this step."""
        global VarRegExps

        if self.contents is None:
            return False

        try:
            v_re = VarRegExps[var]
        except KeyError:
            v_re = re.compile(Step.var_pat.format(var), flags=re.M)
            VarRegExps[var] = v_re

        itr = v_re.finditer(self.contents)
        found = True
        try:
            itr.next()  # try to get first match
        except StopIteration:  # will be thrown if iterator is empty (no match)
            found = False

        return found

    def html(self, priorcfg=None):
        """Return an html representation of this step."""

        pname, stepname = os.path.split(self.path)
        h_name = "{0}/<b>{1}</b>".format(pname, stepname)

        outstr = '<div class="steppath">{0}</div>\n'.format(h_name)

        dur = self.get_duration()
        if dur < 0.0:
            durstr = 'unknown'
        else:
            durstr = str(datetime.timedelta(seconds=dur))

        outstr += '<img src="hourglass.png" style="vertical-align:middle" width="20" alt="hour glass">{0}<br>\n'.format(durstr)
        if self.readme is not None:
            outstr += '<details>\n<summary>README</summary>\n'
            outstr += '<div class="textfile">\n'
            outstr += '<pre>\n'
            outstr += self.readme + '\n'
            outstr += '</pre>\n'
            outstr += '</div>\n'
            outstr += '</details>\n'

        cmdlinecfg = os.path.join(
            self.path, 'SRS-GO', 'config', 'COMMANDLINE.config')
        if os.path.exists(cmdlinecfg):
            outstr += '<details>\n<summary>COMMANDLINE.config</summary>\n'
            outstr += '<div class="textfile">\n'
            outstr += '<pre>\n'
            outstr += open(cmdlinecfg).read() + '\n'
            outstr += '</pre>\n'
            outstr += '</div>\n'
            outstr += '</details>\n'

        mastercfg = os.path.join(
            self.path, 'SRS-GO', 'config', 'MASTER.config')
        if os.path.exists(mastercfg):
            outstr += '<details>\n<summary>MASTER.config</summary>\n'
            outstr += '<div class="textfile">\n'
            outstr += '<pre>\n'
            outstr += open(mastercfg).read() + '\n'
            outstr += '</pre>\n'
            outstr += '</div>\n'
            outstr += '</details>\n'

        if self.dfltcfg is not None:
            outstr += '<details>\n<summary>default.config</summary>\n'
            outstr += '<div class="textfile"><pre>\n'
            outstr += '<pre>\n'
            outstr += self.dfltcfg + '\n'
            outstr += '</pre></div>\n'
            outstr += '</details>\n'

        if priorcfg is not None:
            # Get config vars and values as they were before this step
            self.icfg = {
                k: v for k, v in priorcfg.viewitems() if self.has_var(k)}

            if len(self.icfg) > 0:
                outstr += '<details>\n<summary>PRE-STEP CONFIG VARIABLES</summary>\n'
                outstr += '<p>The values shown are the values at <em>the beginning</em> of the step.</p>'
                outstr += '<br><ul>\n'
                for v in sorted(self.icfg):
                    val = self.icfg[v]
                    outstr += '<li><dfn>{0}</dfn>: {1}</li>\n'.format(v, val)
                outstr += '</ul><br>\n'
                outstr += '</details>\n'

        if self.contents is not None:
            outstr += '<details>\n<summary>STEP FILE</summary>\n'
            outstr += '<pre><code>\n'
            outstr += self.contents + '\n'
            outstr += '</code></pre><br>\n'
            outstr += '</details>\n'

        if self.ocfg is not None and len(self.ocfg) > 0:
            # Get config vars and valus as they were after this step
            anychanged = False
            anynew = False

            tmpstr = ''
            for v in sorted(self.ocfg):
                val = self.ocfg[v]
                if self.icfg is not None and v in self.icfg and self.icfg[v] != self.ocfg[v]:
                    tmpstr += '<li><dfn class="changedvar">{0}</dfn>: {1}</li>\n'.format(
                        v, val)
                    anychanged = True
                elif self.icfg is not None and v not in self.icfg:
                    tmpstr += '<li><dfn class="newvar">{0}</dfn>: {1}</li>\n'.format(
                        v, val)
                    anynew = True
                else:
                    tmpstr += '<li><dfn>{0}</dfn>: {1}</li>\n'.format(v, val)

            hints = ''
            if anychanged:
                hints += '<span class="changedvar">&#x2713;</span>'
            if anynew:
                hints += '<span class="newvar">&#x2713;</span>'
            outstr += '<details>\n<summary>POST-STEP CONFIG VARIABLES {0}</summary>\n'.format(
                hints)
            outstr += '<p>The values shown are the values at <em>the end</em> of the step.</p>'
            outstr += '<p>Vars that have changed are shown as <dfn class="changedvar">changedvar</dfn> '
            outstr += 'and vars that are new are shown as <dfn class="newvar">newvar</dfn>.</p>'
            outstr += '<br><ul>\n'

            outstr += tmpstr

            outstr += '</ul><br>\n'
            outstr += '</details>\n'

        if self.subs is not None:
            outstr += '<details>\n<summary>SUB-STEPS</summary>\n'
            outstr += '<ul>\n'
            for s in self.subs:
                sb = os.path.basename(s.path)
                outstr += '<li><a href="#{0}">{1}</a></li>\n'.format(s, sb)
            outstr += '</ul>\n'
            outstr += '</details>\n'

        return outstr

def print_steps_html(step, priorcfg=None, level=0, out=sys.stdout):
    """Generate a representation of the given step in html"""

    if step is None:
        return

    stype = "step"
    if step.subs is not None:
        stype = "dirstep"

    col = Level_Colors[level % len(Level_Colors)]
    print >> out, '<div id="{0}" class="{1}" style="background-color: {2}">\n'.format(step.path,
                                                                                      stype, col)

    # print an html representation of this node
    print >> out, step.html(priorcfg=priorcfg)

    if stype == "dirstep":
        if level == 0:
            if step.cmdline_config is not None:
                lastcfg = read_config_vars(step.cmdline_config)
            else:
                lastcfg = None
        else:
            lastcfg = step.get_output_config_vars()

        for s in step.subs:
            print_steps_html(s, priorcfg=lastcfg, level=level + 1, out=out)
            lastcfg = s.get_output_config_vars()

    print >> out, '</div>\n'


Config_Info = {}
def read_config_vars(cfgfile):
    """Return a dict containing the config vars and values for the
    given config file."""

    global Config_Info

    if cfgfile is None:
        return {}

    if cfgfile in Config_Info:     # check cache
        return Config_Info[cfgfile]

    retcode, output = shell("srs-config -dump -config {0}".format(cfgfile))
    if retcode != 0:
        print "Warning: can't get config vars for {0}:\n{1}".format(cfgfile, output)
        return {}

    cfg = {}
    for line in output.split('\n'):
        line = line.strip()
        if len(line) == 0:
            continue
        var, val = string.split(line, maxsplit=1)
        cfg[var] = val

    Config_Info[cfgfile] = cfg  # save to cache for next call

    return cfg


def find_in_step(varname, step):
    """Return a list of all step path names that contain a reference
    to the given variable name.
    
    Arguments:
    - `varname`: name of the variable to search for
    - `step`: a Step() object
    """
    steps = []
    if step.subs is None:  # leaf node
        if varname in step.get_used_output_config_vars():
            steps.append(step.path)
    else:
        for s in step.subs:
            steps.extend(find_in_step(varname, s))

    return steps

def make_index(step):
    """Create an index for the config variables
    
    Arguments:
    - `step`: The a Step() object
    """
    global ConfDict

    steps_per_var = {}
    for var in ConfDict:
        steps_per_var[var] = [x for x in find_in_step(var, step)]

    return steps_per_var


def process_command_line():
    """
    Return a command line parser object
    """

    # initialize the command-line parser
    # for more info see: http://docs.python.org/library/argparse.html
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Extract information from a given SRS exp dir",
        epilog="")

    #
    # Required (positional) args
    #    (note: no "-" in arg name indicates that it is required)
    #
    parser.add_argument("expdir", help="get info for this exp dir")
    parser.add_argument("-o", "--output", 
                        help="send html output to this file",
                        default=sys.stdout.name)

    cmdline = parser.parse_args()
    return cmdline


def shell(cmdline):
    """Run the given command line
    
    Arguments:
    - cmdline: A string containing the command line to run

    Returns:
      A tuple containing the return code and the output. The
      return code should be checked to make sure it is 0. If it
      is not 0, then the output will contain the error message.
    """

    args = cmdline
    retcode = 0
    try:
        output = subprocess.check_output(args, shell=shell,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        retcode = e.returncode
        output = e.output
    except OSError, e:
        retcode = -1
        output = "{0}".format(e)

    return (retcode, output)


def gen_ol(step):
    """Generate an html string containing an ordered list of the sub
    steps for the given step.
    
    Arguments:
    - `step`: a Step() object
    """
    if step.subs is None:
        return ""

    outstr = "<ol>\n"
    for s in step.subs:
        path = s.path
        disptxt = os.path.basename(s.path)
        if s.did_fail():
            status = '<span class="fail">&nbsp;&#x2717;</span>'
        else:
            status = '<span class="success">&nbsp;&#x2717;</span>'

        outstr += '<li><a href="#{0}">{1}</a>{2}</li>\n'.format(path,
                                                                disptxt, status)
    outstr += "</ol>\n"
    return outstr


def output_html(step, out=sys.stdout):

    global Steps_Per_Var, ConfDict
    global HTML_top, HTML_bot

    print >> out, HTML_top

    #
    # Navigation Sidebar
    #
    print >> out, '<div id="sidebar">\n'
    print >> out, '<div id="main_sidebar">\n'

    #  Steps
    print >> out, '<h2>Template Steps:</h2>\n'
    print >> out, gen_ol(step)

    #  Conf Vars
    print >> out, '<br><h2>Config Variables:</h2>\n'
    print >> out, '<select id="varsrch" data-placeholder="Config Var Search" style="width:300px">\n'
    print >> out, '<option></option>\n'  # need this for placeholder to work
    for v in sorted(ConfDict):
        print >> out, '<option value="{0}">{0}</option>\n'.format(v)
    print >> out, '</select>\n'

    #  Legend
    print >> out, '<br><br><h2>Legend:</h2>\n'
    print >> out, '<p><span class="fail">&nbsp;&#x2717;</span> = Step failed.<br>\n'
    print >> out, '<span class="success">&nbsp;&#x2717;</span> = Step completed successfully.<br><br>\n'
    print >> out, '<img src="hourglass.png" style="vertical-align:middle" width="20" alt="hour glass"> = Runtime (hh:mm:ss)<br>\n'
    print >> out, '<span class="changedvar"><b>&#x2713;</b></span> = A variable was changed.<br>\n'
    print >> out, '<span class="newvar"><b>&#x2713;</b></span> = A variable was added.</p>\n'

    print >> out, '</div>\n'
    print >> out, '</div>\n'
    #
    # End Navigation Sidebar
    #

    #
    # Main Body Content
    #
    print >> out, '<div id="content">\n'

    #   processing steps
    print >> out, '<section id="steps">\n'
    print >> out, '<h3>Processing Steps:</h3>\n'
    print_steps_html(step, out=out)
    print >> out, '</section>\n'

    #   config variables
    print >> out, '<section id="cvars">\n'
    print >> out, '<h3>Config Variables</h3>\n'
    print >> out, '<ul>\n'
    for var in sorted(ConfDict.keys()):
        print >> out, '<li class="cvar" id="{0}">\n'.format(var)
        print >> out, '<var class="configvar"><b>{0}</b></var>\n'.format(var)

        svars = Steps_Per_Var[var]
        if len(svars) > 0:
            print >> out, '<details>\n<summary>Found in {0} steps:</summary>\n<ul>\n'.format(
                len(svars))
            for s in svars:
                print >> out, '<li><a href="#{0}">{0}</a></li>\n'.format(s)
            print >> out, '</ul>\n</details>\n'
        else:
            print >> out, '<p>Not found in any steps.</p>'

        print >> out, '</li>\n'

    print >> out, '</ul>\n'
    print >> out, '</section>\n'

    print >> out, HTML_bot

#
# Main
#


def main():

    global Steps_Per_Var, ConfDict, VarRegExps

    cmdline = process_command_line()
    rootdir = cmdline.expdir
    outfile = cmdline.output

    if outfile == '<stdout>':
        out = sys.stdout
    else:
        out = open(outfile, 'w')

    # Construct a tree of the steps for a given exp dir
    rootstep = Step(rootdir)

    # Get a dictionary of all of the output config variables based on
    # the last-executed step. This should be a super-set of all config
    # vars.
    print >> sys.stderr, "Retrieving list of config variables..."
    ConfDict = read_config_vars(rootstep.get_output_config_file())

    # Make a dict containing all of the config vars as compiled
    # regexps
    for var in ConfDict:
        if var not in VarRegExps:
            VarRegExps[var] = re.compile(Step.var_pat.format(var), flags=re.M)

    # Construct indexes of variables and steps
    print >> sys.stderr, "Cross-referencing all config variables..."
    Steps_Per_Var = make_index(rootstep)

    print >> sys.stderr, "Writing HTML output..."
    output_html(rootstep, out=out)

    return 0        # success


if __name__ == '__main__':
    status = main()
    sys.exit(status)
