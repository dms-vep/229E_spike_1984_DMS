import pandas as pd
import altair as alt

# Configuration
DATA_CSV = "../results/summaries/cell_entry_and_binding.csv"
CHART_HTML = "figures/receptor_binding_heatmap_full_spike.html"
TITLE = "Effect of mutations to 229E spike protein on receptor binding in 293T-hAPN-TMPRSS2 cells"
EFFECT_COL = "receptor binding"
COLOR_SCHEME = "purpleorange"
FIXED_MIN = -2
FIXED_MAX = 2
ALPHABET = "RKHDEQNSTYWFAILMVGPC"
SITES_PER_ROW = 150
SITE_LABEL_FREQ = 10
SITE_LABEL_START = 5
W_STEP = 9
H_STEP = 9

# Dark gray mutations filter
DARK_GRAY_MUTS = {
    "col": "cell entry",
    "cutoff": -2.5
}

def create_wrapped_heatmap(data_csv, output_file):
    
    if isinstance(ALPHABET, str):
        alphabet = list(ALPHABET)
    else:
        alphabet = ALPHABET
    
    data = pd.read_csv(data_csv, dtype={"site": str})
    print(f"Read {len(data)} rows with columns: {list(data.columns)}")
    
    req_cols = ["site", "sequential_site", "wildtype", "mutant", EFFECT_COL]
    
    if DARK_GRAY_MUTS and (DARK_GRAY_MUTS["col"] not in data.columns):
        raise ValueError(f"{DARK_GRAY_MUTS['col']} not in {data.columns}")
    elif DARK_GRAY_MUTS and (DARK_GRAY_MUTS["col"] not in req_cols):
        req_cols.append(DARK_GRAY_MUTS["col"])
    
    data = data[data["mutant"].isin(alphabet) & data["wildtype"].isin(alphabet)].reset_index(drop=True)
    print(f"After filtering to amino acids in alphabet: {len(data)} mutations")
    
    data = data[req_cols]
    
 
    assert len(data) == len(data.groupby(["site", "wildtype", "mutant"]))
    
  
    heatmap_base = (
        alt.Chart(data)
        .encode(alt.Y("mutant", sort=alphabet, title="amino acid"))
        .properties(width=alt.Step(W_STEP), height=alt.Step(H_STEP))
    )

    heatmap_bg = heatmap_base.transform_impute(
        impute="_stat_dummy",
        key="mutant",
        keyvals=alphabet,
        groupby=["site"],
        value=None,
    ).mark_rect(color="#E0E0E0", opacity=0.8)
    
    heatmap_wildtype = (
        heatmap_base
        .transform_filter(alt.datum["wildtype"] == alt.datum["mutant"])
        .mark_text(text="x", color="black")
    )
    
    heatmap_muts = (
        heatmap_base
        .encode(
            alt.Color(
                EFFECT_COL,
                scale=alt.Scale(
                    scheme=COLOR_SCHEME,
                    domainMid=0,
                    domainMin=FIXED_MIN,
                    domainMax=FIXED_MAX,
                    clamp=True,
                    reverse=True,  
                ),
            ),
            tooltip=["site", "mutant", "wildtype", alt.Tooltip(EFFECT_COL, format=".2f")],
        )
        .mark_rect(stroke="black", opacity=1, strokeOpacity=1)
    )
    

    if DARK_GRAY_MUTS:
        heatmap_muts = heatmap_muts.transform_filter(
            alt.datum[DARK_GRAY_MUTS["col"]] >= DARK_GRAY_MUTS["cutoff"]
        )
        

        heatmap_dark_gray = (
            heatmap_base
            .transform_filter(alt.datum[DARK_GRAY_MUTS["col"]] < DARK_GRAY_MUTS["cutoff"])
            .transform_calculate(filtered="0")
            .mark_rect(stroke="black", opacity=1, strokeOpacity=1, color="silver")
        )
    

    heatmap_rows = []
    sequential_sites = sorted(data["sequential_site"].unique())
    
    for i in range(0, len(sequential_sites), SITES_PER_ROW):
        row_sites = sequential_sites[i: i + SITES_PER_ROW]
        last_row = row_sites[-1] == sequential_sites[-1]
        sequential_to_site = data.set_index("sequential_site")["site"].to_dict()
        

        if SITE_LABEL_START is not None:
            to_label_sequential = []
            current_label = SITE_LABEL_START
            while current_label <= row_sites[-1]:
                if current_label >= row_sites[0]:
                    to_label_sequential.append(current_label)
                current_label += SITE_LABEL_FREQ
            to_label_values = [
                sequential_to_site[seq_site]
                for seq_site in to_label_sequential
                if seq_site in sequential_to_site
            ]
        else:
            to_label_values = [
                sequential_to_site[i]
                for i in range(row_sites[0], row_sites[-1], SITE_LABEL_FREQ)
            ]
        

        if DARK_GRAY_MUTS:
            row_charts = heatmap_bg + heatmap_dark_gray + heatmap_muts + heatmap_wildtype
        else:
            row_charts = heatmap_bg + heatmap_muts + heatmap_wildtype
        
        heatmap_rows.append(
            row_charts
            .encode(
                alt.X(
                    "site:N",
                    title="site" if last_row else None,
                    sort=alt.SortField("sequential_site"),
                    scale=alt.Scale(nice=False, zero=False),
                    axis=alt.Axis(values=to_label_values, labelAngle=0)
                ),
            )
            .transform_filter(
                (alt.datum["sequential_site"] >= min(row_sites))
                & (alt.datum["sequential_site"] <= max(row_sites))
            )
        )
    
    heatmap = (
        alt.vconcat(*heatmap_rows, spacing=15)
        .configure_axis(tickColor="black", tickSize=4, titleFontSize=16)
        .configure_legend(
            orient="bottom",
            gradientStrokeWidth=1,
            gradientStrokeColor="black",
            titleAnchor="middle",
            titleFontSize=16,
            titleLimit=200,
        )
        .properties(title=TITLE)
        .configure_title(anchor="middle", fontSize=18)
    )
    
    print(f"Saving {output_file}")
    heatmap.save(output_file)
    print("Done!")
    
    return heatmap


def main():
    """Main execution function"""
    chart = create_wrapped_heatmap(DATA_CSV, CHART_HTML)
    return chart


if __name__ == "__main__":
    chart = main()