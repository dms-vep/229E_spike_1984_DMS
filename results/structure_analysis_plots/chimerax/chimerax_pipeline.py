import pandas as pd
import argparse
import subprocess
import shutil
import os


def convert_sites_to_ref(entry_results, site_map_df, structure_pdb_entry):
    if structure_pdb_entry in ["6U7H", "8WDE"]:
        entry_results["ref_site"] = entry_results["site"]
    elif structure_pdb_entry == "6U7E":
        # map reference_site -> sequential_site + 18
        map_dict = dict(
            zip(
                site_map_df["reference_site"],
                site_map_df["sequential_site"] + 18,
            )
        )
        entry_results["ref_site"] = entry_results["site"].apply(
            lambda x: int(map_dict.get(x)) if map_dict.get(x) is not None else None
        )
        entry_results = entry_results[entry_results["ref_site"].notnull()]
    return entry_results


def chimerax_entry_prep(
    entry_df_path,
    effect_column,
    structure_pdb_entry,
    site_map_path,
    outdir,
):
    """
    entry_df_path: CSV with DMS results
    effect_column: column name to use (e.g. 'cell entry', 'receptor binding', 'human resistant sera escape')
    structure_pdb_entry: '6U7E', '6U7H', '8WDE'
    site_map_path: path to site_numbering_map.csv
    outdir: directory to write *_chimerax_{structure}.csv
    """
    print(entry_df_path)
    data = pd.read_csv(entry_df_path)
    site_map_df = pd.read_csv(site_map_path)
    type_dict = {
        "cell entry": "entry",
        "receptor binding": "binding",
        "human resistant sera escape": "escape",
        "human sensitive sera escape": "escape",
        "all sera escape": "escape",
    }

    if effect_column not in type_dict:
        raise ValueError(f"Unknown effect_column: {effect_column}")

    selection_type = type_dict[effect_column]

    data_ref = convert_sites_to_ref(data, site_map_df, structure_pdb_entry)
    print (selection_type)

    if selection_type == "escape":
        data_ref_filter = data_ref[data_ref['cell entry'] >= -2.5]
        data_ref_mean = (
            data_ref_filter.groupby(["ref_site"])[effect_column]
            .sum()
            .reset_index()
            .round(3)
        )

    elif selection_type == 'binding':
        data_ref_filter = data_ref[data_ref['cell entry'] >= -2.5]
        data_ref_mean = (
            data_ref_filter.groupby(["ref_site"])[effect_column]
            .mean()
            .reset_index()
            .round(3)
        )
    else:
        data_ref_mean = (
            data_ref.groupby(["ref_site"])[effect_column]
            .mean()
            .reset_index()
            .round(3)
        )
    print(data_ref_mean)
    data_ref_mean = data_ref_mean.rename(columns={"ref_site": "site"})
    data_ref_mean["site"] = data_ref_mean["site"].astype(int)

    # base file name logic
    if selection_type == "entry":
        base_file_name = "cell_entry"
    elif selection_type == "escape":
        antibody = str(effect_column).split()[1]  # resistant / sensitive / sera
        base_file_name = f"escape_{antibody}"
    elif selection_type == "binding":
        base_file_name = "receptor_binding"
    else:
        raise ValueError(f"Unknown selection_type: {selection_type}")

    # NEW: use outdir from CLI instead of undefined output_dir
    os.makedirs(outdir, exist_ok=True)
    mean_path = os.path.join(outdir, f"{base_file_name}_chimerax_{structure_pdb_entry}.csv")

    data_ref_mean.to_csv(mean_path, index=False)
    print(f"Saved mean data to {mean_path}")


def aggregate_entry_mean(infile, name, effect_col, outdir):
    tmp_df = pd.read_csv(infile).round(3)
    structure_id = infile.split("_")[-1].split(".")[0]

    tmp_df["site"] = tmp_df["site"].astype(str)
    tmp_df[effect_col] = tmp_df[effect_col].astype(str)
    tmp_df["formatted"] = "\t" + ":" + tmp_df["site"] + "\t" + tmp_df[effect_col]

    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, os.path.basename(infile).replace(".csv", ".csv"))
    if "_" in name:
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
    parser.add_argument("--effect_col", help="Effect column")
    parser.add_argument("--site_map", help="Path to site map")
    parser.add_argument("--outdir", help="Output directory for chimerax CSVs")
    parser.add_argument("--aggregate", action="store_true")
    parser.add_argument("--infile", help="File to aggregate")
    parser.add_argument("--name", help="Attribute name for aggregation")
    parser.add_argument("--effect_col_agg", help="Effect column for aggregation")
    parser.add_argument("--outdir_agg", help="Output directory for .defattr (optional)")

    args = parser.parse_args()

    if args.aggregate:
        # use outdir_agg if given, otherwise reuse outdir
        outdir = args.outdir_agg if args.outdir_agg is not None else args.outdir
        aggregate_entry_mean(args.infile, args.name, args.effect_col_agg, outdir)
    else:
        chimerax_entry_prep(
            entry_df_path=args.func_file,
            structure_pdb_entry=args.structure,
            effect_column=args.effect_col,
            site_map_path=args.site_map,
            outdir=args.outdir,
        )
