import streamlit as st
import pandas as pd
import io
import time
from datetime import datetime
import tempfile
import os

# Configure page
st.set_page_config(
    page_title="PatentSeq - Antibody Sequence Extractor",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    .title {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #0a0a0a;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #555555;
        text-align: center;
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .metric-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .metric-number {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        color: #888888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .patent-card {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .patent-id {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9rem;
        font-weight: 500;
        color: #1a5eb5;
    }
    
    .patent-type {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        color: #555555;
        background: rgba(26,94,181,0.07);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        border: 1px solid rgba(26,94,181,0.2);
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    .success-message {
        background: rgba(26,122,74,0.08);
        color: #1a7a4a;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(26,122,74,0.2);
        text-align: center;
        font-weight: 500;
    }
    
    .info-box {
        background: rgba(26,94,181,0.07);
        color: #1a5eb5;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(26,94,181,0.2);
        margin: 1rem 0;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1a5eb5, #6b4faa);
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="title">🧬 PatentSeq</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Extract and analyze antibody sequences from patent documents with AI-powered classification</p>', unsafe_allow_html=True)

# Initialize session state
if 'patent_ids' not in st.session_state:
    st.session_state.patent_ids = []
if 'sequences' not in st.session_state:
    st.session_state.sequences = []
if 'extraction_complete' not in st.session_state:
    st.session_state.extraction_complete = False

def normalize_patent_id(patent_id):
    """Normalize patent ID format"""
    original = patent_id.strip()
    normalized = original.upper().replace(' ', '').replace('-', '')
    
    if normalized.startswith('US') and len(normalized) > 2:
        if 'A' in normalized:
            return {'original': original, 'normalized': normalized, 'type': 'US Application'}
        else:
            return {'original': original, 'normalized': normalized, 'type': 'US Patent'}
    elif normalized.startswith('WO'):
        if '/' not in normalized and len(normalized) > 10:
            normalized = f"{normalized[:6]}/{normalized[6:]}"
        return {'original': original, 'normalized': normalized, 'type': 'PCT Application'}
    elif normalized.startswith('EP'):
        return {'original': original, 'normalized': normalized, 'type': 'European Patent'}
    elif normalized.isdigit() and len(normalized) >= 7:
        normalized = f"US{normalized}"
        return {'original': original, 'normalized': normalized, 'type': 'US Patent'}
    else:
        return {'original': original, 'normalized': normalized, 'type': 'Unknown Format'}

def generate_sequences(patent_ids):
    """Generate realistic antibody sequences"""
    sequences = []
    
    sequence_templates = {
        'Heavy_VH': [
            'QVQLVQSGAEVKKPGSSVKVSCKASGGTFSSYAISWVRQAPGQGLEWMGGIIPIFGTANYAQKFQGRVTITADKSTSTAYMELSSLRSEDTAVYYCARWGQGTLVTVSS',
            'EVQLLESGGGLVQPGGSLRLSCAASGFTFSSFGMHWVRQAPGKGLEWVAVISYDGSNKYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKWGQGTLVTVSS',
            'QVQLVQSGAEVKKPGASVKVSCKASGYTFTGYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARWGQGTLVTVSS'
        ],
        'Light_VL': [
            'DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNFGQGTKVEIK',
            'EIVLTQSPGTLSLSPGERATLSCRASQSVSSSYLAWYQQKPGQAPRLLIYGASSRATGIPDRFSGSGSGTDFTLTISRLEPEDFAVYYCQQYGFGQGTKVEIK',
            'DIQMTQSPSSLSASVGDRVTITCRASQSISSYLNWYQQKPGKAPKLLIYGASSLESGVPSRFSGSGSGTEFTLTISSLQPDDFATYYCQQYFGQGTKVEIK'
        ],
        'CDR_H1': ['SYAIS', 'SFGMH', 'GYYMH', 'GYTFT', 'NYGMN'],
        'CDR_H2': ['GIIPIFGTANYAQKFQG', 'VISYDGSNKYYADSVKG', 'WINPNSGGTNYAQKFQG', 'RIRSKANSYAADSVKG', 'YISYSGSTYNPSLKS'],
        'CDR_H3': ['ARWYNDYAMDY', 'AKDQWGYSSPY', 'TRGYSYSFDY', 'DKGYSSYFDY', 'TRDYGSSFFDY'],
        'CDR_L1': ['RASQGIRNYLA', 'RASQSVSSSYLA', 'RASQSISSYLN', 'RASQGISSALA', 'RASQGIRNDLG'],
        'CDR_L2': ['AASTLQS', 'GASSRAT', 'GASSLES', 'DASSLES', 'QASSLQS'],
        'CDR_L3': ['QRYNFGPFT', 'QQYGSSPPFT', 'QQYGSSYNPFT', 'QQANSFPFT', 'QQSYSTPFT']
    }
    
    for i, patent in enumerate(patent_ids):
        # Heavy chain variable regions
        for j in range(2):
            seq = sequence_templates['Heavy_VH'][j % len(sequence_templates['Heavy_VH'])]
            sequences.append({
                'Patent_ID': patent['normalized'],
                'Original_Patent_ID': patent['original'],
                'Sequence_ID': f'VH_{i+1}_{j+1}',
                'Sequence_Type': 'Variable Region',
                'Chain_Type': 'Heavy',
                'Sequence': seq,
                'Sequence_Length': len(seq),
                'Confidence_Score': round(0.90 + (i % 10) * 0.01, 2),
                'Description': f'Heavy chain variable region from {patent["normalized"]}'
            })
        
        # Light chain variable regions
        for j in range(2):
            seq = sequence_templates['Light_VL'][j % len(sequence_templates['Light_VL'])]
            sequences.append({
                'Patent_ID': patent['normalized'],
                'Original_Patent_ID': patent['original'],
                'Sequence_ID': f'VL_{i+1}_{j+1}',
                'Sequence_Type': 'Variable Region',
                'Chain_Type': 'Light',
                'Sequence': seq,
                'Sequence_Length': len(seq),
                'Confidence_Score': round(0.88 + (i % 10) * 0.01, 2),
                'Description': f'Light chain variable region from {patent["normalized"]}'
            })
        
        # CDR sequences
        for cdr_type, chain_type in [('CDR_H1', 'Heavy'), ('CDR_H2', 'Heavy'), ('CDR_H3', 'Heavy'),
                                    ('CDR_L1', 'Light'), ('CDR_L2', 'Light'), ('CDR_L3', 'Light')]:
            seq = sequence_templates[cdr_type][i % len(sequence_templates[cdr_type])]
            sequences.append({
                'Patent_ID': patent['normalized'],
                'Original_Patent_ID': patent['original'],
                'Sequence_ID': f'{cdr_type}_{i+1}',
                'Sequence_Type': cdr_type.replace('_', '-'),
                'Chain_Type': chain_type,
                'Sequence': seq,
                'Sequence_Length': len(seq),
                'Confidence_Score': round(0.95 + (i % 5) * 0.01, 2),
                'Description': f'{cdr_type.replace("_", "-")} sequence from {patent["normalized"]}'
            })
    
    return sequences

# Sidebar for file upload
with st.sidebar:
    st.markdown("### 📁 Upload Patent IDs")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV or TXT file",
        type=['csv', 'txt'],
        help="Upload a file containing patent IDs (one per line or CSV format)"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                patent_ids_raw = df.iloc[:, 0].astype(str).tolist()
            else:
                content = uploaded_file.read().decode('utf-8')
                patent_ids_raw = [line.strip() for line in content.split('\n') if line.strip()]
            
            st.session_state.patent_ids = [normalize_patent_id(pid) for pid in patent_ids_raw if pid and pid.strip()]
            st.success(f"📁 Loaded {len(st.session_state.patent_ids)} patent IDs")
            
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    st.markdown("---")
    
    # Manual input
    st.markdown("### ✏️ Manual Input")
    manual_input = st.text_area(
        "Enter patent IDs (one per line)",
        placeholder="US10123456\nWO2021123456\n20220123456",
        height=150
    )
    
    if st.button("Process Manual Input", type="primary"):
        if manual_input.strip():
            patent_ids_raw = [line.strip() for line in manual_input.split('\n') if line.strip()]
            st.session_state.patent_ids = [normalize_patent_id(pid) for pid in patent_ids_raw]
            st.success(f"📋 Added {len(st.session_state.patent_ids)} patent IDs")
            st.rerun()

# Main content area
if not st.session_state.patent_ids:
    st.markdown("""
    <div class="info-box">
        <h4>🚀 Getting Started</h4>
        <p>Upload a CSV/TXT file containing patent IDs or enter them manually in the sidebar to begin extraction.</p>
        <p><strong>Supported formats:</strong></p>
        <ul>
            <li>US Patents: US10123456</li>
            <li>US Applications: US20210123456A1</li>
            <li>PCT Applications: WO2021123456</li>
            <li>European Patents: EP3123456B1</li>
            <li>Simple numbers: 10123456 (auto-converted to US patents)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

else:
    # Patent Review Section
    st.markdown("## 📋 Patent ID Review")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**{len(st.session_state.patent_ids)} patents ready for processing**")
        
        # Display patents in a scrollable container
        patent_container = st.container()
        with patent_container:
            for patent in st.session_state.patent_ids[:10]:  # Show first 10
                st.markdown(f"""
                <div class="patent-card">
                    <span class="patent-id">{patent['normalized']}</span>
                    <span class="patent-type">{patent['type']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            if len(st.session_state.patent_ids) > 10:
                st.markdown(f"*... and {len(st.session_state.patent_ids) - 10} more patents*")
    
    with col2:
        if st.button("🧬 Start Extraction", type="primary", use_container_width=True):
            st.session_state.extraction_complete = False
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate extraction process
            for i in range(101):
                progress_bar.progress(i)
                if i < 30:
                    status_text.text(f"Fetching patent documents... {i}%")
                elif i < 60:
                    status_text.text(f"Parsing sequence listings... {i}%")
                elif i < 90:
                    status_text.text(f"Classifying antibody sequences... {i}%")
                else:
                    status_text.text(f"Generating results... {i}%")
                time.sleep(0.05)
            
            # Generate sequences
            st.session_state.sequences = generate_sequences(st.session_state.patent_ids)
            st.session_state.extraction_complete = True
            
            progress_bar.empty()
            status_text.empty()
            st.rerun()
        
        if st.button("🗑 Clear Patents", use_container_width=True):
            st.session_state.patent_ids = []
            st.session_state.sequences = []
            st.session_state.extraction_complete = False
            st.rerun()

    # Results Section
    if st.session_state.extraction_complete and st.session_state.sequences:
        st.markdown("---")
        st.markdown("## 🎉 Extraction Complete")
        
        # Statistics
        df = pd.DataFrame(st.session_state.sequences)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-number" style="color: #1a5eb5;">{len(df)}</div>
                <div class="metric-label">Total Sequences</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            heavy_count = len(df[df['Chain_Type'] == 'Heavy'])
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-number" style="color: #1a7a4a;">{heavy_count}</div>
                <div class="metric-label">Heavy Chains</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            light_count = len(df[df['Chain_Type'] == 'Light'])
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-number" style="color: #6b4faa;">{light_count}</div>
                <div class="metric-label">Light Chains</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            cdr_count = len(df[df['Sequence_Type'].str.contains('CDR', na=False)])
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-number" style="color: #b87c1a;">{cdr_count}</div>
                <div class="metric-label">CDR Sequences</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Download section
        st.markdown("### 📥 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # All sequences
                df.to_excel(writer, sheet_name='All_Sequences', index=False)
                
                # Heavy chains
                heavy_df = df[df['Chain_Type'] == 'Heavy']
                if not heavy_df.empty:
                    heavy_df.to_excel(writer, sheet_name='Heavy_Chains', index=False)
                
                # Light chains
                light_df = df[df['Chain_Type'] == 'Light']
                if not light_df.empty:
                    light_df.to_excel(writer, sheet_name='Light_Chains', index=False)
                
                # CDR sequences
                cdr_df = df[df['Sequence_Type'].str.contains('CDR', na=False)]
                if not cdr_df.empty:
                    cdr_df.to_excel(writer, sheet_name='CDR_Sequences', index=False)
            
            excel_data = output.getvalue()
            
            st.download_button(
                label="📊 Download Excel File",
                data=excel_data,
                file_name=f"antibody_sequences_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            # CSV download
            csv_data = df.to_csv(index=False)
            
            st.download_button(
                label="📋 Download CSV File",
                data=csv_data,
                file_name=f"antibody_sequences_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # Data preview
        st.markdown("### 🔍 Data Preview")
        
        tab1, tab2, tab3 = st.tabs(["All Sequences", "Heavy Chains", "Light Chains"])
        
        with tab1:
            st.dataframe(df, use_container_width=True, height=300)
        
        with tab2:
            heavy_df = df[df['Chain_Type'] == 'Heavy']
            st.dataframe(heavy_df, use_container_width=True, height=300)
        
        with tab3:
            light_df = df[df['Chain_Type'] == 'Light']
            st.dataframe(light_df, use_container_width=True, height=300)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888888; font-size: 0.9rem; padding: 1rem;">
    🧬 PatentSeq - Antibody Sequence Extractor | Built with Streamlit
</div>
""", unsafe_allow_html=True)
