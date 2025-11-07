import streamlit as st
import tempfile
import os
import json
from pathlib import Path
import time
from src.resume_crew.crew import ResumeCrew
from src.resume_crew.models import JobRequirements, ResumeOptimization, CompanyResearch

# Page config
st.set_page_config(
    page_title="Resume Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #2E86AB;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">📄 AI Resume Optimizer</h1>', unsafe_allow_html=True)
    st.markdown("**Optimize your resume for any job posting using AI-powered analysis**")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📋 Input Requirements")
        
        # API Key input
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Your OpenAI API key for AI analysis"
        )
        
        # Serper API Key input
        serper_api_key = st.text_input(
            "Serper API Key", 
            type="password",
            help="Your Serper API key for web search (company research)"
        )
        
        # Resume upload
        uploaded_resume = st.file_uploader(
            "Upload Resume (PDF)",
            type=['pdf'],
            help="Upload your resume in PDF format"
        )
        
        # Show upload status
        if uploaded_resume is not None:
            st.success(f"✅ Resume uploaded: {uploaded_resume.name}")
        
        # Job details
        job_url = st.text_input(
            "Job Posting URL",
            placeholder="https://company.com/careers/job-id",
            help="Direct link to the job posting"
        )
        
        # Validate URL format
        if job_url and not job_url.startswith(('http://', 'https://')):
            st.warning("⚠️ Please enter a valid URL starting with http:// or https://")
        
        company_name = st.text_input(
            "Company Name",
            placeholder="e.g., Google, Microsoft, etc.",
            help="Name of the company you're applying to"
        )
        
        # Validation
        inputs_valid = all([
            openai_api_key,
            serper_api_key, 
            uploaded_resume,
            job_url,
            company_name
        ])
        
        if inputs_valid:
            st.success("✅ All inputs provided!")
        else:
            st.warning("⚠️ Please fill all required fields")
        
        # Add a reset button for troubleshooting
        st.markdown("---")
        if st.button("🔄 Clear Cache & Reset", help="Use this if you encounter errors"):
            cleanup_previous_files()
            cleanup_output_files() 
            cleanup_crewai_cache()
            st.success("✅ Cache cleared! Try running the analysis again.")
    
    # Main content area
    if inputs_valid:
        # Initialize session state
        if 'processing' not in st.session_state:
            st.session_state.processing = False
        
        # Disable button during processing
        button_disabled = st.session_state.processing
        button_text = "⏳ Processing..." if button_disabled else "🚀 Optimize Resume"
        
        if st.button(button_text, type="primary", use_container_width=True, disabled=button_disabled):
            st.session_state.processing = True
            try:
                optimize_resume(openai_api_key, serper_api_key, uploaded_resume, job_url, company_name)
            finally:
                st.session_state.processing = False
    else:
        st.info("👈 Please provide all required inputs in the sidebar to get started")
        
        # Show feature overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🎯 Job Analysis
            - Extract job requirements
            - Identify key skills needed
            - Analyze company culture
            """)
            
        with col2:
            st.markdown("""
            ### 📊 Resume Scoring  
            - Calculate match percentage
            - Score technical & soft skills
            - Identify strengths & gaps
            """)
            
        with col3:
            st.markdown("""
            ### ✨ Optimization
            - Suggest specific improvements
            - ATS keyword optimization
            - Generate optimized resume
            """)

def cleanup_previous_files(exclude_file=None):
    """Clean up any previous uploaded resume files to prevent duplicates"""
    knowledge_dir = 'knowledge'
    if os.path.exists(knowledge_dir):
        for filename in os.listdir(knowledge_dir):
            if filename.startswith('uploaded_resume_') and filename.endswith('.pdf'):
                # Don't delete the file we just created
                if exclude_file and filename == exclude_file:
                    continue
                file_path = os.path.join(knowledge_dir, filename)
                try:
                    os.unlink(file_path)
                except OSError:
                    pass  # File might be in use, ignore

def cleanup_crewai_cache():
    """Clean up CrewAI cache and temporary files - AGGRESSIVE MODE"""
    import shutil
    import glob
    
    # All possible cache and database locations
    cache_dirs = [
        '.crewai',
        '__pycache__',
        '.chroma',              # ChromaDB vector database - THIS IS KEY!
        'chroma_db',            # Alternative ChromaDB location
        'src/__pycache__',
        'src/resume_crew/__pycache__',
        '.streamlit/cache',
        '.cache'
    ]
    
    # Also find any .db files (SQLite databases used by ChromaDB)
    db_files = glob.glob('**/*.db', recursive=True)
    db_files.extend(glob.glob('**/*.sqlite', recursive=True))
    db_files.extend(glob.glob('**/*.sqlite3', recursive=True))
    
    cleaned = []
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                cleaned.append(cache_dir)
            except OSError as e:
                pass  # Directory might be in use, ignore
    
    # Remove database files
    for db_file in db_files:
        if 'venv' not in db_file and '.venv' not in db_file:  # Don't delete venv files
            try:
                os.remove(db_file)
                cleaned.append(db_file)
            except OSError:
                pass
    
    if cleaned:
        print(f"🧹 Cleaned {len(cleaned)} cache locations")
    
    return len(cleaned)

def cleanup_output_files():
    """Clean up previous output files to ensure fresh results"""
    output_dir = 'output'
    if os.path.exists(output_dir):
        output_files = [
            'job_analysis.json',
            'resume_optimization.json', 
            'company_research.json',
            'optimized_resume.md',
            'final_report.md'
        ]
        for filename in output_files:
            file_path = os.path.join(output_dir, filename)
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except OSError:
                    pass

def optimize_resume(openai_api_key, serper_api_key, uploaded_resume, job_url, company_name):
    """Run the resume optimization process"""
    
    # Set environment variables
    os.environ['OPENAI_API_KEY'] = openai_api_key
    os.environ['SERPER_API_KEY'] = serper_api_key
    
    # Create progress bar and status
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    # Create results container
    results_container = st.container()
    
    # Store original working directory
    original_cwd = os.getcwd()
    
    try:
        # FIRST: Clean vector database BEFORE doing anything
        status_text.text("🗑️ Clearing vector database from previous runs...")
        cleaned = cleanup_crewai_cache()
        if cleaned > 0:
            st.info(f"✅ Cleared {cleaned} cache locations to prevent duplicate ID errors")
        
        # Ensure directories exist
        os.makedirs('knowledge', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        
        # Create unique filename using timestamp and hash
        import hashlib
        file_hash = hashlib.md5(uploaded_resume.getvalue()).hexdigest()[:8]
        resume_filename = f"uploaded_resume_{int(time.time())}_{file_hash}.pdf"
        resume_path = os.path.join('knowledge', resume_filename)
        
        status_text.text("📄 Saving uploaded resume...")
        
        try:
            # Get file content safely
            file_content = uploaded_resume.getvalue()
            if not file_content:
                raise ValueError("Uploaded file is empty")
            
            # Show what we're doing
            st.info(f"💾 Saving to: {resume_path}")
            
            # Save the file FIRST
            with open(resume_path, 'wb') as f:
                bytes_written = f.write(file_content)
            
            # Verify file exists and has content
            if not os.path.exists(resume_path):
                raise FileNotFoundError(f"Failed to save resume to {resume_path}")
            
            file_size = os.path.getsize(resume_path)
            if file_size == 0:
                raise ValueError("Saved file is empty")
            
            # Show absolute path for debugging
            abs_path = os.path.abspath(resume_path)
            st.success(f"✅ Resume saved successfully!")
            st.write(f"📍 Location: {abs_path}")
            st.write(f"📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Verify we can read it back
            with open(resume_path, 'rb') as f:
                verify_content = f.read()
            if len(verify_content) != file_size:
                raise ValueError("File verification failed - size mismatch")
            
            st.success("✅ File verified and ready for processing")
            
        except Exception as save_error:
            st.error(f"❌ Failed to save resume: {save_error}")
            st.error(f"Working directory: {os.getcwd()}")
            st.error(f"Attempted path: {resume_path}")
            raise
        
        # Clean up old files (excluding the one we just saved)
        status_text.text("🧹 Cleaning up old uploaded files...")
        cleanup_previous_files(exclude_file=resume_filename)
        cleanup_output_files()
        
        status_text.text("📄 Processing uploaded resume...")
        progress_bar.progress(20)
        time.sleep(0.5)
        
        # Initialize crew with uploaded resume (use just filename)
        status_text.text("🤖 Initializing AI crew...")
        
        # Verify file still exists before crew initialization
        if not os.path.exists(resume_path):
            raise FileNotFoundError(f"Resume file disappeared: {resume_path}")
        
        try:
            crew_instance = ResumeCrew(resume_path=resume_filename)
            st.success("✅ AI crew initialized successfully")
        except Exception as init_error:
            st.error(f"Failed to initialize AI crew: {init_error}")
            st.error("This might be a file path issue. Please try again.")
            raise
        
        status_text.text("🔍 Analyzing job posting...")
        progress_bar.progress(40)
        time.sleep(0.5)
        
        # Prepare inputs
        inputs = {
            'job_url': job_url,
            'company_name': company_name
        }
        
        status_text.text("🤖 Running AI analysis (this may take 2-3 minutes)...")
        progress_bar.progress(60)
        
        # Run the crew with error handling for knowledge base issues
        with st.spinner("AI agents are working..."):
            try:
                result = crew_instance.crew().kickoff(inputs=inputs)
            except Exception as crew_error:
                error_msg = str(crew_error).lower()
                if "duplicate" in error_msg or "upsert" in error_msg or "unique" in error_msg:
                    st.error("❌ Vector database conflict detected!")
                    st.error("This happens when ChromaDB has cached data from a previous run.")
                    st.error("Please stop the app (Ctrl+C) and run: python start_fresh.py")
                    st.info("💡 The issue: ChromaDB keeps data in memory even after cleanup.")
                    st.info("💡 The fix: Restart the app completely to clear memory.")
                    raise crew_error
                else:
                    raise crew_error
        
        status_text.text("📊 Generating results...")
        progress_bar.progress(80)
        time.sleep(0.5)
        
        # Display results in the results container
        with results_container:
            display_results()
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        # Success message
        st.balloons()
        st.success("🎉 Resume optimization completed successfully!")
        
        # Keep the file for now (don't delete immediately)
        # User can manually clean up later if needed
        st.info(f"📁 Resume file saved at: {resume_path}")
        # if os.path.exists(resume_path):
        #     os.unlink(resume_path)
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        st.error("Please check your API keys and try again.")
        
        # Keep the file even on error so user can debug
        if 'resume_path' in locals() and os.path.exists(resume_path):
            st.info(f"📁 Resume file preserved at: {resume_path}")
        
        progress_bar.empty()
        status_text.empty()
    
    finally:
        # Always restore original working directory
        os.chdir(original_cwd)

def display_results():
    """Display the analysis results"""
    
    st.markdown('<h2 class="section-header">📊 Analysis Results</h2>', unsafe_allow_html=True)
    
    # Check if output directory exists
    if not os.path.exists('output'):
        st.warning("⚠️ No results found. The analysis may not have completed successfully.")
        return
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Job Match", "✨ Optimization", "🏢 Company Intel", 
        "📋 Summary", "📄 New Resume"
    ])
    
    try:
        # Job Analysis Tab
        with tab1:
            if os.path.exists('output/job_analysis.json'):
                with open('output/job_analysis.json', 'r', encoding='utf-8') as f:
                    job_analysis = json.load(f)
                display_job_analysis(job_analysis)
            else:
                st.info("Job analysis results not available.")
        
        # Resume Optimization Tab
        with tab2:
            if os.path.exists('output/resume_optimization.json'):
                with open('output/resume_optimization.json', 'r', encoding='utf-8') as f:
                    resume_opt = json.load(f)
                display_resume_optimization(resume_opt)
            else:
                st.info("Resume optimization results not available.")
        
        # Company Research Tab
        with tab3:
            if os.path.exists('output/company_research.json'):
                with open('output/company_research.json', 'r', encoding='utf-8') as f:
                    company_research = json.load(f)
                display_company_research(company_research)
            else:
                st.info("Company research results not available.")
        
        # Final Report Tab
        with tab4:
            if os.path.exists('output/final_report.md'):
                with open('output/final_report.md', 'r', encoding='utf-8') as f:
                    final_report = f.read()
                display_final_report(final_report)
            else:
                st.info("Final report not available.")
        
        # Optimized Resume Tab
        with tab5:
            if os.path.exists('output/optimized_resume.md'):
                with open('output/optimized_resume.md', 'r', encoding='utf-8') as f:
                    optimized_resume = f.read()
                display_optimized_resume(optimized_resume)
            else:
                st.info("Optimized resume not available.")
                
    except Exception as e:
        st.error(f"Error loading results: {str(e)}")
        st.error("Please try running the analysis again.")

def display_job_analysis(job_analysis):
    """Display job analysis results"""
    
    st.subheader("🎯 Job Match Analysis")
    
    # Overall match score
    if 'match_score' in job_analysis:
        match_score = job_analysis['match_score']
        overall_match = match_score.get('overall_match', 0)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Overall Match", f"{overall_match:.0f}%")
        with col2:
            st.metric("Technical Skills", f"{match_score.get('technical_skills_match', 0):.0f}%")
        with col3:
            st.metric("Experience", f"{match_score.get('experience_match', 0):.0f}%")
        with col4:
            st.metric("Education", f"{match_score.get('education_match', 0):.0f}%")
    
    # Job requirements
    col1, col2 = st.columns(2)
    
    with col1:
        if job_analysis.get('technical_skills'):
            st.write("**Technical Skills Required:**")
            for skill in job_analysis['technical_skills']:
                st.write(f"• {skill}")
    
    with col2:
        if job_analysis.get('soft_skills'):
            st.write("**Soft Skills Required:**")
            for skill in job_analysis['soft_skills']:
                st.write(f"• {skill}")

def display_resume_optimization(resume_opt):
    """Display resume optimization suggestions"""
    
    st.subheader("✨ Resume Optimization Suggestions")
    
    # Content suggestions
    if resume_opt.get('content_suggestions'):
        st.write("**Content Improvements:**")
        for suggestion in resume_opt['content_suggestions']:
            with st.expander(f"📝 {suggestion.get('section', 'Section')}"):
                st.write("**Before:**")
                st.write(suggestion.get('before', ''))
                st.write("**After:**")
                st.write(suggestion.get('after', ''))
                if 'rationale' in suggestion:
                    st.write("**Why:**")
                    st.write(suggestion['rationale'])
    
    # Skills to highlight
    col1, col2 = st.columns(2)
    
    with col1:
        if resume_opt.get('skills_to_highlight'):
            st.write("**Skills to Highlight:**")
            for skill in resume_opt['skills_to_highlight']:
                st.write(f"• {skill}")
    
    with col2:
        if resume_opt.get('keywords_for_ats'):
            st.write("**ATS Keywords:**")
            for keyword in resume_opt['keywords_for_ats']:
                st.write(f"• {keyword}")

def display_company_research(company_research):
    """Display company research results"""
    
    st.subheader("🏢 Company Intelligence")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if company_research.get('recent_developments'):
            st.write("**Recent Developments:**")
            for dev in company_research['recent_developments']:
                st.write(f"• {dev}")
    
    with col2:
        if company_research.get('culture_and_values'):
            st.write("**Culture & Values:**")
            for value in company_research['culture_and_values']:
                st.write(f"• {value}")
    
    if company_research.get('interview_questions'):
        st.write("**Strategic Interview Questions:**")
        for question in company_research['interview_questions']:
            st.write(f"• {question}")

def display_final_report(final_report):
    """Display the final report"""
    
    st.subheader("📋 Executive Summary")
    st.markdown(final_report)

def display_optimized_resume(optimized_resume):
    """Display the optimized resume with download option"""
    
    st.subheader("📄 Your Optimized Resume")
    
    # Download button
    st.download_button(
        label="📥 Download Optimized Resume",
        data=optimized_resume,
        file_name="optimized_resume.md",
        mime="text/markdown"
    )
    
    # Display preview
    with st.expander("👀 Preview Optimized Resume"):
        st.markdown(optimized_resume)

if __name__ == "__main__":
    main()