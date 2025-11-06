# Resume Optimization with CrewAI

![Resume Optimization System Architecture](docs/architecture-diagam.svg)

An AI-powered tool that optimizes your resume for specific job applications using multiple AI agents. Built with [CrewAI](https://crewai.com).

## What It Does

1. **Job Analysis**: Analyzes job requirements, skills, and qualifications
2. **Resume Scoring**: Calculates match scores for technical skills, experience, and qualifications
3. **Optimization**: Suggests specific improvements to increase your match score
4. **Company Research**: Provides company insights for interview preparation

## Installation

1. Clone the repository and install dependencies:

    ```bash
    git clone https://github.com/tonykipkemboi/resume-optimization-crew.git
    cd resume-optimization-crew
    ```

2. Create a virtual environment and install dependencies:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    crewai install
    ```

## Environment Setup

1. Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```

2. Add your API keys to `.env`:
    - Required:
        - `OPENAI_API_KEY`: OpenAI API key
        - `SERPER_API_KEY`: Serper API key for web search
    - Optional:
        - See `.env.example` for additional optional APIs

## Quick Start

1. Save your resume as PDF in the project root under the `knowledge/` directory:
    - Feel free to use the sample resume provided in `knowledge/knowledge/CV_Mohan.pdf`
    - I got it from [here](https://www.hbs.edu/doctoral/Documents/job-market/CV_Mohan.pdf)

2. Fill in the input data in `main.py`:
    - `job_url`: URL of the job posting (e.g., 'https://www.mckinsey.com/careers/search-jobs/jobs/associate-15178')
    - `company_name`: Name of the company (e.g., 'Mckinsey & Co.')

3. Run the optimization crew:
    ```bash
    crewai run
    ```

## Output Files

The tool generates three JSON files in the `output` directory:

- `job_analysis.json`: Detailed job requirements and match scoring
- `resume_optimization.json`: Specific suggestions to improve your resume
- `company_research.json`: Company insights for interview prep

## Architecture

The system uses three specialized AI agents:

1. **Job Analyzer**: Extracts and analyzes job requirements
2. **Resume Analyzer**: Scores resume match and suggests improvements
3. **Company Researcher**: Gathers company information for interviews

## Requirements

- Python `>= 3.10` and `< 3.13`
- PDF resume file
- Job posting URL
- Company name

## Support

- [CrewAI Documentation](https://docs.crewai.com)
- [Community Forum](https://community.crewai.com)
- [Chat with our docs](https://chatg.pt/DWjSBZn)
