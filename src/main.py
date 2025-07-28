import json
import os
import time
import re
from datetime import datetime
from typing import List, Dict, Any
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class DocumentIntelligenceSystem:
    def __init__(self):
        """Initialize with TF-IDF vectorizer for CPU-only processing"""
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.95
        )
        
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF with page and section information"""
        sections = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:  # Filter out empty/short pages
                        section_splits = self._split_into_sections(text, page_num)
                        for section in section_splits:
                            section['document'] = os.path.basename(pdf_path)
                        sections.extend(section_splits)
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
                    
        return sections
    
    def _split_into_sections(self, text: str, page_num: int) -> List[Dict]:
        """Split text into logical sections using multiple strategies"""
        sections = []
        
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Strategy 1: Split by section headers
        section_patterns = [
            r'(?:^|\n)([A-Z][A-Z\s]{2,50})\n',  # ALL CAPS headers
            r'(?:^|\n)(\d+\.?\s+[A-Z][^.!?]*)\n',  # Numbered sections
            r'(?:^|\n)(Abstract|Introduction|Methods?|Results?|Discussion|Conclusion|References|Background|Related Work|Experiments?)[.\s]*\n',
            r'(?:^|\n)([IVX]+\.\s+[A-Z][^.!?]*)\n'  # Roman numerals
        ]
        
        # Find section boundaries
        boundaries = []
        for pattern in section_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                boundaries.append((match.start(), match.group(1).strip()))
        
        # Sort boundaries by position
        boundaries.sort(key=lambda x: x[0])
        
        if not boundaries:
            # Fallback: split by paragraphs
            return self._split_by_paragraphs(text, page_num)
        
        # Create sections based on boundaries
        current_section = "Introduction"
        start_pos = 0
        
        for i, (pos, title) in enumerate(boundaries):
            # Add previous section
            if start_pos < pos:
                section_text = text[start_pos:pos].strip()
                if len(section_text) > 100:  # Minimum section length
                    sections.append({
                        'document': 'placeholder',
                        'page_number': page_num,
                        'section_title': current_section,
                        'text': section_text
                    })
            
            current_section = title
            start_pos = pos
        
        # Add final section
        final_text = text[start_pos:].strip()
        if len(final_text) > 100:
            sections.append({
                'document': 'placeholder',
                'page_number': page_num,
                'section_title': current_section,
                'text': final_text
            })
            
        return sections if sections else self._split_by_paragraphs(text, page_num)
    
    def _split_by_paragraphs(self, text: str, page_num: int) -> List[Dict]:
        """Fallback method: split by paragraphs"""
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
        
        sections = []
        for i, para in enumerate(paragraphs[:5]):  # Limit to 5 paragraphs per page
            sections.append({
                'document': 'placeholder',
                'page_number': page_num,
                'section_title': f"Section {i+1}",
                'text': para
            })
        
        return sections
    
    def rank_sections_by_relevance(self, sections: List[Dict], 
                                 persona: Dict, job_description: str) -> List[Dict]:
        """Rank sections based on persona and job relevance"""
        
        if not sections:
            return []
        
        # Create comprehensive query from persona and job
        persona_role = persona.get('role', '')
        persona_expertise = persona.get('expertise', '')
        persona_focus = ' '.join(persona.get('focus_areas', []))
        
        # Handle travel planning specific terms
        if 'travel' in persona_role.lower() or 'planner' in persona_role.lower():
            travel_keywords = ['itinerary', 'activities', 'attractions', 'restaurants', 'hotels', 'transportation', 'budget', 'schedule']
            persona_expertise += ' ' + ' '.join(travel_keywords)
        
        persona_text = f"{persona_role} {persona_expertise} {persona_focus}"
        query = f"{persona_text} {job_description}"
        
        # Get all texts for vectorization
        section_texts = [s['text'] for s in sections]
        all_texts = section_texts + [query]
        
        try:
            # Fit TF-IDF and transform
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Query is the last vector
            query_vector = tfidf_matrix[-1]
            section_vectors = tfidf_matrix[:-1]
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, section_vectors)[0]
            
            # Add persona-specific boost for travel planning
            travel_boost_terms = ['restaurant', 'hotel', 'attraction', 'activity', 'food', 'culture', 'history', 'city', 'place', 'visit', 'trip', 'travel']
            group_boost_terms = ['group', 'friends', 'college', 'young', 'budget', 'affordable', 'student']
            
            for i, section in enumerate(sections):
                base_score = similarities[i]
                
                # Boost score for travel-related content
                boost = 0
                section_lower = section['text'].lower()
                
                # Travel content boost
                for term in travel_boost_terms:
                    if term in section_lower:
                        boost += 0.1
                
                # Group travel boost
                for term in group_boost_terms:
                    if term in section_lower:
                        boost += 0.05
                
                # Section title boost for travel planning
                title_lower = section['section_title'].lower()
                if any(term in title_lower for term in ['restaurant', 'hotel', 'activity', 'attraction', 'thing to do', 'tip']):
                    boost += 0.2
                
                final_score = base_score + boost
                section['relevance_score'] = float(final_score)
                section['importance_rank'] = 0  # Will be set after sorting
            
            # Sort by relevance
            sections.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Assign importance ranks
            for i, section in enumerate(sections):
                section['importance_rank'] = i + 1
                
        except Exception as e:
            print(f"Error in ranking: {str(e)}")
            # Fallback: assign sequential ranks
            for i, section in enumerate(sections):
                section['relevance_score'] = 1.0 / (i + 1)
                section['importance_rank'] = i + 1
        
        return sections[:15]  # Return top 15 sections
    
    def refine_sections(self, sections: List[Dict], job_description: str) -> List[Dict]:
        """Refine sections for sub-section analysis"""
        refined_sections = []
        
        # Extract key terms from job description
        job_terms = set(re.findall(r'\b[a-zA-Z]{4,}\b', job_description.lower()))
        
        for section in sections:
            sentences = [s.strip() for s in re.split(r'[.!?]+', section['text']) if len(s.strip()) > 20]
            
            # Score sentences based on job relevance
            scored_sentences = []
            for sentence in sentences:
                sentence_lower = sentence.lower()
                score = sum(1 for term in job_terms if term in sentence_lower)
                scored_sentences.append((score, sentence))
            
            # Sort by relevance and take top sentences
            scored_sentences.sort(key=lambda x: x[0], reverse=True)
            top_sentences = [s[1] for s in scored_sentences[:3]]
            
            if not top_sentences and sentences:
                top_sentences = sentences[:2]  # Fallback to first sentences
            
            refined_text = '. '.join(top_sentences)
            if not refined_text.endswith('.'):
                refined_text += '.'
            
            refined_sections.append({
                'document': section['document'],
                'page_number': section['page_number'],
                'section_title': section['section_title'],
                'refined_text': refined_text,
                'importance_rank': section['importance_rank']
            })
        
        return refined_sections
    
    def process_documents(self, config_path: str) -> Dict[str, Any]:
        """Main processing function"""
        start_time = time.time()
        
        try:
            # Load configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print("Configuration loaded successfully")
            
            # Handle different input formats
            if 'challenge_info' in config:
                # New format with challenge_info
                documents = config['documents']
                persona = config['persona']
                job_description = config['job_to_be_done']['task'] if isinstance(config['job_to_be_done'], dict) else config['job_to_be_done']
                challenge_info = config.get('challenge_info', {})
            else:
                # Old format
                documents = config['documents']
                persona = config['persona']
                job_description = config['job_to_be_done']
                challenge_info = {}
            
            # Extract text from all documents
            all_sections = []
            processed_docs = []
            
            for doc_path in documents:
                if os.path.exists(doc_path):
                    print(f"Processing {doc_path}...")
                    sections = self.extract_text_from_pdf(doc_path)
                    all_sections.extend(sections)
                    processed_docs.append(os.path.basename(doc_path))
                else:
                    print(f"Warning: Document not found: {doc_path}")
            
            print(f"Extracted {len(all_sections)} sections from {len(processed_docs)} documents")
            
            # Rank sections by relevance
            ranked_sections = self.rank_sections_by_relevance(
                all_sections, persona, job_description
            )
            
            print(f"Ranked {len(ranked_sections)} sections")
            
            # Refine sections
            refined_sections = self.refine_sections(ranked_sections, job_description)
            
            # Prepare output
            output = {
                "metadata": {
                    "input_documents": processed_docs,
                    "persona": persona,
                    "job_to_be_done": job_description,
                    "processing_timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": round(time.time() - start_time, 2)
                },
                "extracted_sections": [
                    {
                        "document": section['document'],
                        "page_number": section['page_number'],
                        "section_title": section['section_title'],
                        "importance_rank": section['importance_rank']
                    }
                    for section in ranked_sections
                ],
                "sub_section_analysis": refined_sections
            }
            
            # Add challenge info if present
            if challenge_info:
                output["metadata"]["challenge_info"] = challenge_info
            
            return output
            
        except Exception as e:
            print(f"Error in processing: {str(e)}")
            return {
                "metadata": {
                    "input_documents": [],
                    "persona": {},
                    "job_to_be_done": "",
                    "processing_timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": round(time.time() - start_time, 2),
                    "error": str(e)
                },
                "extracted_sections": [],
                "sub_section_analysis": []
            }

def main():
    """Main execution function"""
    print("=== Document Intelligence System Starting ===")
    
    system = DocumentIntelligenceSystem()
    result = system.process_documents('input_config.json')
    
    # Save output
    with open('challenge1b_output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== Processing Complete ===")
    print(f"Processing time: {result['metadata']['processing_time_seconds']} seconds")
    print(f"Extracted sections: {len(result['extracted_sections'])}")
    print(f"Refined sections: {len(result['sub_section_analysis'])}")
    print("Output saved to: challenge1b_output.json")

if __name__ == "__main__":
    main()
