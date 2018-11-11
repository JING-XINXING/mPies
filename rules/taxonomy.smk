rule run_diamond:
    input:
        expand("{sample}/proteome/combined.mincutoff.nodup.hashed.faa", sample=config["sample"])
    output:
        temp(expand("{sample}/taxonomy/combined.tax.daa", sample=config["sample"]))
    params:
        mode=config["taxonomy"]["run_diamond"]["mode"],
        output_format=config["taxonomy"]["run_diamond"]["output_format"],
        diamond_database=config["taxonomy"]["run_diamond"]["diamond_database"],
        maxtargetseqs=config["taxonomy"]["run_diamond"]["max_target_seqs"],
        score=config["taxonomy"]["run_diamond"]["score"],
        compress=config["taxonomy"]["run_diamond"]["compress"],
        sensitive=config["taxonomy"]["run_diamond"]["sensitive"]
    log:
        expand("{sample}/log/diamond.log", sample=config["sample"])
    threads:
        config["ressources"]["threads"]
    shell:
        """
        diamond {params.mode} -f {params.output_format} -p {threads} -d {params.diamond_database} \
          -k {params.maxtargetseqs} -e {params.score} --compress {params.compress} {params.sensitive} \
          -q {input} -o {output} > {log} 2>&1
        """

rule run_blast2lca:
    input:
        expand("{sample}/taxonomy/combined.tax.daa", sample=config["sample"])
    output:
        temp(expand("{sample}/taxonomy/combined.megan.txt", sample=config["sample"]))
    params:
        blast2lca_bin=config["taxonomy"]["run_blast2lca"]["binary"],
        input_format=config["taxonomy"]["run_blast2lca"]["input_format"],
        blast_mode=config["taxonomy"]["run_blast2lca"]["blast_mode"],
        acc2tax_file=config["taxonomy"]["run_blast2lca"]["acc2tax_file"]
    log:
        expand("{sample}/log/blast2lca.log", sample=config["sample"])
    shell:
        """
        {params.blast2lca_bin} -i {input} -f {params.input_format} -m {params.blast_mode} -o {output} \
          -a2t {params.acc2tax_file} > {log} 2>&1
        """

rule parse_taxonomy:
    input:
        expand("{sample}/taxonomy/combined.megan.txt", sample=config["sample"])
    output:
        expand("{sample}/taxonomy/combined.tax.txt", sample=config["sample"])
    params:
        mode=config["taxonomy"]["parse_taxonomy"]["mode"],
    shell:
        "./main.py -v {params.mode} -m {input} -t {output}"

rule get_taxonomy_done:
    input:
        expand("{sample}/taxonomy/combined.tax.txt", sample=config["sample"])
    output:
        touch("checkpoints/taxonomy.done")

