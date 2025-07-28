# Adobe-India-Hackathon25-Challenge_1b

## Overview
A persona-driven document intelligence system that extracts and prioritizes the most relevant sections from a collection of documents based on a specific persona and their job-to-be-done.

## Docker Execution

### Prerequisites
- Docker Desktop installed and running
- PDF documents placed in the `documents/` folder

### Build and Run

- **Build the Docker image**
    docker build -t round1b:latest .

- **Run the container with volume mounting**
    docker run -v ${PWD}:/app round1b:latest

## Input Format

The system reads from `input_config.json`. 
- **documents**: List of PDF file paths (relative to project root)
- **persona**: User role
- **job_to_be_done**: Specific task description

### Input Configuration
```json
{
  "documents": [
    "documents/....",
  ],
  "persona": {
    "role": "Travel Planner",
  },
  "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends."
}
```

## Output Format

The system generates `challenge1b_output.json` with the following structure:

### Metadata Section
```json
{
  "metadata": {
    "input_documents": ["paper1.pdf", "paper2.pdf", "paper3.pdf"],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends.",
    "processing_timestamp": "2024-01-15T10:30:45.123456",
    "processing_time_seconds": 12.34
  }
}
```

### Extracted Sections
```json
{
  "extracted_sections": [
    {
      "document": "South of France - Cities.pdf",
      "page_number": 3,
      "section_title": "Section 1",
      "importance_rank": 1
    }
  ]
}
```

### Sub-section Analysis
```json
{
  "sub_section_analysis": [
    {
      "document": "South of France - Cities.pdf", 
      "page_number": 3,
      "section_title": "Section 1",
      "refined_text": "Local Experiences • Boat Trip to the Calanques: Take a boat trip to the Calanques",
      "importance_rank": 1
    }
  ]
}
```

## Project Structure
```
round_1b/
├── documents/               # PDF files to process
│   ├── South of France - Cities.pdf
│   ├── South of France - Cuisine.pdf
│   └── South of France - History.pdf
|   └── South of France - Restaurants and Hotels.pdf
|   └── South of France - Things to Do.pdf
|   └── South of France - Tips and Tricks.pdf
|   └── South of France - Traditions and Culture.pdf
|
├── src/
│   └── main.py             # Core processing logic
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies  
├── input_config.json       # Input configuration
├── approach_explanation.md # Technical methodology
├── README.md              # This file
└── challenge1b_output.json # Generated output
```

## Architecture Overview

1. **PDF Text Extraction**: Uses `pdfplumber` for robust text extraction with page-level granularity
2. **Section Detection**: Pattern-based identification of document sections using headers and formatting
3. **Relevance Ranking**: TF-IDF vectorization with cosine similarity scoring against persona queries
4. **Persona Weighting**: Boosts sections containing persona-specific focus area keywords
5. **Content Refinement**: Extracts most relevant sentences from top-ranked sections

## Performance Characteristics

- **Dependencies**: Only lightweight libraries (pdfplumber, scikit-learn, numpy)
- **Memory Usage**: < 500MB RAM during processing
- **Processing Speed**: ~4-5 seconds per document
- **Scalability**: Handles 3-10 documents efficiently
- **Accuracy**: TF-IDF provides robust semantic matching without internet dependency
