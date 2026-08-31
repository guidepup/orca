# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Holds platform-specific settings."""

import os

# $ORCA_VERSION
version     = "50.2"

# The revision if built from git; otherwise an empty string
revision = "45b0071"

# "--prefix" parameter used when configuring the build.
prefix      = "/home/runner/work/orca/orca/orca"

# The package name (should be "orca").
package     = "orca"

# The location of the data directory (usually "share").
datadir = os.path.join('/home/runner/work/orca/orca/orca','share')

# The directory where we could find liblouis translation tables.
tablesdir = ""
