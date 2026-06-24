import streamlit as st
import asyncio
from pathlib import Path
from main import red_flag_analyzer


# ============================================================================
# DATA FLOW:
# 1. User uploads .txt or .doc file via Streamlit UI
# 2. File is read and text is extracted
# 3. Text is passed to red_flag_analyzer() from main.py
# 4. red_flag_analyzer() sends text to AI model (Google Gemini)
# 5. AI analyzes and returns RedFlagReport with identified red flags
# 6. Results are displayed in Streamlit UI with severity color-coding
# ============================================================================

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Red Flag Analyzer",
    page_icon="🚩",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚩 Red Flag Analyzer")
st.markdown("Upload a document to identify potential risks and unfair clauses")

# ============================================================================
# SIDEBAR - FILE UPLOAD
# ============================================================================
st.sidebar.header("📄 Upload Document")
st.sidebar.markdown("Supported formats: `.txt`, `.doc`, `.docx`")

# File uploader widget
uploaded_file = st.sidebar.file_uploader(
    "Choose a file",
    type=["txt", "docx"],
    help="Upload your document for analysis"
)

# ============================================================================
# FUNCTION: Extract text from uploaded file
# ============================================================================
def extract_text_from_file(uploaded_file):
    """
    Extract text from uploaded file based on file type.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        str: Extracted text from the file
    """
    file_extension = Path(uploaded_file.name).suffix.lower()
    
    try:
        if file_extension == ".txt":
            # For .txt files, decode directly
            text = uploaded_file.getvalue().decode("utf-8")
            return text
            

        if file_extension == ".docx":
            from docx import Document
            from io import BytesIO
        
            
            # Extract text from document
            doc = Document(BytesIO(uploaded_file.getbuffer()))
            text = "\n".join([para.text for para in doc.paragraphs])
    
            return text
        
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

# ============================================================================
# MAIN APP LOGIC
# ============================================================================
if uploaded_file is not None:
    # Step 1: Extract text from file
    st.sidebar.success(f"✅ File uploaded: {uploaded_file.name}")
    
    with st.spinner("📖 Reading document..."):
        document_text = extract_text_from_file(uploaded_file)
    
    if document_text:
        # Step 2: Display document preview
        st.subheader("📋 Document Preview")
        with st.expander("View full document", expanded=False):
            st.text_area(
                "Document Content",
                value=document_text,
                height=200,
                disabled=True
            )
        
        st.markdown(f"**Document Size:** {len(document_text)} characters")
        st.markdown("---")
        
        # Step 3: Analyze document with red_flag_analyzer
        if st.button("🔍 Analyze for Red Flags", type="primary"):
            st.session_state.show_disclaimer=True

        if st.session_state.get("show_disclaimer",False):
            st.warning(
                "This tool is designed to assist you in identifying potential "
                "risks and red flags in documents. However, it should not be considered legal advice. "
                "**Please consult with a qualified legal professional before making any final decisions.** "
                "This analysis is for awareness purposes only.",
                icon="⚠️")
            
            if st.checkbox("I understand and wish to proceed with the analysis"):
                with st.spinner("🤖 AI is analyzing your document..."):
                    try:
                        # Call the async red_flag_analyzer function
                        # Streamlit runs on the main thread, so we handle async properly
                        result = red_flag_analyzer(document_text)
                        
                        # Step 4: Display results
                        st.success("✅ Analysis complete!")
                        st.markdown("---")
                        
                        # Display document summary
                        st.subheader("📝 Document Summary")
                        st.info(result.document_summary)
                        
                        # Display red flags
                        st.subheader(f"🚩 Red Flags Found: {len(result.red_flags)}")
                        
                        if result.red_flags:
                            # Color mapping for severity levels
                            severity_colors = {
                                "High": "🔴",
                                "Medium": "🟡",
                                "Low": "🟢"
                            }
                            
                            # Display each red flag in a card-like format
                            for idx, flag in enumerate(result.red_flags, 1):
                                # Determine color based on severity
                                if flag.severity == "High":
                                    color = "#ff4444"
                                elif flag.severity == "Medium":
                                    color = "#ffaa00"
                                else:
                                    color = "#44aa44"
                                
                                # Create a container for each red flag
                                with st.container(border=True):
                                    col1, col2 = st.columns([3, 1])
                                    
                                    with col1:
                                        st.markdown(
                                            f"### {severity_colors.get(flag.severity, '❓')} "
                                            f"Red Flag #{idx}"
                                        )
                                    
                                    with col2:
                                        st.markdown(
                                            f"**Severity:** `{flag.severity}`"
                                        )
                                    
                                    st.markdown("**Problem Text:**")
                                    st.code(flag.item, language="text")
                                    
                                    st.markdown("**Why it's a problem:**")
                                    st.write(flag.reason)
                                    st.markdown("---")
                        else:
                            st.success("✨ No red flags found! This document looks good.")
                        
                        st.session_state.show_disclaimer=False
                    
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
                        st.info("Make sure your `.env` file is configured with the API key.")
            
else:
    # Show empty state when no file is uploaded
    st.info("👈 Upload a document in the sidebar to get started!")
    
    # Display example
    with st.expander("ℹ️ Example - What kind of red flags will be detected?"):
        st.markdown("""
        The analyzer looks for:
        - **Unfair clauses** (one-sided terms, hidden conditions)
        - **Hidden fees** (unexpected costs, surprise charges)
        - **High-risk commitments** (unlimited liability, perpetual obligations)
        - **Ambiguous rules** (vague language, unclear definitions)
        - **Legal risks** (arbitration clauses, waived rights)
        """)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown(
    "💡 **Tip:** Use this tool to review contracts, terms of service, and agreements. "
    "Always consult with legal professionals for final decisions."
)
