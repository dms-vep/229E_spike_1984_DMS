---
layout: home

hero:
  name: Pseudovirus deep mutational scanning of HCoV-229E spike (1984 strain)
  tagline: Interactive visualizations of effects of mutations on different HCoV-229E (1984 strain) spike phenotypes
  image: 229E-main_page_pic.png
features:
  - title: Cell entry
    details: Effects of mutations on entry into 293T-hAPN-TMPRSS2 cells
    link: /cell_entry
  - title: RBD binding loops constraints
    details: The RBD binding loops cell entry measurements compared to natural variation
    link: /rbd_loops
  - title: Receptor binding
    details: Mutation effects of HCoV-229E 1984 spike on binding to hAPN
    link: /APN_binding
  - title: Serum neutralization and RBD up/down conformation
    details: Sites that affect serum neutralization and RBD up/down conformation
    link: /RBD_up_down
  - title: Serum neutralization by different types of sera
    details: Mutations effects on neutralization by evolution-resistant and evolution-sensitive human sera 
    link: /sera_escape
---

The links in the gray boxes above take you to pages with details about the experimental measurements of the effects of mutations on different spike phenotypes, as well as interactive visualizations and links to the numerical measurements for each mutation.

For details about the study, see [Harari et al (2026)](https://www.biorxiv.org/content/10.64898/2026.02.22.707297v1).

All experiments were performed at biosafety-level-2 using [pseudoviruses](https://pubmed.ncbi.nlm.nih.gov/36868218/), which are only able to undergo a single round of cell entry and so are therefore not replicative viruses capable of causing disease.

For the full computer code and numerical results, see the GitHub repo at [https://github.com/dms-vep/229E_spike_1984_DMS](https://github.com/dms-vep/229E_spike_1984_DMS).
For full documentation of the analysis pipeline, see the [Appendix](appendix.html){target="_self"}.
