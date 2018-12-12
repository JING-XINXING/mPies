configfile: "database_creation.json"

inputs = []

include:
    "rules/preprocessing.smk"
inputs.append("checkpoints/preprocessing.done")

include:
    "rules/otu_table.smk"
inputs.append("checkpoints/amplicon_proteome.done")

include:
    "rules/assembled.smk"
inputs.append("checkpoints/assembled_proteome.done")

include:
    "rules/unassembled.smk"
inputs.append("checkpoints/unassembled_proteome.done")

include:
    "rules/postprocessing.smk"
inputs.append("checkpoints/postprocessing.done")

rule ALL:
    input:
        inputs
    output:
        touch('checkpoints/mpies.done')