import pandas as pd
import argparse
import subprocess
import shutil
import os

def convert_sites_to_ref(entry_results, site_map_df, structure_pdb_entry):
    if structure_pdb_entry == '6U7H' or structure_pdb_entry == '8WDE':
        entry_results['ref_site'] = entry_results['site']
    elif structure_pdb_entry == '6U7E':
        map_dict = dict(zip(site_map_df['reference_site'], site_map_df['sequential_site'] + 18))
        entry_results['ref_site'] = entry_results['site'].apply(
            lambda x: int(map_dict.get(x)) if map_dict.get(x) is not None else None
        )
        entry_results = entry_results[entry_results['ref_site'].notnull()]
    return entry_results

def chimerax_entry_prep(entry_df_path, structure_pdb_entry, std_column, effect_column,
                        site_map_path, times_seen=2, entry_std=3, min_effect=-2.5):
    func_data = pd.read_csv(entry_df_path)
    entry_df = pd.read_csv('/fh/fast/bloom_j/computational_notebooks/sharari/2024/229E_spike_1984_DMS/results/func_effects/averages/cell_entry_func_effects.csv')
    site_map = pd.read_csv(site_map_path)

    selection_type = entry_df_path.split('/')[9]
    print(selection_type)
    if selection_type != 'func_effects':
        merged_df = pd.merge(entry_df, func_data, how="left", on=["site", "wildtype", "mutant"],
                             suffixes=("_entry", f"_{selection_type}"))
        func_data_filtered = merged_df[
            (merged_df["times_seen_entry"] >= times_seen) &
            (merged_df[f"times_seen_{selection_type}"] >= times_seen) &
            (merged_df[std_column] <= entry_std) &
            (merged_df['effect_std'] <= entry_std) &
            (merged_df['effect'] >= min_effect) &
            (merged_df["mutant"] != "*") &
            (merged_df["mutant"] != "-")
        ]
    else:
        func_data_filtered = func_data[
            (func_data["times_seen"] >= times_seen) &
            (func_data[std_column] <= entry_std) &
            (func_data["mutant"] != "*") &
            (func_data["mutant"] != "-")
        ]

    func_data_filtered_ref = convert_sites_to_ref(func_data_filtered, site_map, structure_pdb_entry)

    if selection_type == 'antibody_escape':
        func_data_filtered_mean = (
            func_data_filtered_ref.groupby(["ref_site"])[effect_column].sum().reset_index().round(3)
        )
    else:
        func_data_filtered_mean = (
            func_data_filtered_ref.groupby(["ref_site"])[effect_column].mean().reset_index().round(3)
        )

    func_data_filtered_mean = func_data_filtered_mean.rename(columns={'ref_site': 'site'})
    func_data_filtered_mean['site'] = func_data_filtered_mean['site'].astype(int)

    if std_column == 'effect_std':
        base_file_name = 'entry'
    elif selection_type == 'antibody_escape':
        antibody = entry_df_path.split('/')[-1].split('-sera')[0]
        antibody = antibody.replace("_", "-")
        base_file_name = f'escape_{antibody}'
    else:
        base_file_name = std_column.split('_')[0]
    output_dir = "chimerax_files"
    os.makedirs(output_dir, exist_ok=True)

    filtered_path = f"{output_dir}/{base_file_name}_filtered_{structure_pdb_entry}.csv"
    mean_path = f"{output_dir}/{base_file_name}_filtered_chimerax_{structure_pdb_entry}.csv"

    func_data_filtered.to_csv(filtered_path, index=False)
    func_data_filtered_mean.to_csv(mean_path, index=False)
    print(f"Saved filtered data to {filtered_path}")
    print(f"Saved mean data to {mean_path}")

def aggregate_entry_mean(infile, name, effect_col, outdir):
    tmp_df = pd.read_csv(infile).round(3)
    structure_id = infile.split('_')[-1].split('.')[0]

    tmp_df["site"] = tmp_df["site"].astype(str)
    tmp_df[effect_col] = tmp_df[effect_col].astype(str)
    tmp_df["formatted"] = "\t" + ":" + tmp_df["site"] + "\t" + tmp_df[effect_col]

    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, os.path.basename(infile).replace('.csv', '.csv'))
    if '_' in name:
        name = name.split("_")[0]

    with open(outfile, "w") as f:
        f.write(f"attribute: {name}\n")
        f.write("match mode: any\n")
        f.write("recipient: residues\n")

    tmp_df["formatted"].to_csv(outfile, sep="\t", index=False, header=False, mode="a")

    subprocess.run(["sed", "-i", 's/"//g', outfile], check=True)
    new_filename = outfile.replace(".csv", ".defattr")
    shutil.copy(outfile, new_filename)
    print(f"Saved .defattr to {new_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--func_file", help="Path to function CSV")
    parser.add_argument("--structure", help="Structure PDB ID")
    parser.add_argument("--std_col", help="Standard deviation column")
    parser.add_argument("--effect_col", help="Effect column")
    parser.add_argument("--site_map", help="Path to site map")
    parser.add_argument("--aggregate", action="store_true")
    parser.add_argument("--infile", help="File to aggregate")
    parser.add_argument("--name", help="Attribute name for aggregation")
    parser.add_argument("--effect_col_agg", help="Effect column for aggregation")
    parser.add_argument("--outdir", help="Output directory for .defattr")

    args = parser.parse_args()

    if args.aggregate:
        aggregate_entry_mean(args.infile, args.name, args.effect_col_agg, args.outdir)
    else:
        chimerax_entry_prep(
            entry_df_path=args.func_file,
            structure_pdb_entry=args.structure,
            std_column=args.std_col,
            effect_column=args.effect_col,
            site_map_path=args.site_map,
        )
