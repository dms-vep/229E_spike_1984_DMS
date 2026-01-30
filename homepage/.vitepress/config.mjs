import { defineConfig } from "vitepress";

// https://vitepress.dev/reference/site-config
export default defineConfig({
  lang: "en-US",
  title: "Pseudovirus deep mutational scanning of HCoV-229E spike protein (1984 strain)",
  description:
    "Interactive figures from pseudovirus deep mutational scanning of the HCoV-229E spike",
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
      message: 'Study by Sheri Harari in the <a href="https://jbloomlab.org/">Bloom Lab</a>',
    },
  },
});
