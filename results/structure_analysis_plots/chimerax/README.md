# structural analysis of HCoV-229E Spike DMS using chimerax

Input data utilized by the pipeline are located in [results](https://github.com/dms-vep/229E_spike_1984_DMS/tree/main/results) folder of the main DMS pipeline. The pipeline uses the r functional effects, escape by sera and binding affinity of to create [defattr](https://www.cgl.ucsf.edu/chimera/docs/UsersGuide/midas/defattr.html) tables to visulaize the results on the protein structue using chimerax. 

## Organization of this repo

### Code and configuration
The [snakemake](https://snakemake.readthedocs.io/) pipeline uses the configuration from [config.yaml](config.yaml).


### Results and documentation
The results of running the pipeline are placed in [./results/](results), and classified by protein structure.


## Running the pipeline (dry-run)
To do a test run of the pipeline you can execute the following command
    snakemake -n 

## Running the pipeline
To run the pipeline,
    snakemake -j 4
