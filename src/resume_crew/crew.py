import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from .models import (
    JobRequirements,
    ResumeOptimization,
    CompanyResearch
)


@CrewBase
class ResumeCrew():
    """ResumeCrew for resume optimization and interview preparation"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, resume_path=None) -> None:
        """Initialize with resume PDF path"""
        if resume_path:
            # Ensure we're working from the correct directory
            import os
            current_dir = os.getcwd()
            
            # Verify the file exists before creating PDFKnowledgeSource
            full_path = os.path.join('knowledge', resume_path) if not os.path.sep in resume_path else resume_path
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"Resume file not found: {full_path}")
            
            # If resume_path is just a filename, it should be in knowledge/
            if not os.path.sep in resume_path:
                # It's just a filename, PDFKnowledgeSource will look in knowledge/
                print(f"[ResumeCrew] Loading resume: {resume_path}")
                self.resume_pdf = PDFKnowledgeSource(file_paths=resume_path)
            else:
                # It's a full path, use it directly
                print(f"[ResumeCrew] Loading resume from full path: {resume_path}")
                self.resume_pdf = PDFKnowledgeSource(file_paths=resume_path)
        # else:
        #     # Fallback - find uploaded resume files first, then any PDF
        #     import os
        #     if os.path.exists("knowledge"):
        #         # Prioritize uploaded resume files
        #         pdf_files = [f for f in os.listdir("knowledge") 
        #                    if f.endswith('.pdf') and not f.startswith('.')]
                
        #         # Sort to get uploaded_resume files first
        #         uploaded_files = [f for f in pdf_files if f.startswith('uploaded_resume_')]
        #         other_files = [f for f in pdf_files if not f.startswith('uploaded_resume_')]
                
        #         pdf_files = uploaded_files + other_files
                
        #         if pdf_files:
        #             # Use the first PDF found (prioritizing uploaded ones)
        #             print(f"[ResumeCrew] No resume_path provided, using: {pdf_files[0]}")
        #             self.resume_pdf = PDFKnowledgeSource(file_paths=pdf_files[0])
        #         else:
        #             raise FileNotFoundError("No PDF files found in knowledge directory")
        #     else:
        #         raise FileNotFoundError("Knowledge directory not found and no resume_path provided")

    @agent
    def resume_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_analyzer'],
            verbose=True,
            llm=LLM("gpt-4o"),  # Better for analysis and structured output
            allow_delegation=False
            # Knowledge sources added at crew level to avoid duplicates
        )
    
    @agent
    def job_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['job_analyzer'],
            verbose=True,
            tools=[ScrapeWebsiteTool()],
            llm=LLM("gpt-4o"),  # Better for web scraping and analysis
            allow_delegation=False
        )

    @agent
    def company_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['company_researcher'],
            verbose=True,
            tools=[SerperDevTool()],
            llm=LLM("gpt-4o"),  # Better for research and synthesis
            allow_delegation=False
            # Knowledge sources added at crew level to avoid duplicates
        )

    @agent
    def resume_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_writer'],
            verbose=True,
            llm=LLM("gpt-4o"),  # Better for creative writing
            allow_delegation=False
        )

    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'],
            verbose=True,
            llm=LLM("gpt-4o"),  # Better for formatting and synthesis
            allow_delegation=False
        )

    @task
    def analyze_job_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_job_task'],
            output_file='output/job_analysis.json',
            output_pydantic=JobRequirements
        )

    @task
    def optimize_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['optimize_resume_task'],
            output_file='output/resume_optimization.json',
            output_pydantic=ResumeOptimization
        )

    @task
    def research_company_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_company_task'],
            output_file='output/company_research.json',  
            output_pydantic=CompanyResearch
        )

    @task
    def generate_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_resume_task'],
            output_file='output/optimized_resume.md'
        )

    @task
    def generate_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_report_task'],
            output_file='output/final_report.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential,
            knowledge_sources=[self.resume_pdf]
        )
