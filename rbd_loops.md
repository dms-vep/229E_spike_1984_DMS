---
aside: false
---

# Comparison of natural HCoV-229E diversity to cell entry effects in the RBD binding loops.
We compared the natural amino-acid variation of HCoV-229E spike to the measured effects of mutations on cell entry in the RBD binding loops. For further exploration:
[[toc]]

## Site-wise Amino Acid Diversity of Natural Sequences of HCoV-229E

- The **black bars** represent the effective number of amino acids at each site, calculated from Shannon entropy.
- The **bar** at the top indicate major spike domains: NTD, RBD, and S2.
- The **loop labels** (L1, L2, L3) mark the three receptor-binding loops within the RBD.
- **Hover over bars** to see the exact effective number of amino acids, amino acid richness, and domain assignment for each site.

Click on the expansion box in the upper right of the plot to enlarge for easier viewing, or click [here](/htmls/site_diversity_plot_interactive.html) to open the plot in a stand-alone window.

<Figure caption="">
    <Altair :showShadow="true" :spec-url="'htmls/site_diversity_plot_interactive.html'"></Altair>
</Figure>

## RBD binding loops cell entry effcets

- The **three panels** show Loop 1 (308-325), Loop 2 (352-359), and Loop 3 (404-408) side by side for easy comparison.
- The **X marks** indicate the 1984 strain amino acid identity at each position.
- **Hover over any cell** to see the exact site, wildtype amino acid, mutant amino acid, and quantitative cell entry effect.


click [here](htmls/cell_entry_heatmap_all_loops.html){target="_self"} for a standalone link:

<Figure caption="">
    <Altair :showShadow="true" :spec-url="'htmls/cell_entry_heatmap_all_loops.html'"></Altair>
</Figure>
