import pandas as pd
import altair as alt

DATA_CSV = "../results/summaries/cell_entry_and_binding.csv"
CHART_HTML = "figures/cell_entry_heatmap_all_loops.html"
TITLE = "Effect of mutations to 229E spike protein binding loops on entry in 293T-hAPN-TMPRSS2 cells"
EFFECT_COL = "cell entry"
COLOR_SCHEME = "redblue"
FIXED_MIN = -5
FIXED_MAX = 2
ALPHABET = "RKHDEQNSTYWFAILMVGPC"
W_STEP = 12
H_STEP = 12
LOOPS = {
    'Loop1': {'start': 308, 'end': 325, 'label': 'Loop 1 (308-325)'},
    'Loop2': {'start': 352, 'end': 359, 'label': 'Loop 2 (352-359)'},
    'Loop3': {'start': 404, 'end': 408, 'label': 'Loop 3 (404-408)'}
}
LOOP2_MAPPING = {site: 333 + (site - 352) for site in range(352, 360)}

def prepare_loop_data(csv_data, loop_name, loop_info):
    """Prepare data for a specific loop"""
    # Filter data for this loop
    data = csv_data[
        (csv_data['site'] >= loop_info['start']) & 
        (csv_data['site'] <= loop_info['end'])
    ].copy()
    data['loop'] = loop_name
    data['loop_label'] = loop_info['label']
    

    if loop_name == 'Loop2':

        if 353 not in data['site'].values:
            data = pd.concat([data, pd.DataFrame([{
                "site": 353, "wildtype": "G", 'mutant': 'C', 
                EFFECT_COL: None,  
                'loop': loop_name, 'loop_label': loop_info['label'],
                'is_missing': True 
            }])], ignore_index=True)
        if 354 not in data['site'].values:
            data = pd.concat([data, pd.DataFrame([{
                "site": 354, "wildtype": "G", 'mutant': 'C', 
                EFFECT_COL: None,  
                'loop': loop_name, 'loop_label': loop_info['label'],
                'is_missing': True  
            }])], ignore_index=True)
        data['sequential_site'] = data['site'].apply(lambda x: LOOP2_MAPPING.get(x, x))
    else:
        data['sequential_site'] = data['site']
    

    if 'is_missing' not in data.columns:
        data['is_missing'] = False
    data['is_missing'] = data['is_missing'].fillna(False)
    
    data['site'] = data['site'].astype(str)
    
    return data

def create_loop_heatmap(loop_data, loop_name):
    

    if isinstance(ALPHABET, str):
        alphabet = list(ALPHABET)
    else:
        alphabet = ALPHABET
    
    loop_data = loop_data[
        loop_data["mutant"].isin(alphabet) & 
        loop_data["wildtype"].isin(alphabet)
    ].reset_index(drop=True)
    
    # Base heatmap
    heatmap_base = (
        alt.Chart(loop_data)
        .encode(
            alt.Y("mutant:N", 
                 sort=alphabet, 
                 title="amino acid" if loop_name == 'Loop1' else None,
                 axis=alt.Axis(labels=(loop_name == 'Loop1')))
        )
        .properties(width=alt.Step(W_STEP), height=alt.Step(H_STEP))
    )
    
    # Background gray
    heatmap_bg = heatmap_base.transform_impute(
        impute="_stat_dummy",
        key="mutant",
        keyvals=alphabet,
        groupby=["site"],
        value=None,
    ).mark_rect(color="#E0E0E0", opacity=0.8)
    
    # Wildtype markers
    heatmap_wildtype = (
        heatmap_base
        .transform_filter(alt.datum["wildtype"] == alt.datum["mutant"])
        .transform_filter(alt.datum["is_missing"] == False)  
        .mark_text(text="x", color="black", size=14)
    )
    
    # Mutation effects (only for non-missing data)
    heatmap_muts = (
        heatmap_base
        .transform_filter(alt.datum["is_missing"] == False)  
        .encode(
            alt.Color(
                f'{EFFECT_COL}:Q',
                scale=alt.Scale(
                    scheme=COLOR_SCHEME,
                    domainMid=0,
                    domainMin=FIXED_MIN,
                    domainMax=FIXED_MAX,
                    clamp=True,
                ),
                legend=alt.Legend(title="Cell entry effect") if loop_name == 'Loop1' else None
            ),
            tooltip=[
                "site:N", 
                "mutant:N", 
                "wildtype:N", 
                alt.Tooltip(f'{EFFECT_COL}:Q', format=".2f"),
                "loop_label:N"
            ],
        )
        .mark_rect(stroke="black", opacity=1, strokeOpacity=1, strokeWidth=0.5)
    )
    
    sequential_sites = sorted(loop_data["sequential_site"].unique())
    sequential_to_site = loop_data.set_index("sequential_site")["site"].to_dict()
    to_label_values = [sequential_to_site[seq] for seq in sequential_sites]
    combined = heatmap_bg + heatmap_muts + heatmap_wildtype
    combined = combined.encode(
        alt.X(
            "site:N",
            title=f"{loop_name}",
            sort=alt.SortField("sequential_site"),
            scale=alt.Scale(nice=False, zero=False),
            axis=alt.Axis(values=to_label_values, labelAngle=-90)  # Changed to 90 degrees
        ),
    )
    
    return combined

def main():
    csv_data = pd.read_csv(DATA_CSV, dtype={"site": int})
    all_loop_data = []
    loop_charts = []
    
    for loop_name, loop_info in LOOPS.items():
        loop_data = prepare_loop_data(csv_data, loop_name, loop_info)
        all_loop_data.append(loop_data)
        loop_chart = create_loop_heatmap(loop_data, loop_name)
        loop_charts.append(loop_chart)

    combined_heatmap = (
        alt.hconcat(*loop_charts, spacing=30)
        .configure_axis(
            tickColor="black", 
            tickSize=4, 
            titleFontSize=14,
            labelFontSize=11
        )
        .configure_legend(
            orient="bottom",
            gradientStrokeWidth=1,
            gradientStrokeColor="black",
            titleAnchor="middle",
            titleFontSize=14,
            labelFontSize=12,
            titleLimit=300,
        )
        .properties(title=TITLE)
        .configure_title(anchor="middle", fontSize=16, fontWeight='bold')
        .configure_view(strokeWidth=0)
    )

    combined_heatmap.save(CHART_HTML)
    print("Done!")
    
    return combined_heatmap

if __name__ == "__main__":
    chart = main()