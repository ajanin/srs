# $Id: Makefile 766 2014-01-16 01:02:43Z janin $

# Install SRS scripts and support files under $SWORDFISH_ROOT.
# You should define SWORDFISH_ROOT if you use this Makefile
#
# Note that nfs_sync_cp is used to try to avoid issues of non-atomic
# copies under NFS at ICSI. Comment out the next line to use the
# standard install tool instead.

USE_NFS_SYNC_CP=1

all:	$(PYTHON_BINARIES) $(PYTHON_LIBRARIES) $(SHELL_LIBRARIES) $(PERL_LIBRARIES)
.PHONY:	all install clean

# These don't require compilation, and install to share/bin
PYTHON_BINARIES = \
	srs-arch \
	srs-config \
	srs-go \
	srs-go-parallel \
	srs-go-parallel-litestep \
	srsrs-go \
	srs-info.py \
	srs-time.py

# These don't require compilation, and install to share/lib/python
PYTHON_LIBRARIES = \
	srs.py

# Install Perl modules to share/lib/perl
PERL_LIBRARIES = \
	srs.pm

# This is kinda unusual, but it's a nonexecutable file that can be
# loaded by shell scripts; it should be found in $PATH
SHELL_LIBRARIES = \
	srs_config_litestep

install:	all
ifndef SWORDFISH_ROOT
	$(error SWORDFISH_ROOT is undefined)
endif
ifdef PYTHON_BINARIES
	mkdir -p $(SWORDFISH_ROOT)/share/bin
ifdef USE_NFS_SYNC_CP
	for P in $(PYTHON_BINARIES); do echo $$P; nfs_sync_cp $$P $(SWORDFISH_ROOT)/share/bin; chmod 775 $(SWORDFISH_ROOT)/share/bin/$$P; chgrp `groups | cut -d ' ' -f 1` $(SWORDFISH_ROOT)/share/bin/$$P; done
else
	install -m 775 -t $(SWORDFISH_ROOT)/share/bin $(PYTHON_BINARIES)
endif # USE_NFS_SYNC_CP
endif # PYTHON_BINARIES
ifdef PYTHON_LIBRARIES
	mkdir -p $(SWORDFISH_ROOT)/share/lib/python
ifdef USE_NFS_SYNC_CP
	for P in $(PYTHON_LIBRARIES); do echo $$P; nfs_sync_cp $$P $(SWORDFISH_ROOT)/share/lib/python; chmod 664 $(SWORDFISH_ROOT)/share/lib/python/$$P; chgrp `groups | cut -d ' ' -f 1` $(SWORDFISH_ROOT)/share/lib/python/$$P; done
else
	install -m 664 -t $(SWORDFISH_ROOT)/share/lib/python $(PYTHON_LIBRARIES)
endif # USE_NFS_SYNC_CP
endif # PYTHON_LIBRARIES
ifdef SHELL_LIBRARIES
	mkdir -p $(SWORDFISH_ROOT)/share/bin
ifdef USE_NFS_SYNC_CP
	for P in $(SHELL_LIBRARIES); do echo $$P; nfs_sync_cp $$P $(SWORDFISH_ROOT)/share/bin; chmod 775 $(SWORDFISH_ROOT)/share/bin/$$P; chgrp `groups | cut -d ' ' -f 1` $(SWORDFISH_ROOT)/share/bin/$$P; done
else
	install -m 775 -t $(SWORDFISH_ROOT)/share/bin $(SHELL_LIBRARIES)
endif # USE_NFS_SYNC_CP
endif # SHELL_LIBRARIES
ifdef PERL_LIBRARIES
	mkdir -p $(SWORDFISH_ROOT)/share/lib/perl
ifdef USE_NFS_SYNC_CP
	for P in $(PERL_LIBRARIES); do echo $$P; nfs_sync_cp $$P $(SWORDFISH_ROOT)/share/lib/perl; chmod 664 $(SWORDFISH_ROOT)/share/lib/perl/$$P; chgrp `groups | cut -d ' ' -f 1` $(SWORDFISH_ROOT)/share/lib/perl/$$P; done
else
	install -m 664 -t $(SWORDFISH_ROOT)/share/lib/perl $(PERL_LIBRARIES)
endif # USE_NFS_SYNC_CP
endif # PERL_LIBRARIES

clean:
	@echo "Nothing to clean up"
