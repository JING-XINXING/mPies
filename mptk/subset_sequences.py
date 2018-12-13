#!/usr/bin/env python

"""
Create sequence subset of identified sequences.

This module uses the result files of protein pilot and the generated database from the first step of mPies to create
a subset protein fasta file with only identified protein sequences.
"""

import logging
import pandas as pd

logger = logging.getLogger("pies.subset_sequences")


def parse_proteinpilot_file(excel_file):
    """
    Parses the ProteinPilot result Excel file.

    The function parse_proteinpilot_file extracts the columns N, Accession, and Peptides(95%) from the UniProt results
    file.

    Parameters
    ----------
      excel_file: the ProteinPilot result excel file

    Returns
    -------
      df: a data frame with the kept columns

    """
    df = pd.read_excel(excel_file)
    df = df[["N", "Accession", "Peptides(95%)"]]
    df["Accession"] = df["Accession"].str.split("|", expand=False).str[0]

    return df


def subset_sequence_file(df, sequence_file, sequence_file_subset):
    """
    Creates a subset of the sequence file.

    Based on the identified protein accessions, a subset of the protein fasta file is generated.

    Parameters
    ----------
      df: a data frame with the kept columns
      sequence_file: the sequence file generated by mPies part I

    Returns
    -------
      None

    """
    sequence_dict = {}

    fasta_headers = df["Accession"].tolist()
    with open(sequence_file) as sequence_file_open, open(sequence_file_subset, "w") as sequence_file_subset_open:
        for line in sequence_file_open:
            if line.startswith(">"):
                header = line.rstrip()
            else:
                seq = line.rstrip()
                sequence_dict[header] = seq

        for key in sequence_dict:
            id = key[1:].split()[0]
            if id in fasta_headers:
                sequence_file_subset_open.write(key + "\n")
                sequence_file_subset_open.write(sequence_dict[key] + "\n")

    return


# mPies (metaProteomics in environmental sciences) creates annotated databases for metaproteomics analysis.
# Copyright 2018 Johannes Werner (Leibniz-Institute for Baltic Sea Research)
# Copyright 2018 Augustin Geron (University of Mons, University of Stirling)
# Copyright 2018 Sabine Matallana Surget (University of Stirling)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
