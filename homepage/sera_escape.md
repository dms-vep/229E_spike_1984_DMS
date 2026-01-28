---
aside: false
---

# Evolution-resistant and evolution-sensitive sera escape 

We measured how mutations in the HCoV-229E spike affect neutralization by Evolution-resistant compared to Evolution-sensitive sera. All sera samples were isolated in the 1980-1990's. 

Below are several ways to explore these data:
[[toc]]

## Line plots and heatmaps showing effects of mutations summarized by sera group

The plot below is interactive, and allows you to zoom and mouseover sites and mutations.
Click on the expansion box in the upper right of the plot to enlarge it for easier viewing, or click [here](htmls/summary_of_all_phenotypes_overlaid.html){target="_self"} for a standalone version of the plot.
The line plots summarize the effects of mutations at each measured site, while the heatmaps below show the effects of individual mutations.
Each panel groups all evolution-resistant or evolution-sesitive sera.
Note that the two different shades of gray in the heatmaps have differing meanings: light gray means a mutation was missing (not measured) in the library, whereas dark gray means a mutation was measured but was so deleterious for cell entry it is not possible to reliably estimate its effect on other phenotypes (the threshold for how deleterious a mutation must be for cell entry to be shown in dark gray is controlled by the cell entry slider at the bottom of the plot). This plot also includes the cell entry and hAPN binding heatmaps for easy comparison of the mutations’ effects on different phenotypes. 
 
<Figure caption="">
    <Altair :showShadow="true" :spec-url="'htmls/summary_of_all_phenotypes_overlaid.html'"></Altair>
</Figure>

## Per-individual comparison of effects of mutations neutralization by evolution-resistant and evolution-sensitive serum

The plots below show the effects of mutations on neutralization by sera from the same individual.
The scatter plots show the effects of individual mutations, and the line plots show the total effects of mutations at each site.
The zoom bar at top allows you to examine just certain regions of spike.

### Eevolution-sensitive serum

<Figure caption="SD85_3 serum">
    <Altair :showShadow="true" :spec-url="'htmls/85_3-sera_mut_effect.html'"></Altair>
</Figure>

<Figure caption="SD85_7 serum">
    <Altair :showShadow="true" :spec-url="'htmls/85_7-sera_mut_effect.html'"></Altair>
</Figure>

<Figure caption="SD87_2 serum">
    <Altair :showShadow="true" :spec-url="'htmls/87_2-sera_mut_effect.html'"></Altair>
</Figure>

<Figure caption="SD88_4 serum">
    <Altair :showShadow="true" :spec-url="'htmls/88_4-sera_mut_effect.html'"></Altair>
</Figure>

<Figure caption="SD93_4 serum">
    <Altair :showShadow="true" :spec-url="'htmls/93_4-sera_mut_effect.html'"></Altair>
</Figure>

### Eevolution-sensitive serum

<Figure caption="SD86_11 serum">
    <Altair :showShadow="true" :spec-url="'htmls/86_11-sera_mut_effect.html'"></Altair>
</Figure>

<Figure caption="SD88_10 serum">
    <Altair :showShadow="true" :spec-url="'htmls/88_10-sera_mut_effect.html'"></Altair>
</Figure>

<Figure caption="SD95_3 serum">
    <Altair :showShadow="true" :spec-url="'htmls/95_3-sera_mut_effect.html'"></Altair>
</Figure>

If you want to compare the sera escape between serum samples, please use this plot: 

<Figure caption="">
    <Altair :showShadow="true" :spec-url="'htmls/summary_of_all_phenotypes_faceted.html'"></Altair>
</Figure>

