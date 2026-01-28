import numpy as np
import pandas as pd
import altair as alt
from Bio import AlignIO
from collections import Counter

# Configuration
MSA_FILE = "data/protein_ungapped_no_outgroup.fasta"
MSA_FORMAT = "fasta"
OUTPUT_FILE = 'figures/site_diversity_plot_interactive.html'

class DiversityAnalyzer:
    
    def __init__(self, msa_file, file_format='fasta'):
        self.alignment = AlignIO.read(msa_file, file_format)
        self.length = self.alignment.get_alignment_length()
        self.num_sequences = len(self.alignment)
        
        # Define 229E spike domains
        self.domains = {
            'NTD': (38, 267),
            'RBD': (293, 435),
            'Loop1': (308, 325),
            'Loop2': (352, 359),
            'Loop3': (404, 408),
            'S2': (575, 1113)
        }
        
        # Color palette
        self.domain_colors = {
            'NTD': '#4477AA',
            'RBD': '#EE6677',
            'Loop1': '#8B0000',
            'Loop2': '#8B0000',
            'Loop3': '#8B0000',
            'S2': '#66CCEE',
            'Other': '#CCCCCC'
        }
        
    def calculate_effective_num_aa(self, site_index):
        column = self.alignment[:, site_index]
        column_no_gaps = [aa for aa in column if aa not in ['-', 'X', '?', '*', 'B', 'Z', 'J']]
        
        if len(column_no_gaps) == 0:
            return 1.0
        
        aa_counts = Counter(column_no_gaps)
        total = len(column_no_gaps)
        
        entropy = 0.0
        for count in aa_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)
        
        effective_num = 2 ** entropy
        return effective_num
    
    def calculate_all_diversity(self):
        results = []
        
        for i in range(self.length):
            effective_num = self.calculate_effective_num_aa(i)
            site = i + 1
            domain = self.get_domain(site)
            
            column = self.alignment[:, i]
            column_no_gaps = [aa for aa in column if aa not in ['-', 'X', '?', '*', 'B', 'Z', 'J']]
            aa_richness = len(set(column_no_gaps))
            
            results.append({
                'site': site,
                'effective_num_aa': effective_num,
                'domain': domain,
                'aa_richness': aa_richness
            })
        
        return pd.DataFrame(results)
    
    def get_domain(self, site):
        """Get domain name for a given site (loops take priority)"""
        for domain in ['Loop1', 'Loop2', 'Loop3']:
            start, end = self.domains[domain]
            if start <= site <= end:
                return domain
        
        for domain in ['NTD', 'RBD', 'S2']:
            start, end = self.domains[domain]
            if start <= site <= end:
                return domain
        
        return 'Other'
    
    def create_interactive_plot(self, output_file):
        df = self.calculate_all_diversity()
        
        # Create domain annotations data
        domain_annotations = []
        main_domains = ['NTD', 'RBD', 'S2']
        
        for domain in main_domains:
            start, end = self.domains[domain]
            domain_annotations.append({
                'domain': domain,
                'start': start - 0.5,  
                'end': end + 0.5,      
                'mid': (start + end) / 2,  
                'y_rect': 3.15,  # 
                'y_domain_label': 3.22,  
                'color': self.domain_colors[domain]
            })
        
        domain_df = pd.DataFrame(domain_annotations)

        loop_annotations = []
        for loop in ['Loop1', 'Loop2', 'Loop3']:
            start, end = self.domains[loop]
            loop_short = loop.replace('Loop', 'L')
            loop_annotations.append({
                'loop': loop_short,
                'start': start,
                'end': end,
                'mid': (start + end) / 2,
                'y_label': 3.05  
            })
        
        loop_df = pd.DataFrame(loop_annotations)
        
        bars = alt.Chart(df).mark_bar(
            color='black',
            opacity=1.0,
            size=0.8  
        ).encode(
            x=alt.X('site:Q',
                   title='Site',
                   scale=alt.Scale(domain=[0, df['site'].max() + 50])),
            y=alt.Y('effective_num_aa:Q',
                   title='Effective amino acids',
                   scale=alt.Scale(domain=[1, 3.3])),  
            y2=alt.datum(1),  # Set baseline to 1
            tooltip=[
                alt.Tooltip('site:Q', title='Site'),
                alt.Tooltip('effective_num_aa:Q', title='Effective # AA', format='.3f'),
                alt.Tooltip('domain:N', title='Domain'),
                alt.Tooltip('aa_richness:Q', title='AA Richness')
            ]
        )
        
        domain_rects = alt.Chart(domain_df).mark_rect(
            opacity=0.3,
            stroke='black',
            strokeWidth=1.2
        ).encode(
            x=alt.X('start:Q', scale=alt.Scale(domain=[0, df['site'].max() + 50])),
            x2=alt.X2('end:Q'),
            y=alt.Y('y_rect:Q', scale=alt.Scale(domain=[1, 3.3])),
            y2=alt.datum(3.28),  # Fixed height - top of rectangle
            color=alt.Color('color:N', scale=None),
            tooltip=alt.Tooltip('domain:N')
        )
        

        domain_labels = alt.Chart(domain_df).mark_text(
            fontSize=14,
            fontWeight='bold',
            align='center',
            baseline='middle'
        ).encode(
            x=alt.X('mid:Q', scale=alt.Scale(domain=[0, df['site'].max() + 50])),
            y=alt.Y('y_domain_label:Q', scale=alt.Scale(domain=[1, 3.3])),  # Use y_domain_label
            text='domain:N'
        )
        

        loop_labels = alt.Chart(loop_df).mark_text(
            fontSize=12,
            fontWeight='bold',
            align='center',
            baseline='top'
        ).encode(
            x=alt.X('mid:Q', scale=alt.Scale(domain=[0, df['site'].max() + 50])),
            y=alt.Y('y_label:Q', scale=alt.Scale(domain=[1, 3.3])),
            text='loop:N'
        )
        

        chart = alt.layer(
            bars,
            domain_rects,
            domain_labels,
            loop_labels
        ).properties(
            width=1400,  # Even wider
            height=350,
            title=alt.TitleParams(
                text='Effective amino acid diversity of HCoV-229E Spike natural sequences',
                fontSize=18,
                fontWeight='bold'
            )
        ).configure_axis(
            labelFontSize=14,
            titleFontSize=16,
            titleFontWeight='bold',
            grid=False
        ).configure_view(
            strokeWidth=0
        )
        
        # Save to HTML
        chart.save(output_file)
        
        return df, chart


def main():
    
    try:
        analyzer = DiversityAnalyzer(MSA_FILE, file_format=MSA_FORMAT)
        df_results, chart = analyzer.create_interactive_plot(OUTPUT_FILE)
         
    except FileNotFoundError:
        print(f"Error: Could not find MSA file '{MSA_FILE}'")
        print("Please update the MSA_FILE variable with your actual file path")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()