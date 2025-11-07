#!/usr/bin/env python
import sys
import warnings

from resume_crew.crew import ResumeCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run(job_url=None, company_name=None, resume_path=None):
    """
    Run the resume optimization crew.
    """
    # Default values for testing
    if not job_url:
        job_url = 'https://www.mckinsey.com/careers/search-jobs/jobs/associate-15178'
    if not company_name:
        company_name = 'Mckinsey & Co.'
    
    inputs = {
        'job_url': job_url,
        'company_name': company_name
    }
    
    # Initialize crew with optional resume path
    crew_instance = ResumeCrew(resume_path=resume_path)
    crew_instance.crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()
