"""Custom rules used in the ``snakemake`` pipeline.

This file is included by the pipeline ``Snakefile``.

"""

# Configure dms-viz JSONs ---------------------------------------------------------------

# read configuration for `configure_dms_viz`
with open("data/dms_viz_config.yaml") as f:
    dms_viz_config = yaml.YAML(typ="safe", pure=True).load(f)

rule configure_dms_viz:
    """Configure a JSON for `dms-viz`."""
    input:
        data_csv=lambda wc: dms_viz_config[wc.viz_name]["data_csv"],
        sitemap_csv=lambda wc: dms_viz_config[wc.viz_name]["sitemap_csv"],
        nb="notebooks/configure_dms_viz.ipynb",
    output:
        dms_viz_json="results/dms-viz/{viz_name}/{viz_name}.json",
        pdb_file="results/dms-viz/{viz_name}/{viz_name}.pdb",
        input_data_csv="results/dms-viz/{viz_name}/{viz_name}_data.csv",
        input_sitemap_csv="results/dms-viz/{viz_name}/{viz_name}_sitemap.csv",
        nb="results/notebooks/configure_dms_viz_{viz_name}.ipynb",
    params:
        params_yaml=lambda wc: yaml_str(
            {
                key: dms_viz_config[wc.viz_name][key]
                for key in [
                    "pdb_id",
                    "pdb_type",
                    "name",
                    "melt_condition_metric_cols",
                    "metric",
                    "opt_params",
                ]
            }
        ),
    conda:
        "envs/dms-viz.yml"
    log:
        "results/logs/configure_dms_viz_{viz_name}.txt",
    shell:
        """
        papermill {input.nb} {output.nb} \
            -p data_csv {input.data_csv} \
            -p sitemap_csv {input.sitemap_csv} \
            -p dms_viz_json {output.dms_viz_json} \
            -p pdb_file {output.pdb_file} \
            -p input_data_csv {output.input_data_csv} \
            -p input_sitemap_csv {output.input_sitemap_csv} \
            -y "{params.params_yaml}" \
            &> {log}
        """

docs["dms-viz visualizations"] = {
    "dms-viz JSON files": {
        viz_name: rules.configure_dms_viz.output.dms_viz_json.format(viz_name=viz_name)
        for viz_name in dms_viz_config
    },
    "Notebooks prepping dms-viz JSONs": {
        viz_name: rules.configure_dms_viz.output.nb.format(viz_name=viz_name)
        for viz_name in dms_viz_config
    },
}


rule binding_vs_escape:
    """Compare binding and escape at key sites."""
    input:
        dms_csv="results/summaries/summary_of_all_sera.csv",
        nb="notebooks/binding_vs_escape.ipynb",
    output:
        nb="results/notebooks/binding_vs_escape.ipynb",
        RBD_up_down_chart_html = "results/binding_vs_escape/RBD_up_down_chart_html.html",
        logoplot_subdir=directory("results/binding_vs_escape/logoplots"),
        RBD_up_down_subdir=directory("results/RBD_up_down"),
        RBD_up_down_csv = "results/RBD_up_down/RBD_up_down_sites.csv",
    params:
        yaml=lambda _, input, output: yaml_str(
            {
                "dms_csv": input.dms_csv,
                "logoplot_subdir": output.logoplot_subdir,
                "RBD_up_down_subdir": output.RBD_up_down_subdir,
                "min_cell_entry": -2.5,
                "min_mutations_at_site": 5,
                "RBD_up_down_chart_html": output.RBD_up_down_chart_html,
                "RBD_up_down_csv": output.RBD_up_down_csv,
            }
        ),
    log:
        log="results/logs/binding_vs_escape.txt",
    conda:
        os.path.join(config["pipeline_path"], "environment.yml")
    shell:
        "papermill {input.nb} {output.nb} -y '{params.yaml}' &> {log}"


docs["binding vs escape effect"] = {
    "Sites that affect RBD up/down conformation": rules.binding_vs_escape.output.RBD_up_down_chart_html,
    "Notebook comparing binding vs escape at key sites": rules.binding_vs_escape.output.nb,
}

docs["Row-wrapped heatmaps"] = {
    "Cell entry": "non_pipeline_analysis/figures/cell_entry_heatmap_full_spike.html",
    "Receptor binding": "non_pipeline_analysis/figures/receptor_binding_heatmap_full_spike.html",
}

docs["other paper figures"] = {
    "Binding loops cell entry": "non_pipeline_analysis/figures/cell_entry_heatmap_all_loops.html",
    "comparison of receptor binding": "non_pipeline_analysis/figures/coronavirus_comparison_interactive.html",
    "receptor binding and escape correlation": "non_pipeline_analysis/figures/receptor_binding_escape_correlation_interactive.html",
    "Natural diversity": "non_pipeline_analysis/figures/site_diversity_plot_interactive.html",
}
