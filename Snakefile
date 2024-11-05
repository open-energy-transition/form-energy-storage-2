# SPDX-FileCopyrightText: : 2017-2024 The PyPSA-Eur Authors
#
# SPDX-License-Identifier: MIT

from shutil import unpack_archive

from snakemake.utils import min_version

include: "workflow/pypsa-eur/rules/common.smk"

import sys

sys.path.append("workflow/pypsa-eur/scripts")

from _helpers import path_provider, get_scenarios, get_rdir

min_version("8.5")


configfile: "workflow/pypsa-eur/config/config.default.yaml"
configfile: "config/config.default.yaml"

run = config["run"]
scenarios = get_scenarios(run)  # global variable
RDIR = get_rdir(run)
policy = run["shared_resources"]["policy"]
exclude = run["shared_resources"]["exclude"]
logs = path_provider("logs/", RDIR, policy, exclude)
benchmarks = path_provider("benchmarks/", RDIR, policy, exclude)
resources = path_provider("resources/", RDIR, policy, exclude)

RESULTS = "results/" + RDIR


wildcard_constraints:
    simpl="[a-zA-Z0-9]*",
    clusters="[0-9]+(m|c)?|all",
    ll=r"(v|c)([0-9\.]+|opt)",
    opts=r"[-+a-zA-Z0-9\.]*",
    sector_opts=r"[-+a-zA-Z0-9\.\s]*",


module pypsaeur:
    snakefile:
        "workflow/pypsa-eur/Snakefile"
    config:
        config


use rule * from pypsaeur

from pathlib import Path

data_dir = Path("workflow/pypsa-eur/data")


rule get_data:
    output:
        [
            str(Path("data") / p.relative_to(data_dir))
            for p in data_dir.rglob("*")
            if p.is_file()
        ],
    shell:
        """
        mkdir -p data
        cp -nR {data_dir}/. data/
        """

rule clean:
    message:
        "Remove all build results but keep downloaded data."
    run:
        import shutil

        shutil.rmtree("resources")
        shutil.rmtree("results")
        print("Data downloaded to data/ has not been cleaned.")

rule plot_line_loading_myopic:
    params:
        plotting=config_provider("plotting"),
    input:
        network=RESULTS
        + "postnetworks/base_s_{clusters}_l{ll}_{opts}_{sector_opts}_{planning_horizons}.nc",
    output:
        map=RESULTS
            + "maps/base_s_{clusters}_l{ll}_{opts}_{sector_opts}-line_loading_{planning_horizons}.pdf"
    benchmark:
        (
            RESULTS
            + "benchmarks/plot_line_loading/base_s_{clusters}_l{ll}_{opts}_{sector_opts}_{planning_horizons}"
        )
    conda:
        "../envs/environment.yaml"
    script:
        "../scripts/plot_line_loading.py"
    

# example how to use rule from pypsa-eur
# use rule solve_sector_network_myopic from pypsaeur with:
#     params:
#         **{
#             k: v
#             for k, v in rules.solve_sector_network_myopic.params.items()
#             if k != "custom_extra_functionality"
#         },
#         custom_extra_functionality=os.path.join(
#             os.path.dirname(workflow.snakefile), "scripts/additional_functionality.py"
#         ),
#     input:
#         **{
#             k: v
#             for k, v in rules.solve_sector_network_myopic.input.items()
#             if k != "network"
#         },
#         network=RESULTS
#         + "prenetworks-final/elec_s{simpl}_{clusters}_l{ll}_{opts}_{sector_opts}_{planning_horizons}.nc",
#         co2_totals_name=resources("co2_totals.csv"),
