# mPies: metaProteomics in environmental sciences

mPies is a tool to create suitable databases for metaproteomic analysis. 

This workflow uses three different databases for a metagenome (i) OTU-table, (ii) assembled-derived, (iii) and
unassembled-derived to build a consensus of these databases and increase the mapping sensitivity.

## Installation

The easiest way is to use bioconda and create a new environment. 

```bash
conda create -n mpies --file conda_env.conf
source activate mpies
```

SingleM has been packaged by AppImage (due to the Python 2 dependency).  Download 
[AppImage](https://github.com/probonopd/AppImageKit/releases) and build the image with

```bash
cd appimages
./appimage_singlem.sh
appimagetool-x86_64.AppImage singlem-x86_64.AppImage/ singlem.AppImage
```

## Usage

The entire workflow is written in Snakemake.

```bash
snakemake --configfile snake.json
```

### Detailed explanation of the mpies workflow

#### Preprocessing

The preprocessing trims the raw reads and combines the single reads into one file.

#### Amplicon-derived proteome file

In order to create the amplicon-derived proteome file, there are two possibilities. If amplicon data is available,
then a text file with the taxon names (one per line) is used for downloading the proteomes from UniProt. If no
amplicon data is available, you can set the option config["otu_table"]["run_singlem"] to `true` and a taxon file is
created with `singlem` (singlem finds OTUs based on metagenome shotgun sequencing data).

#### Assembled-derived proteome file

If only raw data is available, it is possible to run an assembly with MEGAHIT or metaSPAdes (set
config["assembled"]["run_assembly"] to `true` and config["assembled"]["assembler"] to "megahit" or "metaspades").
Please keep in mind that assemblies can take a lot of time depending on the size of the dataset. If you already have an
assembly, set config["assembled"]["run_assembly"] to `false` and create a symlink of your assembly into
`{sample}/assembly/contigs.fa`. If you have no gene calling yet, remember to set config["assembled"]["run_genecalling"]
to `true`.

If you have both assembly and gene calling already performed, set config["assembled"]["run_assembly"] and
config["assembled"]["run_genecalling"] to `false` and create a symlink of the assembled proteome into
`{sample}/proteome/assembled.faa`.

#### Unassembled-derived proteome file

To create the unassembled-derived proteome file, `FragGeneScan` is called (and prior to that a fastq-to-fasta
conversion).

#### Postprocessing

During the postprocessing, the all three proteomes are combined into one file. Short sequences (below 30 amino acids)
are deleted and all duplicates are removed. Afterwards, the fasta headers are hashed to shorten the headers (and save
some disk space especially for large proteome files).

#### Taxonomical analysis

The taxonomic analysis is performed with blast2lca from the MEGAN package. Per default, the taxonomic analysis is set
to false in the snake config file.

Some prerequisites are necessary to run the taxonomic analysis for the created proteome fasta file.

1. Download [MEGAN](http://ab.inf.uni-tuebingen.de/data/software/megan6/download/welcome.html). Don't forget to also
to download and unzip the file `prot_acc2tax-June2018X1.abin.zip` from the same page.

2. Download the `nr.gz` fasta file from NCBI (size: 40 GB).

```bash
wget ftp://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz
wget ftp://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz.md5
md5sum -c nr.gz.md5
```

If the checksum does not match, the download was probably not complete. `wget -c` continues a partial download.

3. Create a diamond database of the file `nr.gz`.

```bash
diamond makedb --threads <number_of_threads> --in nr.gz --db nr.dmnd
```

4. Now you can set config["taxonomy"]["run_taxonomy"] to `true` and run `snakemake`. Remember to set the paths for the
diamond database, the binary of blast2lca and the path to the file `prot_acc2tax-Jun2018X1.abin`. Please note that
`diamond blastp` takes a very long time to execute. 

#### Functional analysis

Different databases can be used to add functional annotation. Per default, the funtional annotation is set to `false`.

##### COG

In order to use the COG database, some prerequisites have to be fulfilled before.

1. Download the necessary files from the FTP server.

```bash
wget ftp://ftp.ncbi.nih.gov/pub/COG/COG2014/data/prot2003-2014.fa.gz
wget ftp://ftp.ncbi.nih.gov/pub/COG/COG2014/data/cog2003-2014.csv
wget ftp://ftp.ncbi.nih.gov/pub/COG/COG2014/data/cognames2003-2014.tab
wget ftp://ftp.ncbi.nih.gov/pub/COG/COG2014/data/fun2003-2014.tab
```

2. Create a diamond database of the file `prot2003-2014.fa.gz`.

```bash
diamond makedb --threads <number_of_threads> --in prot2003-2014.fa.gz --db cog.dmnd
```

3. Now you can set config["functions"]["run_cog"]["run_functions_cog"] to `true` and run `snakemake`. Remember to set
the paths for the diamond database and the files `cog_table`, `cog_names`, and `cog_functions`.

## Test data

The test data set is a subset from the Ocean Sampling Day (first 18,000 lines for each read file), Accession number
ERR770958 obtained from https://www.ebi.ac.uk/ena/data/view/ERR770958). The data is deposited in the test_data
directory of this repository.

