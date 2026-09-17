import pandas as pd
import numpy as np
import altair as alt
import math
import tempfile
import urllib.request
import polyclonal.pdb_utils

# Configuration
DMS_229E_CSV = "../results/summaries/cell_entry_and_binding.csv"
DMS_SARS_CSV = "data/KP.3.1.1_summary.csv"
DMS_XBB_CSV = "data/XBB.1.5_RBD_summary.csv"
OUTPUT_FILE = 'figures/coronavirus_comparison_interactive.html'

# Per-dataset cell entry filters (region == 'RBD' is applied separately, using
# the region column already present in each source file)
cell_entry_filters = {
    '229E_APN': {
        'column': 'cell entry',
        'min_value': -2.5
    },
    'KP.3.1.1_ACE2': {
        'column': 'cell entry',
        'min_value': -2.0
    },
    'XBB.1.5_ACE2': {
        'column': 'cell entry',
        'min_value': -1.5
    }
}

# Color scheme
VIOLIN_COLOR = '#b0c4b1'
JITTER_COLOR = '#445716'


def load_dms_data(csv_path, virus_name, min_cell_entry,
                   cell_entry_col=None, receptor_col=None):
    """Load one virus's DMS summary, standardize columns, and filter to
    clean, RBD-only, cell-entry-passing mutations.

    cell_entry_col / receptor_col: pass the source column name if it needs
    renaming to 'cell entry' / 'receptor binding'; leave as None if the file
    already uses those names.
    """
    df = pd.read_csv(csv_path)

    rename_map = {}
    if cell_entry_col is not None:
        rename_map[cell_entry_col] = "cell entry"
    if receptor_col is not None:
        rename_map[receptor_col] = "receptor binding"
    if rename_map:
        df = df.rename(columns=rename_map)

    return (
        df
        .dropna(subset=["cell entry", "receptor binding"])
        .query("mutant not in ['*', '-']")
        .query("`cell entry` >= @min_cell_entry")
        .query("region == 'RBD'")
        .assign(
            mutation=lambda x: x["wildtype"] + x["site"].astype(str) + x["mutant"],
            virus=virus_name,
        )
        .reset_index(drop=True)
    )


def get_distance_df(pdb_id, chain1, chain2, receptor_name):
    with tempfile.NamedTemporaryFile() as f:
        urllib.request.urlretrieve(
            f"https://files.rcsb.org/download/{pdb_id}.pdb",
            f.name,
        )
        coords_df = polyclonal.pdb_utils.extract_atom_locations(
            f.name, [chain1, chain2], target_atom="CA"
        )

    return (
        coords_df
        .query(f"chain == '{chain1}'")
        [["site", "x", "y", "z"]]
        .merge(
            (
                coords_df
                .query(f"chain == '{chain2}'")
                [["site", "x", "y", "z"]]
                .rename(columns={c: f"{receptor_name}_{c}" for c in ["site", "x", "y", "z"]})
            ),
            how="cross",
        )
        .assign(
            distance=lambda x: x.apply(
                lambda r: math.sqrt(sum((r[c] - r[f"{receptor_name}_{c}"])**2
                                       for c in ["x", "y", "z"])),
                axis=1,
            )
        )
        .groupby("site", as_index=False)
        .aggregate({"distance": "min"})
    )


def process_dms_data(df, dist_df, distance_cutoff=15):
    """Merge in receptor-distance data and classify receptor-proximal vs
    receptor-distal. Assumes df is already filtered to RBD-only rows."""
    df = df.copy()
    df = df[df["site"].astype(str).str.match(r"^\d+$")]
    df["site"] = df["site"].astype(int)

    df = df.merge(dist_df, on='site', how="left")
    df = df.fillna({'distance': 100})

    df['receptor_distance'] = np.where(
        df['distance'] <= distance_cutoff,
        'receptor-proximal',
        'receptor-distal',
    )

    return df


def create_interactive_violin_plot(df, viruses_to_plot, output_file):
    receptor_distance_order = ['receptor-distal', 'receptor-proximal']

    df_plot = df[df['virus'].isin(viruses_to_plot)].copy()
    df_plot['virus'] = pd.Categorical(df_plot['virus'], categories=viruses_to_plot, ordered=True)
    df_plot = df_plot.sort_values('virus')

    np.random.seed(42)  # for reproducibility
    df_plot['jitter'] = df_plot.groupby(['virus', 'receptor_distance'], observed=True).cumcount().apply(
        lambda x: np.random.normal(0, 0.08)
    )
    sample_sizes = (
        df_plot.groupby(['virus', 'receptor_distance'], observed=True)
        .size()
        .reset_index(name='n')
    )
    sample_sizes['label'] = 'n=' + sample_sizes['n'].astype(str)

    y_max_per_virus = df_plot.groupby('virus', observed=True)['receptor binding'].max().reset_index()
    y_max_per_virus.columns = ['virus', 'y_max']
    sample_sizes = sample_sizes.merge(y_max_per_virus, on='virus')
    sample_sizes['y_position'] = sample_sizes['y_max'] * 1.05

    colors = {
        'box': VIOLIN_COLOR,
        'jitter': JITTER_COLOR
    }

    charts = []

    for virus in viruses_to_plot:
        virus_data = df_plot[df_plot['virus'] == virus].copy()
        virus_sample_sizes = sample_sizes[sample_sizes['virus'] == virus].copy()

        boxplot = alt.Chart(virus_data).mark_boxplot(
            size=50,
            color=colors['box'],
            opacity=0.7
        ).encode(
            x=alt.X('receptor_distance:N',
                   title='Receptor Distance',
                   sort=receptor_distance_order,
                   axis=alt.Axis(labelAngle=0)),
            y=alt.Y('receptor binding:Q',
                   title='Receptor Binding')
        )

        jitter = alt.Chart(virus_data).mark_circle(
            size=15,
            opacity=0.3,
            color=colors['jitter']
        ).encode(
            x=alt.X('receptor_distance:N',
                   sort=receptor_distance_order,
                   axis=alt.Axis(labelAngle=0)),
            y=alt.Y('receptor binding:Q'),
            xOffset='jitter:Q',
            tooltip=[
                alt.Tooltip('mutation:N', title='Mutation'),
                alt.Tooltip('site:Q', title='Site'),
                alt.Tooltip('receptor binding:Q', title='Receptor Binding', format='.3f'),
                alt.Tooltip('cell entry:Q', title='Cell Entry', format='.3f'),
                alt.Tooltip('receptor_distance:N', title='Category')
            ]
        )

        annotations = alt.Chart(virus_sample_sizes).mark_text(
            align='center',
            baseline='bottom',
            fontSize=11,
            fontWeight='bold',
            dy=-5
        ).encode(
            x=alt.X('receptor_distance:N', sort=receptor_distance_order),
            y=alt.Y('y_position:Q'),
            text='label:N'
        )

        chart = (boxplot + jitter + annotations).properties(
            width=350,
            height=400,
            title=virus
        )

        charts.append(chart)

    final_chart = alt.hconcat(*charts).configure_view(
        strokeWidth=0
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=13
    ).configure_title(
        fontSize=14,
        anchor='middle'
    ).configure_concat(
        spacing=20
    ).properties(
        title=alt.TitleParams(
            text='HCoV-229E and SARS-CoV-2 receptor binding comparison',
            fontSize=16,
            anchor='middle'
        )
    )

    # Save to HTML
    final_chart.save(output_file)
    return final_chart


def main():
    dms_229e = load_dms_data(
        DMS_229E_CSV, "229E_APN",
        min_cell_entry=cell_entry_filters['229E_APN']['min_value'],
        # cell_entry_col=None, receptor_col=None,  # set these if 229E's file needs renaming
    )

    dms_sars = load_dms_data(
        DMS_SARS_CSV, "KP.3.1.1_ACE2",
        min_cell_entry=cell_entry_filters['KP.3.1.1_ACE2']['min_value'],
        cell_entry_col="spike mediated entry", receptor_col="ACE2 binding",
    )

    dms_xbb = load_dms_data(
        DMS_XBB_CSV, "XBB.1.5_ACE2",
        min_cell_entry=cell_entry_filters['XBB.1.5_ACE2']['min_value'],
        cell_entry_col="spike mediated entry", receptor_col="ACE2 binding",
    )
    dms_xbb["receptor binding"] = dms_xbb["receptor binding"].clip(lower=-4)

    dist_df_229e = get_distance_df("8WDE", "A", "D", "APN")
    dist_df_sars = get_distance_df("6M0J", "E", "A", "ACE2")

    dms_229e_processed = process_dms_data(dms_229e, dist_df_229e)
    dms_sars_processed = process_dms_data(dms_sars, dist_df_sars)
    dms_xbb_processed = process_dms_data(dms_xbb, dist_df_sars)

    df_rbd = pd.concat([
        dms_229e_processed,
        dms_sars_processed,
        dms_xbb_processed,
    ], ignore_index=True)

    print("Mutations per virus after filtering:")
    print(df_rbd['virus'].value_counts())

    print("Creating interactive visualization...")

    viruses_to_plot = [
        '229E_APN',
        'KP.3.1.1_ACE2',
        'XBB.1.5_ACE2'
    ]

    fig = create_interactive_violin_plot(df_rbd, viruses_to_plot, OUTPUT_FILE)

    print("Done!")

    return df_rbd, fig


if __name__ == "__main__":
    df, fig = main()