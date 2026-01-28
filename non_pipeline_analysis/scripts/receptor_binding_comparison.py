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
DMS_XBB_CSV = "data/XBB.1.5_summary.csv"
MIN_CELL_ENTRY = -2.5
OUTPUT_FILE = 'figures/coronavirus_comparison_interactive.html'

# Color scheme
VIOLIN_COLOR = '#b0c4b1'
JITTER_COLOR = '#445716'

def load_dms_data(csv_path, cell_entry_col="spike mediated entry", 
                  receptor_col="receptor binding"):
    return (
        pd.read_csv(csv_path)
        .rename(columns={cell_entry_col: "cell entry", receptor_col: "receptor binding"})
        .dropna(subset=["cell entry", "receptor binding"])
        .query("`cell entry` >= @MIN_CELL_ENTRY")
        .query("mutant not in ['*', '-']")
        .assign(
            mutation=lambda x: x["wildtype"] + x["site"].astype(str) + x["mutant"],
            n_mutations_at_site=lambda x: x.groupby("site")["mutant"].transform("count"),
        )
        .reset_index(drop=True)
    )

def assign_region_229e(seq_site):
    """Assign spike region for 229E"""
    if 38 <= seq_site <= 267:
        return "NTD"
    elif 293 <= seq_site <= 435:
        return "RBD"
    elif 575 < seq_site <= 1173:
        return "S2"
    else:
        return "other"

def assign_region_sars(seq_site):
    """Assign spike region for SARS-CoV-2"""
    if 13 <= seq_site <= 301:
        return "NTD"
    elif 327 <= seq_site <= 523:
        return "RBD"
    elif 681 < seq_site <= 1300:
        return "S2"
    else:
        return "other"

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

def process_dms_data(df, virus_name, dist_df, region_func, distance_cutoff=15):
    df = df.copy()
    df = df[df["site"].astype(str).str.match(r"^\d+$")]
    df["site"] = df["site"].astype(int)
    
    df = df.merge(dist_df, on='site', how="left")
    df = df.fillna({'distance': 100})
    
    df['region'] = df['site'].apply(region_func)
    df['receptor_distance'] = np.where(
        df['region'] == 'RBD',
        np.where(df['distance'] <= distance_cutoff, 'receptor_proximal', 'receptor_distal'),
        'non_rbd'
    )
    df['virus'] = virus_name
    
    return df

def create_interactive_violin_plot(df, viruses_to_plot, output_file):
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
            x=alt.X('receptor_distance:N'),
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
    dms_229e = load_dms_data(DMS_229E_CSV, "spike mediated entry", "all sera escape")
    dms_229e = dms_229e.rename(columns={"all sera escape": "sera escape"})
    dms_sars = load_dms_data(DMS_SARS_CSV, "spike mediated entry", "ACE2 binding")
    dms_xbb = load_dms_data(DMS_XBB_CSV, "spike mediated entry", "ACE2 binding")
    
    dist_df_229e = get_distance_df("8WDE", "A", "D", "APN")
    dist_df_sars = get_distance_df("6M0J", "E", "A", "ACE2")

    dms_229e_processed = process_dms_data(dms_229e, "229E_APN", dist_df_229e, assign_region_229e)
    dms_sars_processed = process_dms_data(dms_sars, "KP.3.1.1_ACE2", dist_df_sars, assign_region_sars)
    dms_xbb_processed = process_dms_data(dms_xbb, "XBB.1.5_ACE2", dist_df_sars, assign_region_sars)
    
    df = pd.concat([
        dms_229e_processed,
        dms_sars_processed,
        dms_xbb_processed,
    ], ignore_index=True)
    
    df_no_s2 = df[df['region'] != 'S2'].copy()
    
    print("Creating interactive visualization...")
    

    viruses_to_plot = [
        '229E_APN', 
        'KP.3.1.1_ACE2', 
        'XBB.1.5_ACE2'
    ]
    

    fig = create_interactive_violin_plot(df_no_s2, viruses_to_plot, OUTPUT_FILE)
    
    print("Done!")
    
    return df_no_s2, fig

if __name__ == "__main__":
    df, fig = main()