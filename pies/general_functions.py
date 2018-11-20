#!/usr/bin/env python

"""
Provide general functions necessary for multiple modules

This module includes the functions `get_desired_ranks`, `get_names_dmp`, and `create_tax_dict` to download and access
the NCBI taxonomy.
"""

import logging
import os
import re
import tarfile
import urllib.parse
import urllib.request
from ete3 import NCBITaxa

module_logger = logging.getLogger("pies.general_functions")
NCBI = NCBITaxa()


def get_desired_ranks(taxid):
    """
    Get taxonomic lineage on taxid for desired ranks.

    The function get_desired_ranks uses a taxid as input and returns a dict of ranks (superkingdom,
    phylum, class, order, family, genus, species) as keys and corresponding taxIDs as values.

    Parameters
    ----------
      taxid: TaxID (-1 represents unclassified)

    Returns
    -------
      ranks2lineage: dict with ranks as keys and taxIDs as values

    """
    logger = logging.getLogger("pies.general_functions.get_desired_ranks")

    if taxid == -1:
        return {"superkingdom": -1, "phylum": -1, "class": -1, "order": -1, "family": -1,
                "genus": -1}
    lineage = NCBI.get_lineage(taxid)
    lineage2ranks = NCBI.get_rank(lineage)
    ranks2lineage = dict((rank, taxid) for (taxid, rank) in lineage2ranks.items())
    for taxrank in ["superkingdom", "phylum", "class", "order", "family", "genus"]:
        if taxrank not in ranks2lineage:
            ranks2lineage[taxrank] = -1

    return ranks2lineage


def get_names_dmp(names_dmp=None):
    """
    Download names.dmp.

    The function downloades the names.dmp file if not already existing or if the file size is zero.

    Parameter
    ---------
      names_dmp: location of names.dmp (default: None)

    Returns
    -------
      absolute path of file names.dmp

    """
    logger = logging.getLogger("pies.general_functions.get_names_dmp")

    if names_dmp is not None:
        if os.stat(names_dmp).st_size == 0:
            os.remove(names_dmp)
        else:
            return os.path.abspath(names_dmp)
    else:
        names_dmp = "names.dmp"
        if os.path.isfile("names.dmp"):
            if os.stat(names_dmp).st_size != 0:
                return os.path.abspath(names_dmp)

            else:
                os.remove(names_dmp)

    logger.info("Downloading taxdump.tar.gz ...")
    urllib.request.urlretrieve("ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz",
                               filename="taxdump.tar.gz")
    tar = tarfile.open("taxdump.tar.gz")
    tar.extract("names.dmp")
    tar.close()
    os.remove("taxdump.tar.gz")

    return os.path.abspath("names.dmp")


def create_tax_dict(abspath_names_dmp):
    """
    Create a taxonomy dictionary with taxID as keys and tax names as values.

    The function uses names.dmp to create a tax dictionary to map taxIDs onto tax names.

    Below, the first 10 lines of the current version of names.dmp are shown. The first column
    (`curr_line[0]`) represents the taxID, the second column (`curr_line[1]`) the name and the
    fourth column (`curr_line[3]`) if the name is a valid scientific name.

    ```
    $ head names.dmp

    1	|	all	|		|	synonym	|
    1	|	root	|		|	scientific name	|
    2	|	Bacteria	|	Bacteria <prokaryotes>	|	scientific name	|
    2	|	Monera	|	Monera <Bacteria>	|	in-part	|
    2	|	Procaryotae	|	Procaryotae <Bacteria>	|	in-part	|
    2	|	Prokaryota	|	Prokaryota <Bacteria>	|	in-part	|
    2	|	Prokaryotae	|	Prokaryotae <Bacteria>	|	in-part	|
    2	|	bacteria	|	bacteria <blast2>	|	blast name	|
    2	|	eubacteria	|		|	genbank common name	|
    2	|	not Bacteria Haeckel 1894	|		|	authority	|
    ```

    Parameter
    ---------
      abspath_names_dmp: absolute path of of names.dmp

    Returns
    -------
      ncbi_tax_dict: tax dictionary

    """
    logger = logging.getLogger("pies.general_functions.create_tax_dict")

    ncbi_tax_dict = {}
    ncbi_tax_dict[-1] = -1
    logger.info("creating tax dictionary ...")
    with open(abspath_names_dmp) as names_dmp_open:
        for line in names_dmp_open:
            curr_line = re.split(r"\t*\|\t*", line.rstrip())
            if curr_line[3] == "scientific name":
                ncbi_tax_dict[int(curr_line[0])] = curr_line[1]

    return ncbi_tax_dict

