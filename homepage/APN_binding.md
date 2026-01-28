---
aside: false
---

# Effects of HCoV-229E spike mutations on human APN binding.

## Interactive plot
The plots below show how mutations affect the binding of the human APN receptor. These plots are interactive, and allow you to zoom and mouseover sites and mutations.
- The **zoom bar** at the top of the plot shows different regions of spike, and can be used to zoom in on specific sites.
- The **line plot** summarizes the effects of mutations on cell entry at each site (more negative values indicate impaired cell entry). The cell entry at a site is quantified using the site summary statistic specified by the interactive option at the bottom of the plot (e.g., mean effect of mutations at a site).
- The **heatmap** shows how each individual mutation affects cell entry. The `X`'s indicate the amino-acid identity in the 1984 strain. Light gray tiles indicate mutations that were missing (not measured) in the library.

Click on the expansion box in the upper right of the plot to enlarge for easier viewing, or click [here](https://dms-vep.org/229E_spike_1984_DMS/htmls/human_APN_binding_mut_effect.html) to open the plot in a stand-alone window.

<Figure caption="">
    <Altair :showShadow="true" :spec-url="'htmls/human_APN_binding_mut_effect.html'"></Altair>
</Figure>

For a wrapped version of the heatmap, click [here](htmls/receptor_binding_heatmap_full_spike.html).

## Numerical values
The **pre-filtered** numerical data plotted on this page can be found [here](https://github.com/dms-vep/229E_spike_1984_DMS/blob/main/results/summaries/cell_entry_and_binding.csv). Alternatively, the **unfiltered** data are available [here](https://github.com/dms-vep/229E_spike_1984_DMS/blob/main/results/receptor_affinity/averages/human_APN_binding_mut_effect.csv). Note the unfiltered data have not been filtered for QC criteria like `times_seen`, so either make sure you understand the filters in the file or we recommend just using the pre-filtered data.