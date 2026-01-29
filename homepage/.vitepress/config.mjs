import { defineConfig } from "vitepress";

// https://vitepress.dev/reference/site-config
export default defineConfig({
  lang: "en-US",
  title: "Pseudovirus deep mutational scanning of HCoV-229E 1984 spike protein",
  description:
    "A collection of data, figures, and analysis for exploring the HCoV-229E evolution by mapping spike constraints.",
  base: "/229E_spike_1984_DMS/",
  appearance: false,
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: "Home", link: "/" },
      { text: "Appendix", link: "/appendix", target: "_self" },
    ],
    socialLinks: [{ icon: "github", link: "https://github.com/dms-vep/229E_spike_1984_DMS" }],
    footer: {
      message: "Built by Sheri Harari and Jesse Bloom",
    },
  },
});
