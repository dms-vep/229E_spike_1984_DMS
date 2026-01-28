# Interactive Figure Generation Pipeline

This Snakemake pipeline generates all interactive figures for the homepage.


```bash
snakemake --cores 1
```
``

## Figures

1. **Figure 1**: wrapped heatmap
   - Output: `figures/cell_entry_heatmap_full_spike.html`
   
2. **Figure 2**: Site-wise amino acid diversity
   - Output: `figures/site_diversity_plot_interactive.html`
   
3. **Figure 3**: Binding loops cell entry heatmap
   - Output: `figures/cell_entry_heatmap_all_loops.html`

4. **Figure 4**: Coronavirus receptor binding comparison
   - Output: `figures/coronavirus_comparison_interactive.html`
   
5. **Figure 5**: Receptor binding vs sera escape correlation
   - Output: `figures/receptor_binding_escape_correlation_interactive.html`
