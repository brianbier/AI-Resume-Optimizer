import streamlit as st
import tempfile
import os
import json
from pathlib import Path
import time
from src.resume_crew.crew import ResumeCrew
from src.resume_crew.models import JobRequirements, ResumeOptimization, CompanyResearch

# Note: Removed load_dotenv() to force users to enter their own API keys
# This prevents using deployed secrets and ensures each user provides their own keys

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

    # FORCE ChromaDB cleanup on every app startup
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = True
        # Clean vector database immediately on startup (silent)
        cleanup_crewai_cache()

    # Initialize session state for tracking processed resumes
    if 'processed_resume_hash' not in st.session_state:
        st.session_state.processed_resume_hash = None
    if 'analysis_count' not in st.session_state:
        st.session_state.analysis_count = 0
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📋 Input Requirements")
        
        # Note: No longer checking for environment variables to force manual key entry
        # This ensures each user must provide their own API keys
        st.info("🔑 Please enter your API keys below to get started")
        
        # API Key inputs - now required for each session
        openai_api_key = st.text_input(
            "OpenAI API Key (Required)",
            type="password",
            value="",
            help="Your OpenAI API key for AI analysis. Required for each session.",
            placeholder="sk-..."
        )

        serper_api_key = st.text_input(
            "Serper API Key (Required)",
            type="password",
            value="",
            help="Your Serper API key for web search. Required for each session.",
            placeholder="..."
        )

        # Use only the manually entered keys
        final_openai_key = openai_api_key
        final_serper_key = serper_api_key
        
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
        
        # Validation - check final resolved keys, not UI inputs
        inputs_valid = all([
            final_openai_key,  # Check resolved key (UI or env)
            final_serper_key,  # Check resolved key (UI or env)
            uploaded_resume,
            job_url,
            company_name
        ])
        
        if inputs_valid:
            st.success("✅ All inputs provided!")
        else:
            # Show which fields are missing
            missing = []
            if not final_openai_key:
                missing.append("OpenAI API Key")
            if not final_serper_key:
                missing.append("Serper API Key")
            if not uploaded_resume:
                missing.append("Resume PDF")
            if not job_url:
                missing.append("Job URL")
            if not company_name:
                missing.append("Company Name")
            
            st.warning(f"⚠️ Missing: {', '.join(missing)}")
        
        # Add reset buttons for troubleshooting
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Clear Cache", help="Clear all cache and temporary files"):
                cleanup_previous_files()
                cleanup_output_files()
                cleanup_crewai_cache()
                st.success("Cache cleared!")

        with col2:
            if st.button("🧹 Clear Results", help="Hide current results from display"):
                st.session_state.results_available = False
                st.success("Results cleared!")
    
    # Main content area
    if inputs_valid:
        # Initialize session state
        if 'processing' not in st.session_state:
            st.session_state.processing = False
        if 'results_available' not in st.session_state:
            st.session_state.results_available = False

        # Disable button during processing
        button_disabled = st.session_state.processing
        button_text = "⏳ Processing..." if button_disabled else "🚀 Optimize Resume"

        if st.button(button_text, type="primary", use_container_width=True, disabled=button_disabled):
            st.session_state.processing = True
            st.session_state.results_available = False  # Reset results
            try:
                optimize_resume(final_openai_key, final_serper_key, uploaded_resume, job_url, company_name)
                st.session_state.results_available = True  # Set results available after successful completion
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.session_state.results_available = False
            finally:
                st.session_state.processing = False

    # Display results if available (separate from the button logic)
    if st.session_state.get('results_available', False):
        # Check if output files actually exist
        if os.path.exists('output') and any(os.path.exists(f'output/{f}') for f in
            ['job_analysis.json', 'resume_optimization.json', 'company_research.json', 'optimized_resume.md', 'final_report.md']):
            display_results()
        else:
            st.session_state.results_available = False  # Reset if files don't exist
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
    """Clean up CrewAI cache and temporary files - ULTRA AGGRESSIVE MODE"""
    import shutil
    import glob
    import gc
    import sys

    # All possible cache and database locations
    cache_dirs = [
        '.crewai',
        '__pycache__',
        '.chroma',              # ChromaDB vector database - THIS IS KEY!
        'chroma_db',            # Alternative ChromaDB location
        'chromadb',             # Another possible location
        'src/__pycache__',
        'src/resume_crew/__pycache__',
        '.streamlit/cache',
        '.cache',
        'knowledge/.chroma',    # ChromaDB might create here
        'output/.chroma'        # Or here
    ]

    # Find ALL database and vector store files
    db_patterns = [
        '**/*.db', '**/*.sqlite', '**/*.sqlite3',
        '**/*.parquet',  # ChromaDB uses parquet files
        '**/*.pkl', '**/*.pickle',  # Potential pickle caches
        '**/chroma-*'  # ChromaDB temp files
    ]

    db_files = []
    for pattern in db_patterns:
        db_files.extend(glob.glob(pattern, recursive=True))

    cleaned = []

    # Clear Python module caches related to ChromaDB/CrewAI
    modules_to_clear = [name for name in sys.modules.keys()
                       if any(keyword in name.lower() for keyword in
                             ['chroma', 'crewai', 'knowledge', 'vector'])]

    for module_name in modules_to_clear:
        if module_name in sys.modules:
            try:
                del sys.modules[module_name]
                cleaned.append(f"module:{module_name}")
            except:
                pass

    # Remove cache directories
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                cleaned.append(cache_dir)
            except OSError as e:
                # Try individual file deletion if directory deletion fails
                try:
                    for root, dirs, files in os.walk(cache_dir):
                        for file in files:
                            try:
                                os.remove(os.path.join(root, file))
                            except:
                                pass
                    shutil.rmtree(cache_dir)
                    cleaned.append(f"{cache_dir}(forced)")
                except:
                    pass

    # Remove database files
    for db_file in db_files:
        if 'venv' not in db_file and '.venv' not in db_file:  # Don't delete venv files
            try:
                os.remove(db_file)
                cleaned.append(db_file)
            except OSError:
                pass

    # Force multiple garbage collections with different strategies
    for _ in range(3):
        gc.collect()

    # Clear any lingering ChromaDB client instances
    try:
        import chromadb
        # Force close any existing clients
        if hasattr(chromadb, '_clients'):
            chromadb._clients.clear()
    except:
        pass

    if cleaned:
        print(f"🧹 Cleaned {len(cleaned)} cache locations and modules")

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
        cleanup_crewai_cache()
        
        # Ensure directories exist
        os.makedirs('knowledge', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        
        # Create unique filename using timestamp and hash
        import hashlib
        file_hash = hashlib.md5(uploaded_resume.getvalue()).hexdigest()[:8]

        # With aggressive cleanup, we can now handle different resumes
        resume_filename = f"uploaded_resume_{int(time.time())}_{file_hash}.pdf"
        resume_path = os.path.join('knowledge', resume_filename)

        # Store the hash for tracking (but don't block different resumes)
        st.session_state.processed_resume_hash = file_hash
        st.session_state.analysis_count += 1
        
        status_text.text("📄 Saving uploaded resume...")
        
        try:
            # Get file content safely
            file_content = uploaded_resume.getvalue()
            if not file_content:
                raise ValueError("Uploaded file is empty")
            
            # Save the file
            with open(resume_path, 'wb') as f:
                f.write(file_content)

            # Verify file exists and has content
            if not os.path.exists(resume_path):
                raise FileNotFoundError(f"Failed to save resume to {resume_path}")

            file_size = os.path.getsize(resume_path)
            if file_size == 0:
                raise ValueError("Saved file is empty")
            
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
            # Force Python garbage collection to clear any cached objects
            import gc
            gc.collect()

            # Create a completely new crew instance
            crew_instance = ResumeCrew(resume_path=resume_filename)
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

        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")

        # Success message
        st.balloons()
        st.success("🎉 Resume optimization completed successfully!")

        # Clear the progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Show what user can do next
        st.markdown("---")
        st.markdown("### 🎯 What's Next?")
        
        col1, col2 = st.columns(2)

        with col1:
            st.success("✅ **Same Resume, Different Job?**")
            st.write("Just change the job URL and company name above, then click 'Optimize Resume' again!")
            st.write("No restart needed! 🚀")

        with col2:
            st.success("✅ **Different Resume?**")
            st.write("Upload a new resume and analyze directly!")
            st.write("Auto-cleanup enabled - no restart needed! 🎉")
            st.write("Vector database clears automatically.")
        
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
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Summary", "✨ Optimization",
        "📄 New Resume", "🏢 Company Insights"
    ])

    try:
        # Tab 1: Summary (Final Report)
        with tab1:
            if os.path.exists('output/final_report.md'):
                with open('output/final_report.md', 'r', encoding='utf-8') as f:
                    final_report = f.read()
                display_final_report(final_report)
            else:
                st.info("Final report not available.")
        
        # Tab 2: Optimization Suggestions
        with tab2:
            if os.path.exists('output/resume_optimization.json'):
                with open('output/resume_optimization.json', 'r', encoding='utf-8') as f:
                    resume_opt = json.load(f)
                display_resume_optimization(resume_opt)
            else:
                st.info("Resume optimization results not available.")

        # Tab 3: New Resume
        with tab3:
            if os.path.exists('output/optimized_resume.md'):
                with open('output/optimized_resume.md', 'r', encoding='utf-8') as f:
                    optimized_resume = f.read()
                display_optimized_resume(optimized_resume)
            else:
                st.info("Optimized resume not available.")

        # Tab 4: Company Insights
        with tab4:
            if os.path.exists('output/company_research.json'):
                with open('output/company_research.json', 'r', encoding='utf-8') as f:
                    company_research = json.load(f)
                display_company_research(company_research)
            else:
                st.info("Company research results not available.")
                
    except Exception as e:
        st.error(f"Error loading results: {str(e)}")
        st.error("Please try running the analysis again.")

def display_job_analysis(job_analysis):
    """Display job analysis results"""
    
    st.subheader("🎯 Job Match Analysis")
    
    # Job Title and Basic Info
    if job_analysis.get('job_title'):
        st.markdown(f"### {job_analysis['job_title']}")
        
        info_cols = st.columns(3)
        with info_cols[0]:
            if job_analysis.get('job_level'):
                st.write(f"**Level:** {job_analysis['job_level']}")
        with info_cols[1]:
            if job_analysis.get('location_requirements'):
                loc = job_analysis['location_requirements']
                if isinstance(loc, dict):
                    location = loc.get('city', 'Not specified')
                    st.write(f"**Location:** {location}")
        with info_cols[2]:
            if job_analysis.get('compensation'):
                comp = job_analysis['compensation']
                if isinstance(comp, dict) and comp.get('base_salary'):
                    st.write(f"**Salary:** {comp['base_salary']}")
        
        st.markdown("---")
    
    # Overall match score with visual indicator
    if 'match_score' in job_analysis:
        match_score = job_analysis['match_score']
        overall_match = match_score.get('overall_match', 0)  # Already in percentage format
        
        # Visual match indicator
        if overall_match >= 80:
            match_emoji = "🟢 Excellent Match"
            match_color = "green"
        elif overall_match >= 60:
            match_emoji = "🟡 Good Match"
            match_color = "orange"
        else:
            match_emoji = "🔴 Needs Improvement"
            match_color = "red"
        
        st.markdown(f"### {match_emoji}")
        
        # Score metrics - values are already percentages
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Overall Match", f"{overall_match:.1f}%")
        with col2:
            tech_score = match_score.get('technical_skills_match', 0)
            st.metric("Technical Skills", f"{tech_score:.1f}%")
        with col3:
            exp_score = match_score.get('experience_match', 0)
            st.metric("Experience", f"{exp_score:.1f}%")
        with col4:
            edu_score = match_score.get('education_match', 0)
            st.metric("Education", f"{edu_score:.1f}%")
        with col5:
            ind_score = match_score.get('industry_match', 0)
            st.metric("Industry", f"{ind_score:.1f}%")
        
        st.markdown("---")
        
        # Strengths and Gaps
        col1, col2 = st.columns(2)
        
        with col1:
            if match_score.get('strengths'):
                st.markdown("### ✅ Your Strengths")
                for strength in match_score['strengths']:
                    st.success(f"✓ {strength}")
        
        with col2:
            if match_score.get('gaps'):
                st.markdown("### ⚠️ Areas to Address")
                for gap in match_score['gaps']:
                    st.warning(f"• {gap}")
        
        st.markdown("---")
    
    # Job requirements in expandable sections
    with st.expander("📋 Technical Skills Required", expanded=False):
        if job_analysis.get('technical_skills'):
            skills_per_row = 3
            skills = job_analysis['technical_skills']
            for i in range(0, len(skills), skills_per_row):
                cols = st.columns(skills_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(skills):
                        col.write(f"• {skills[i + j]}")
        else:
            st.info("No technical skills specified")
    
    with st.expander("💬 Soft Skills Required", expanded=False):
        if job_analysis.get('soft_skills'):
            for skill in job_analysis['soft_skills']:
                st.write(f"• {skill}")
        else:
            st.info("No soft skills specified")
    
    with st.expander("🎯 Key Responsibilities", expanded=False):
        if job_analysis.get('key_responsibilities'):
            for i, resp in enumerate(job_analysis['key_responsibilities'], 1):
                st.write(f"{i}. {resp}")
        else:
            st.info("No responsibilities specified")
    
    with st.expander("🎓 Education & Experience Requirements", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Education:**")
            if job_analysis.get('education_requirements'):
                for req in job_analysis['education_requirements']:
                    st.write(f"• {req}")
            else:
                st.info("Not specified")
        
        with col2:
            st.write("**Experience:**")
            if job_analysis.get('experience_requirements'):
                for req in job_analysis['experience_requirements']:
                    st.write(f"• {req}")
            else:
                st.info("Not specified")

def display_resume_optimization(resume_opt):
    """Display resume optimization suggestions"""
    
    st.subheader("✨ Resume Optimization Suggestions")
    
    # Content suggestions
    if resume_opt.get('content_suggestions'):
        st.write("**Content Improvements:**")
        for i, suggestion in enumerate(resume_opt['content_suggestions'], 1):
            # Handle multiple JSON structures
            if isinstance(suggestion, dict):
                if 'suggestion' in suggestion:
                    # Current structure: just has 'suggestion' field
                    with st.expander(f"📝 Suggestion {i}: {suggestion.get('section', 'General Improvement')}"):
                        st.write(suggestion['suggestion'])
                        if 'original_text' in suggestion:
                            st.write("**Original Text:**")
                            st.code(suggestion['original_text'])
                elif 'before' in suggestion or 'after' in suggestion:
                    # Old structure with before/after
                    with st.expander(f"📝 {suggestion.get('section', f'Suggestion {i}')}"):
                        if 'before' in suggestion:
                            st.write("**Before:**")
                            st.write(suggestion.get('before', ''))
                        if 'after' in suggestion:
                            st.write("**After:**")
                            st.write(suggestion.get('after', ''))
                        if 'rationale' in suggestion:
                            st.write("**Why:**")
                            st.write(suggestion['rationale'])
                else:
                    # Fallback: display whatever content is available
                    with st.expander(f"📝 Suggestion {i}"):
                        for key, value in suggestion.items():
                            if key != 'section':
                                st.write(f"**{key.title()}:** {value}")
            else:
                # If suggestion is just a string
                with st.expander(f"📝 Suggestion {i}"):
                    st.write(suggestion)
    
    # Additional suggestions in grid layout
    col1, col2 = st.columns(2)

    with col1:
        if resume_opt.get('skills_to_highlight'):
            st.write("**Skills to Highlight:**")
            for skill in resume_opt['skills_to_highlight']:
                st.write(f"• {skill}")

        if resume_opt.get('achievements_to_add'):
            st.write("**Achievements to Add:**")
            for achievement in resume_opt['achievements_to_add']:
                st.write(f"• {achievement}")

    with col2:
        if resume_opt.get('keywords_for_ats'):
            st.write("**ATS Keywords:**")
            for keyword in resume_opt['keywords_for_ats']:
                st.write(f"• {keyword}")

        if resume_opt.get('formatting_suggestions'):
            st.write("**Formatting Improvements:**")
            for formatting in resume_opt['formatting_suggestions']:
                st.write(f"• {formatting}")

def display_company_research(company_research):
    """Display company research results"""
    
    st.subheader("🏢 Company Insights")
    
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
    
    # Download button with unique key to prevent page reset
    import time
    unique_key = f"download_resume_{int(time.time())}"
    st.download_button(
        label="📥 Download Optimized Resume",
        data=optimized_resume,
        file_name="optimized_resume.md",
        mime="text/markdown",
        key=unique_key,
        help="Download your optimized resume in Markdown format"
    )
    
    st.info("💡 Tip: You can convert this Markdown file to PDF using online tools or Markdown editors")
    
    # Display preview
    with st.expander("👀 Preview Optimized Resume", expanded=True):
        st.markdown(optimized_resume)

if __name__ == "__main__":
    main()