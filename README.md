# Document Intelligence System - Round 1B

## Overview
A persona-driven document intelligence system that extracts and prioritizes relevant sections from PDF documents based on user persona and job requirements.

## System Requirements
- **CPU Only**: No GPU required
- **Model Size**: < 100MB (uses TF-IDF, no large language models)
- **Processing Time**: < 60 seconds for 3-5 documents
- **No Internet**: Fully offline processing
- **Docker**: Required for execution

## Docker Execution

### Prerequisites
- Docker Desktop installed and running
- PDF documents placed in the `documents/` folder

### Build and Run

# Navigate to project directory
cd C:\Users\sneha\adobe_hackathon\round_1b

# Build the Docker image
docker build -t round1b:latest .

# Run the container with volume mounting
docker run -v ${PWD}:/app round1b:latest
```


### Expected Output
```
=== Document Intelligence System Starting ===
Configuration loaded successfully
Processing documents/South of France - Cities.pdf...
Processing documents/South of France - Cuisine.pdf...
Processing documents/South of France - History.pdf...
Processing documents/South of France - Restaurants and Hotels.pdf...
Processing documents/South of France - Things to Do.pdf...
Processing documents/South of France - Tips and Tricks.pdf...
Processing documents/South of France - Traditions and Culture.pdf...

Extracted 73 sections from 7 documents
Ranked 15 sections

=== Processing Complete ===
Processing time: 9.59 seconds
Extracted sections: 15
Refined sections: 15
Output saved to: challenge1b_output.json
```

## Input Configuration

The system reads from `input_config.json`. 
- **documents**: List of PDF file paths (relative to project root)
- **persona**: User role
- **job_to_be_done**: Specific task description

Example configuration:
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
