---
aside: false
---

# Human Sera neutralization profile 

We measured how mutations in the HCoV-229E spike affect neutralization by human sera. The line plots summarize the total effects of mutations at each measured site averged for eight sera samples, while the heatmaps below show the average effects of individual mutations.

Note that the two different shades of gray in the heatmaps have differing meanings: light gray means a mutation was missing (not measured) in the library, whereas dark gray means a mutation was measured but was so deleterious for cell entry it is not possible to reliably estimate its effect on other phenotypes (the threshold for how deleterious a mutation must be for cell entry to be shown in dark gray is controlled by the cell entry slider at the bottom of the plot). This plot also includes the cell entry and hAPN binding heatmaps for easy comparison of the mutations’ effects on different phenotypes.
See [here](https://github.com/dms-vep/229E_spike_1984_DMS/blob/main/results/summaries/summary_of_all_sera.csv) for a CSV with the total escape for each site.
A standalon version of this plot is avilable [here](https://dms-vep.org/229E_spike_1984_DMS/htmls/summary_of_all_sera_overlaid.html).

<Figure caption="">
    <Altair :showShadow="true" :spec-url="'htmls/summary_of_all_sera_overlaid.html'"></Altair>
</Figure>

# Corrlation between hAPN binding and serum neutralization

Some mutations in the spike protein can favor the RBD “up” or “down” conformation. This shift can increase or decrease hAPN binding, respectively. These conformational changes also affect spike neutralization by human sera. The correlation between these two phenotypes is shown in the following interactive plot.

- The **scatter points** represent individual sites in the spike protein total sera escap vs the mean hAPN binding per site, colored by the spike region.
- **Hover over points** to see detailed information including site number, wildtype amino acid, exact receptor binding and sera escape values, and the spike region.  

<Figure caption="">
    <Altair :showShadow="true" :spec-url="'htmls/receptor_binding_escape_correlation_interactive.html'"></Altair>
</Figure>

# Sites that affect RBD up/down conformation

The lineplot below shows the estimated effect each site has on RBD up/down motion (click [here](htmls/RBD_up_down_chart_html.html){target="_self"} for a standalone link to this plot). The larger the value the more impact that mutations at that site are estimated to have on RBD motion. 

The effect of each site on RBD up/down conformation is estimated from the deep mutational scanning by calculating correlation (Pearson R) between serum neutralization escape and hAPN binding for all mutations each site, multiplying that correlation by minus one and weighting it by the root-mean-square (RMS) effect of all mutations at the site on hAPN binding and the RMS effect of all mutations at the site on serum neutralization escape. Sites with positive correlation had the effect floored to zero. This metric captures the fact that mutations at sites that affect RBD up/down conformation tend to have opposing effects on ACE2 binding and serum neutralization escape. Only sites where binding and neutralization effects could be measured for at least five mutations are shown. 
See [here](https://github.com/dms-vep/229E_spike_1984_DMS/blob/main/results/RBD_up_down/RBD_up_down_sites.csv) for a CSV with these estimated effects for each site; the *RxRMS_be* gives the final effect estimate for each site calculated as above.


<Figure caption="Effects of mutations on  RBD up/down motion">
    <Altair :showShadow="true" :spec-url="'htmls/RBD_up_down_chart_html.html'"></Altair>
</Figure>