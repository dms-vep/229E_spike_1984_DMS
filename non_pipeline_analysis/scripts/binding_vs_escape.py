import pandas as pd
import numpy as np
import altair as alt
import math
import tempfile
import urllib.request
import polyclonal.pdb_utils
import scipy.stats as stats

# Configuration
DMS_229E_CSV = "../results/summaries/summary_of_all_sera.csv"
MIN_CELL_ENTRY = -2.5
OUTPUT_FILE = 'figures/receptor_binding_escape_correlation_interactive.html'

# Color scheme
COLOR_MAP = {
    'non_rbd_S1': '#006d77',  
    'non_rbd_S2': '#62b6cb',  
    'receptor_distal': '#744253',  
    'receptor_proximal': '#c6ac8f' 
}

def assign_region_229e(seq_site):
    """Assign spike region for 229E."""
    if 38 <= seq_site <= 267:
        return "NTD"
    elif 293 <= seq_site <= 435:
        return "RBD"
    elif 575 < seq_site <= 1173:
        return "S2"
    elif 17 <= seq_site <= 567:
        return "S1"
    else:
        return "other"

def process_dms_data(df, virus_name, dist_df, region_func):
    df = df.copy()
    df = df[df["site"].astype(str).str.match(r"^\d+$")]
    df["site"] = df["site"].astype(int)
    df = df.merge(dist_df, on='site', how="left")
    df = df.fillna({'distance': 100})
    df['region'] = df['site'].apply(region_func)
    df['receptor_distance'] = np.where(
        df['region'] == 'RBD',
        np.where(df['distance'] <= 15, 'receptor_proximal', 'receptor_distal'),
        'non_rbd'
    )
    df['virus'] = virus_name
    
    return df

def get_distance_df():
    with tempfile.NamedTemporaryFile() as f:
        urllib.request.urlretrieve(
            "https://files.rcsb.org/download/8WDE.pdb",
            f.name,
        )
        coords_df = polyclonal.pdb_utils.extract_atom_locations(
            f.name, ["A", "D"], target_atom="CA"
        )
    
    return (
        coords_df
        .query("chain == 'A'")
        [["site", "x", "y", "z"]]
        .merge(
            (
                coords_df
                .query("chain == 'D'")
                [["site", "x", "y", "z"]]
                .rename(columns={c: f"APN_{c}" for c in ["site", "x", "y", "z"]})
            ),
            how="cross",
        )
        .assign(
            distance=lambda x: x.apply(
                lambda r: math.sqrt(sum((r[c] - r[f"APN_{c}"])**2 
                                       for c in ["x", "y", "z"])),
                axis=1,
            )
        )
        .groupby("site", as_index=False)
        .aggregate({"distance": "min"})
    )

def create_interactive_scatter_plot(site_aggregated, output_file):
    categories = sorted(site_aggregated['receptor_distance'].unique())
    
    # Title mapping
    TITLE_MAP = {
        'non_rbd_S1': 'Non-RBD S1',
        'non_rbd_S2': 'Non-RBD S2',
        'receptor_distal': 'RBD hAPN-distal',
        'receptor_proximal': 'RBD hAPN-proximal'
    }
    
    charts = []
    
    for category in categories:
        subset = site_aggregated[site_aggregated['receptor_distance'] == category].copy()
        color = COLOR_MAP.get(category, '#95a5a6')
        mask = ~(pd.isna(subset['receptor binding']) | pd.isna(subset['sera escape']))
        
        # Create scatter plot
        scatter = alt.Chart(subset).mark_circle(
            size=100,
            opacity=0.6,
            stroke='white',
            strokeWidth=1
        ).encode(
            x=alt.X('receptor binding:Q',
                   title='Receptor Binding',
                   scale=alt.Scale(zero=False)),
            y=alt.Y('sera escape:Q',
                   title='Sum of Sera Escape'),
            color=alt.value(color),
            tooltip=[
                alt.Tooltip('site:Q', title='Site'),
                alt.Tooltip('receptor binding:Q', title='Receptor Binding', format='.3f'),
                alt.Tooltip('sera escape:Q', title='Sera Escape', format='.3f'),
                alt.Tooltip('wildtype:N', title='Wildtype AA'),
                alt.Tooltip('region:N', title='Region')
            ]
        )
        

        if mask.sum() > 2:
            x_clean = subset.loc[mask, 'receptor binding'].values
            y_clean = subset.loc[mask, 'sera escape'].values
            
            r, _ = stats.pearsonr(x_clean, y_clean)
            n = len(x_clean)
            
            stats_text = f"r = {r:.3f}\nn = {n}"
            x_min = subset['receptor binding'].min()
            y_min = subset['sera escape'].min()
            
            annotation = alt.Chart(pd.DataFrame([{
                'x': x_min,
                'y': y_min,
                'text': stats_text
            }])).mark_text(
                align='left',
                baseline='bottom',
                fontSize=13,
                fontWeight='bold',
                dx=5,
                dy=5
            ).encode(
                x=alt.X('x:Q'),
                y=alt.Y('y:Q'),
                text='text:N'
            )
            
            chart = scatter + annotation
        else:
            chart = scatter
        
        title = TITLE_MAP.get(category, category)
        
        chart = chart.properties(
            width=350,
            height=350,
            title=title
        )
        
        charts.append(chart)
    
    final_chart = alt.hconcat(*charts).configure_view(
        strokeWidth=0
    ).configure_axis(
        labelFontSize=14,
        titleFontSize=16,
        titleFontWeight='bold',
        grid=False
    ).configure_title(
        fontSize=16,
        fontWeight='bold',
        anchor='middle'
    ).configure_concat(
        spacing=20
    ).properties(
        title=alt.TitleParams(
            text='Receptor binding vs sera escape correlation',
            fontSize=18,
            fontWeight='bold',
            anchor='middle'
        )
    )
    
    final_chart.save(output_file)
    return final_chart

def main():
    
    dms_229e = (
        pd.read_csv(DMS_229E_CSV)
        .rename(columns={"all sera escape": "sera escape", "spike mediated entry": "cell entry"})
        .dropna(subset=["cell entry", "receptor binding"])
        .query("`cell entry` >= @MIN_CELL_ENTRY")
        .query("mutant not in ['*', '-']")
        .assign(
            mutation=lambda x: x["wildtype"] + x["site"].astype(str) + x["mutant"],
            n_mutations_at_site=lambda x: x.groupby("site")["mutant"].transform("count"),
        )
        .reset_index(drop=True)
    )
    
    dist_df_229e = get_distance_df()
    apn_prox_df = process_dms_data(dms_229e, "229E", dist_df_229e, assign_region_229e)
    apn_prox_df_modified = apn_prox_df.copy()
    apn_prox_df_modified['region'] = apn_prox_df_modified['region'].replace('NTD', 'S1')
    apn_prox_df_modified = apn_prox_df_modified[apn_prox_df_modified['region'] != 'other']
    
    apn_prox_df_modified['receptor_distance'] = apn_prox_df_modified.apply(
        lambda row: f"non_rbd_{row['region']}" if row['receptor_distance'] == 'non_rbd' 
        else row['receptor_distance'], 
        axis=1
    )
    
    
    # Aggregate data
    site_aggregated = apn_prox_df_modified.groupby(['site', 'receptor_distance'], observed=True).agg({
        'sera escape': 'sum',
        'receptor binding': 'mean',
        'wildtype': 'first',
        'region': 'first'
    }).reset_index()

    fig = create_interactive_scatter_plot(site_aggregated, OUTPUT_FILE)
    
    print("Done!")
    
    return site_aggregated, fig

if __name__ == "__main__":
    df, fig = main()