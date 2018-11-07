#!/usr/bin/env python

"""
Hash protein headers

This module hashes the headers of the proteome file.
"""

import hashlib
import logging

module_logger = logging.getLogger("pies.hashing")


def write_hashed_protein_header_fasta_file(input_file, output_file, tsv_file, hash_type):
    """
    Hash headers of proteome file.

    The function write_hashed_protein_header_fasta_file calculates the hash value for each proteome header and creates
    a fasta file with hashed headers. Additionally, a tsv file with two column is created that maps the hashed header
    to the original headers. The function returns None.

    Parameters
    ----------
      input_file: input proteome file
      output_file: output proteome file with hashed headers
      tsv_file: output tsv file
      hash_type: hash algorithm to use

    Returns
    -------
      None
    """
    logger = logging.getLogger("pies.hashing.write_hashed_protein_header_fasta_file")

    h = hashlib.new(hash_type)
    output_file_open = open(output_file, "w")
    tsv_file_open = open(tsv_file, "w")

    with open(input_file) as f:
        for line in f:
            if line.startswith(">"):
                header_substring = line.rstrip()[1:]
                h.update(header_substring.encode("utf-8")) # .hexdigest()
                hashed_header = h.hexdigest()
                quoted_hashed_header = '\"' + hashed_header + '\"'
                output_file_open.write(">" + hashed_header + "\n")
                tsv_file_open.write(quoted_hashed_header + "\t" + header_substring + "\n")
            else:
                output_file_open.write(line)

    output_file_open.close()
    tsv_file_open.close()

    return

