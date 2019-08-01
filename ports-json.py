#!/usr/bin/env python3

# Copyright (c) 2019 Juan Francisco Cantero Hurtado <iam@juanfra.info>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import argparse
import sqlite3
import json
from datetime import datetime

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("database", help="sqlports database file")
group_parser = arg_parser.add_mutually_exclusive_group()
group_parser.add_argument(
    "-l",
    "--list",
    help="list columns, useful to detect new entries in the DB",
    action="store_true",
)
group_parser.add_argument(
    "-o", "--output", help="json file where the results will be written"
)
args = arg_parser.parse_args()

connection = sqlite3.connect(args.database)
cursor = connection.cursor()

table = cursor.execute("SELECT * FROM Ports")
column_names = [n[0] for n in table.description]
discarded_columns = [
    "PathId",
    "AUTOCONF_VERSION",
    "AUTOMAKE_VERSION",
    "COMES_WITH",
    "COMPILER",
    "COMPILER_LANGS",
    "COMPILER_LINKS",
    "CONFIGURE_ARGS",
    "CONFIGURE_STYLE",
    "DESCR",
    "DISTFILES",
    "DIST_SUBDIR",
    "DPB_PROPERTIES",
    "EPOCH",
    "FIX_EXTRACT_PERMISSIONS",
    "FLAVORS",
    "GH_ACCOUNT",
    "GH_COMMIT",
    "GH_PROJECT",
    "GH_TAGNAME",
    "IGNORE",
    "IS_INTERACTIVE",
    "MAKEFILE_LIST",
    "MASTER_SITES",
    "MASTER_SITES0",
    "MASTER_SITES1",
    "MASTER_SITES2",
    "MASTER_SITES3",
    "MASTER_SITES4",
    "MASTER_SITES5",
    "MASTER_SITES6",
    "MASTER_SITES7",
    "MASTER_SITES8",
    "MASTER_SITES9",
    "PATCHFILES",
    "PERMIT_DISTFILES",
    "PERMIT_DISTFILES_FTP",
    "PERMIT_PACKAGE_CDROM",
    "PERMIT_PACKAGE_FTP",
    "PKGPATHS",
    "PKGSPEC",
    "PKGSTEM",
    "PKG_ARCH",
    "PORTROACH",
    "PORTROACH_COMMENT",
    "PREFIX",
    "PSEUDO_FLAVOR",
    "PSEUDO_FLAVORS",
    "README",
    "README_CONTENTS",
    "REVISION",
    "SEPARATE_BUILD",
    "STATIC_PLIST",
    "SUBPACKAGE",
    "SUBST_VARS",
    "SUPDISTFILES",
    "TARGETS",
    "TEST_IS_INTERACTIVE",
    "UPDATE_PLIST_ARGS",
    "USE_GMAKE",
    "USE_GROFF",
    "USE_LIBTOOL",
    "USE_LLD",
]
selected_columns = [
    "FullPkgPath",
    "BUILD_DEPENDS",
    "CATEGORIES",
    "COMMENT",
    "DESCR_CONTENTS",
    "DISTNAME",
    "FULLPKGNAME",
    "HOMEPAGE",
    "LIB_DEPENDS",
    "MAINTAINER",
    "MODULES",
    "NOT_FOR_ARCHS",
    "NO_BUILD",
    "NO_TEST",
    "ONLY_FOR_ARCHS",
    "PERMIT_PACKAGE",
    "PKGNAME",
    "RUN_DEPENDS",
    "SHARED_LIBS",
    "TEST_DEPENDS",
    "USE_WXNEEDED",
    "WANTLIB",
]

if args.list:
    box_crux = "+"
    box_horizontal = "-"
    box_vertical = "|"

    columns_size = 0
    for name in column_names:
        if columns_size < len(name):
            columns_size = len(name)

    box_middle = (
        box_crux
        + (box_horizontal * (columns_size + 2))
        + box_crux
        + (box_horizontal * (9 + 2))
        + box_crux
    )

    print(box_middle)
    for name in column_names:
        if name in selected_columns:
            status = "SELECTED"
        elif name in discarded_columns:
            status = "DISCARDED"
        else:
            status = "\033[07m" + "UNKNOWN" + "\033[0m"
        print(
            box_vertical.ljust(2)
            + name.ljust(columns_size)
            + box_vertical.center(3)
            + status.ljust(9)
            + box_vertical.rjust(2)
        )
        print(box_middle)

elif args.output:
    cursor.execute("SELECT FullPkgPath, Arch, Value from Broken")
    results_broken = cursor.fetchall()
    dict_broken = {}
    for row in results_broken:
        if row[0] in dict_broken:
            dict_broken[row[0]].update({row[1]: row[2]})
        else:
            dict_broken[row[0]] = {row[1]: row[2]}

    cursor.execute("SELECT " + ",".join(selected_columns) + " from Ports")
    results_ports = cursor.fetchall()
    list_ports = []
    for row in results_ports:
        tmpdict = {}
        for col_index, col_name in enumerate(selected_columns):
            tmpdict[col_name] = row[col_index]
            if col_name == "FullPkgPath" and row[col_index] in dict_broken:
                tmpdict["BROKEN"] = dict_broken[row[col_index]]
        list_ports.append(tmpdict)

    dict_info = {}
    dict_info["BUILD_DATE"] = datetime.utcnow().strftime("%Y%m%d%H%M")
    list_final = [dict_info, list_ports]
    with open(args.output, "w") as filedump:
        json.dump(list_final, filedump, ensure_ascii=False)

else:
    arg_parser.print_help()
