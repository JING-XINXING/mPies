#!/usr/bin/env python

"""
Parse the OTU table and generate a file of valid NCBI taxon names.

This module parses the OTU table produced by SingleM to select the abundant genera (or families) present in the
sample (based on a cutoff value, default is 5). The names are validated if they are valid and unique NCBI names and
written into a file.
"""

import logging
import numpy as np
import pandas as pd
import re

logger = logging.getLogger("pies.parse_singlem")


def read_table(input_file):
    """
    Read the OTU table and return a pandas data frame.

    The function `read_table` reads the OTU table produced by SingleM. Unnecessary columns are removed and the
    taxonomy column is separated. The function returns the resulting data frame.

    Parameters
    ----------
      input_file: OTU table

    Returns
    -------
      df: OTU table as pandas data frame object

    """
    df = pd.read_table(input_file)
    df = df[["sample", "num_hits", "taxonomy"]]
    df = pd.concat([df[["sample", "num_hits"]],
                   df["taxonomy"].str.split('; ', expand=True).add_prefix("taxonomy_").fillna(np.nan)], axis=1)
    df = df.drop("taxonomy_0", axis=1)
    df = df.rename(columns={"taxonomy_1": "superkingdom",
                            "taxonomy_2": "phylum",
                            "taxonomy_3": "class",
                            "taxonomy_4": "order",
                            "taxonomy_5": "family",
                            "taxonomy_6": "genus"})

    return df


def calculate_abundant_otus(df, level="genus", cutoff=5):
    """
    Calculate the abundant OTUs of the data frame for a specific taxonomic level.

    The function `calculate_abundant_otus` uses the taxonomic level (default: genus) and returns the taxonomic groups,
    that occur with larger or equal abundance to the chosen cutoff value (default: 5). The function returns a list of
    unvalidated taxon names.

    Parameters
    ----------
      df: OTU table (as data frame)
      level: taxonomic rank (default: genus)
      cutoff: cutoff value to report taxonomic group (default: 5)

    Returns
    -------
      taxon_names: list of unvalidated taxon names

    """
    df_subset = df.groupby([level])["num_hits"].sum().reset_index()
    df_subset = df_subset[df_subset["num_hits"] >= cutoff][level]
    taxon_names = list(df_subset)

    return taxon_names


def validate_taxon_names(taxon_names, ncbi_tax_dict):
    """
    Validate taxon names if they are valid NCBI taxon names.

    The function `validate_taxon_names` uses the list taxon names as input and validates them against the list of
    allowed NCBI taxon names. The function returns a list of validated NCBI taxon names (that is smaller or equal than
    the input list.

    Parameters
    ----------
      taxon_names: list of unvalidated taxon names
      ncbi_tax_dict: taxonomy dictionary generated by general_functions.create_tax_dict()

    Returns
    -------
      validated_taxon_names: list of validated taxon names

    """
    present_taxon_names = []
    for item in taxon_names:
        rx_match = re.search(r"^g__(.+)", item)
        present_taxon_names.append(rx_match.group(1).split("_")[0])

    validated_taxon_names = list(set(present_taxon_names).intersection(ncbi_tax_dict.values()))

    return validated_taxon_names


def write_taxon_list(validated_taxon_names, taxon_file):
    """
    Write the validated taxon names list to a file.

    Parameters
    ----------
      validated_taxon_names: list of validated taxon names

    Returns
    -------
      None

    """
    with open(taxon_file, 'w') as f:
        for item in validated_taxon_names:
            f.write("%s\n" % item)

    return

