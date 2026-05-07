from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from openai import OpenAI
from pdf_processor import PDFProcessor
from rag_system import RAGSystem
import json
import time
import re

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "anthropic/claude-3-haiku"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "QuestGen AI"
    }
)
pdf_processor = PDFProcessor()
rag_system = RAGSystem(client=client, model=OPENROUTER_MODEL)
def call_openrouter_api(prompt, max_retries=3, initial_delay=5):
    """Call OpenRouter API with retry logic for rate limit errors"""
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            response_text = response.choices[0].message.content
            class Response:
                def __init__(self, text):
                    self.text = text
            return Response(response_text)
        except Exception as e:
            error_str = str(e)
            
            if '429' in error_str or 'rate limit' in error_str.lower() or 'quota' in error_str.lower():
                if attempt < max_retries - 1:
                    delay = delay * 2
                    print(f"Rate limit exceeded. Retrying in {delay:.1f} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    raise Exception(f"API rate limit exceeded after {max_retries} attempts. Please try again later.")
            else:
                raise e
    
    raise Exception("Failed to call OpenRouter API after retries")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'QuestGen AI Backend is running'}), 200

@app.route('/api/upload/previous-papers', methods=['POST'])
def upload_previous_papers():
    """Upload previous question papers (1-3 PDFs)"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        
        if len(files) == 0:
            return jsonify({'error': 'At least one file is required'}), 400
        
        if len(files) > 3:
            return jsonify({'error': 'Maximum 3 files allowed'}), 400
        
        uploaded_files = []
        processed_content = []
        
        for file in files:
            if file.filename == '':
                continue
            
            if not allowed_file(file.filename):
                return jsonify({'error': f'Invalid file type. Only PDF files are allowed.'}), 400
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, f"previous_paper_{len(uploaded_files)}_{filename}")
            file.save(filepath)
            content = pdf_processor.extract_text(filepath)
            if content:
                processed_content.append({
                    'filename': filename,
                    'content': content,
                    'filepath': filepath
                })
            
            uploaded_files.append({
                'filename': filename,
                'filepath': filepath
            })
    
        if processed_content:
            rag_system.add_documents(processed_content, doc_type='previous_papers')
        
        return jsonify({
            'message': f'Successfully uploaded {len(uploaded_files)} file(s)',
            'files': [f['filename'] for f in uploaded_files],
            'processed': len(processed_content)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/copo', methods=['POST'])
def upload_copo():
    """Upload CO/PO mapping file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"copo_{filename}")
        file.save(filepath)
        
        content = pdf_processor.extract_text(filepath)
        
        if content:
            rag_system.add_documents([{
                'filename': filename,
                'content': content,
                'filepath': filepath
            }], doc_type='copo')
        
        return jsonify({
            'message': 'CO/PO file uploaded successfully',
            'filename': filename,
            'processed': content is not None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/syllabus', methods=['POST'])
def upload_syllabus():
    """Upload course syllabus"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"syllabus_{filename}")
        file.save(filepath)
        
        content = pdf_processor.extract_text(filepath)
        content = pdf_processor.extract_text(filepath)
        
        if content:
            rag_system.add_documents([{
                'filename': filename,
                'content': content,
                'filepath': filepath
            }], doc_type='syllabus')
        
        return jsonify({
            'message': 'Syllabus uploaded successfully',
            'filename': filename,
            'processed': content is not None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process/read-pdfs', methods=['POST'])
def read_pdfs():
    """Read and process all uploaded PDFs using AI"""
    try:
        documents = rag_system.get_all_documents()
        
        total_docs = sum(len(docs) for docs in documents.values() if isinstance(docs, list))
        if total_docs == 0:
            return jsonify({'error': 'No documents found. Please upload files first.'}), 400
        
        documents_for_prompt = {}
        for doc_type, docs in documents.items():
            if isinstance(docs, list):
                documents_for_prompt[doc_type] = []
                for doc in docs:
                    if isinstance(doc, dict):
                        doc_copy = {
                            'filename': doc.get('filename', 'Unknown'),
                            'content': doc.get('content', '')[:5000] 
                        }
                        documents_for_prompt[doc_type].append(doc_copy)
        
        summary_prompt = f"""
        Analyze the following documents and provide a comprehensive summary:
        
        1. Previous Question Papers: Extract question patterns, types, difficulty levels, and topics covered.
        2. CO/PO Mapping: Identify course outcomes and program outcomes with their mappings.
        3. Syllabus: Extract course topics, learning objectives, and content structure.
        
        Documents:
        {json.dumps(documents_for_prompt, indent=2)}
        
        Provide a structured summary in JSON format with:
        - question_patterns: List of identified question patterns
        - topics_covered: List of topics from syllabus
        - co_po_mappings: CO-PO mapping structure
        - difficulty_levels: Identified difficulty levels
        """
        
        response = call_openrouter_api(summary_prompt)
        
        return jsonify({
            'message': 'PDFs processed successfully',
            'summary': response.text,
            'documents_count': total_docs
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/question-patterns', methods=['POST'])
def analyze_question_patterns():
    """Analyze previous question papers to extract mark patterns"""
    try:
        documents = rag_system.get_all_documents()
        previous_papers = documents.get('previous_papers', [])
        
        if not previous_papers:
            return jsonify({'error': 'No previous question papers found. Please upload them first.'}), 400
        
        papers_content = []
        for paper in previous_papers:
            if paper.get('content'):
                content = paper.get('content', '')[:3000]
                papers_content.append({
                    'filename': paper.get('filename', 'Unknown'),
                    'content': content
                    })
        combined_content = "\n\n---\n\n".join([
            f"Paper: {p['filename']}\n{p['content']}" 
            for p in papers_content
        ])
        
        analysis_prompt = f"""Analyze these question papers and extract mark distribution patterns.

Papers:
{combined_content[:4000]}

Extract:
1. All unique mark values (2, 3, 5, 8, 16, etc.)
2. For each mark value:
   - Count of questions
   - Type: "direct", "either_or", or "split"
   - If split, parent marks

Return ONLY valid JSON:
        {{
            "mark_patterns": [
                {{
                    "marks": 2,
                    "count": 10,
                    "type": "direct",
                    "description": "10 questions of 2 marks each"
                }},
                {{
                    "marks": 16,
                    "count": 10,
                    "type": "either_or",
                    "description": "10 questions of 16 marks each (Answer any one)"
                }},
                {{
                    "marks": 8,
                    "count": 2,
                    "type": "split",
                    "parent_marks": 16,
                    "description": "16 marks split into 2 questions of 8 marks each"
                }}
            ]
        }}
        
        Important:
        - Only include mark values that actually appear in the question papers
        - If a 16-mark question is split into 2 questions of 8 marks, include both: the 16-mark entry with type "either_or" or "split", and the 8-mark entry with type "split"
        - Be precise with the counts
        - Return ONLY the JSON, no additional text
        """
        
        response = call_openrouter_api(analysis_prompt)
        
        response_text = response.text.strip()
        
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        try:
            patterns = json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                patterns = json.loads(json_match.group())
            else:
                raise ValueError("Could not parse JSON from AI response")
        
        return jsonify({
            'message': 'Question patterns analyzed successfully',
            'patterns': patterns.get('mark_patterns', [])
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_questions_in_batches(question_counts, context, copo_mapping, previous_questions, max_questions_per_batch=10):
    """Generate questions in batches to handle large numbers of questions"""
    all_questions = []

    requested_counts = {}
    for marks, count in (question_counts or {}).items():
        try:
            marks_int = int(marks)
            count_int = int(count)
        except (ValueError, TypeError):
            continue
        if count_int > 0:
            requested_counts[marks_int] = count_int

    remaining_counts = dict(requested_counts)
    
    copo_text = "\n".join([f"{co}: {', '.join(pos)}" for co, pos in copo_mapping.items()])
    prev_questions_text = "\n".join([f"- {q[:200]}..." for q in previous_questions[:5]])
    
    max_batches = max(10, sum(remaining_counts.values()) * 5)
    batch_attempts = 0

    while any(count > 0 for count in remaining_counts.values()):
        batch_attempts += 1
        if batch_attempts > max_batches:
            break

        batch_spec = {}
        batch_total = 0
        
        for marks in list(remaining_counts.keys()):
            if remaining_counts.get(marks, 0) > 0 and batch_total < max_questions_per_batch:
                batch_count = min(remaining_counts[marks], max_questions_per_batch - batch_total)
                batch_spec[marks] = batch_count
                batch_total += batch_count
                if batch_total >= max_questions_per_batch:
                    break
        
        if not batch_spec:
            break
            
        question_spec_text = "\n".join([f"- {count} question(s) of {marks} mark(s) each" 
                                      for marks, count in batch_spec.items()])
        
        generation_prompt = f"""
        You are an expert question paper generator. Your task is to create a question paper based on the following:
        
        ===== SYLLABUS AND CONTEXT =====
        {context}
        
        ===== CO-PO MAPPING =====
        {copo_text if copo_text else 'No CO-PO mapping provided'}
        
        ===== SAMPLE PREVIOUS QUESTIONS (DO NOT REPEAT THESE) =====
        {prev_questions_text if prev_questions_text else 'No previous questions found'}
        
        ===== INSTRUCTIONS =====
        1. Generate questions with EXACTLY this distribution:
        {question_spec_text}
        
        2. For each question, ensure:
           - It aligns with at least one CO and corresponding POs from the mapping
           - It's not similar to any of the previous questions shown above
           - It matches the style and format from the context
           - It has appropriate difficulty based on the marks
        
        3. For CO-PO mapping:
           - Each question must be mapped to at least one CO
           - Map to POs based on the CO-PO mapping provided
           - Ensure good coverage of all COs if possible
        
        4. Question types:
           - 1-2 marks: Short answer or MCQ
           - 3-5 marks: Short answer with brief explanation
           - 6+ marks: Long answer or problem-solving
        
        ===== OUTPUT FORMAT =====
        Return ONLY valid JSON with this structure:
        {{
            "questions": [
                {{
                    "question_number": 1,
                    "question_text": "...",
                    "question_type": "Short/MCQ/Long",
                    "marks": 2,
                    "co_mapping": ["CO1"],
                    "po_mapping": ["PO1", "PO2"],
                    "difficulty_level": "Easy/Medium/Hard",
                    "topic": "Topic name from syllabus"
                }}
            ]
        }}
        """
        
        time.sleep(1)
        
        try:
            response = call_openrouter_api(generation_prompt)
            
            response_text = response.text.strip()
            
            json_match = re.search(r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}', response_text, re.DOTALL)
            
            if not json_match:
                start_idx = response_text.find('{')
                if start_idx != -1:
                    response_text = response_text[start_idx:]
                if '```' in response_text:
                    parts = response_text.split('```')
                    if len(parts) > 1:
                        response_text = parts[1] if len(parts) > 1 else parts[0]
                        if response_text.startswith('json\n'):
                            response_text = response_text[5:]
                        elif response_text.startswith('json'):
                            response_text = response_text[4:]
                json_match = re.search(r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}', response_text, re.DOTALL)
                
                if not json_match:
                    start = response_text.find('{')
                    end = response_text.rfind('}')
                    if start != -1 and end != -1 and end > start:
                        response_text = response_text[start:end+1]
                    else:
                        raise ValueError("Could not find valid JSON in the response")
                else:
                    response_text = json_match.group(0)
            else:
                response_text = json_match.group(0)
            
            response_text = response_text.strip()
            
            questions_data = json.loads(response_text)
            
            print(f"Response structure: {json.dumps({k: type(v).__name__ for k, v in questions_data.items()}, indent=2)}")
            
            if not isinstance(questions_data, dict):
                raise ValueError(f"Expected dictionary response, got {type(questions_data).__name__}")
                
            if 'questions' not in questions_data:
                possible_question_keys = [k for k in questions_data.keys() if 'question' in k.lower()]
                if possible_question_keys:
                    questions_data['questions'] = questions_data[possible_question_keys[0]]
                else:
                    list_items = [v for v in questions_data.values() if isinstance(v, list)]
                    if list_items:
                        questions_data['questions'] = list_items[0]
                    else:
                        raise ValueError("No questions found in the response. Response format is not as expected.")
            
            if not isinstance(questions_data['questions'], list):
                questions_data['questions'] = [questions_data['questions']]
            
            batch_questions = []
            for q in questions_data['questions']:
                if not isinstance(q, dict):
                    print(f"Skipping invalid question (not a dictionary): {q}")
                    continue
                    
                required_fields = ['question_text', 'marks']
                if not all(field in q for field in required_fields):
                    print(f"Skipping question missing required fields: {q}")
                    continue
                    
                q.setdefault('co_mapping', ['CO1'])
                q.setdefault('po_mapping', ['PO1'])
                q.setdefault('question_type', 'Short' if isinstance(q.get('marks', 0), (int, float)) and q['marks'] <= 2 else 'Long')
                q.setdefault('difficulty_level', 'Medium')
                q.setdefault('topic', 'General')
                
                try:
                    q['marks'] = int(q['marks'])
                except (ValueError, TypeError):
                    q['marks'] = 1  

                batch_questions.append(q)

            accepted_batch_questions = []
            for q in batch_questions:
                m = q.get('marks')
                if not isinstance(m, int):
                    continue
                if remaining_counts.get(m, 0) <= 0:
                    continue
                accepted_batch_questions.append(q)
                remaining_counts[m] -= 1

            all_questions.extend(accepted_batch_questions)

            previous_questions.extend([q['question_text'] for q in accepted_batch_questions])
            prev_questions_text = "\n".join([f"- {q[:200]}..." for q in previous_questions[-5:]])
            
        except json.JSONDecodeError as e:
            error_msg = f"Error parsing JSON response: {e}"
            print(error_msg)
            print(f"Response text (first 1000 chars): {response_text[:1000]}")
            
            try:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    print("Attempting to extract JSON from response...")
                    questions_data = json.loads(json_str)
                    if 'questions' in questions_data:
                        print("Successfully extracted questions from malformed JSON!")
                        batch_questions = []
                        for q in questions_data['questions']:
                            if not isinstance(q, dict):
                                print(f"Skipping invalid question (not a dictionary): {q}")
                                continue
                                
                            required_fields = ['question_text', 'marks']
                            if not all(field in q for field in required_fields):
                                print(f"Skipping question missing required fields: {q}")
                                continue
                                
                            q.setdefault('co_mapping', ['CO1'])
                            q.setdefault('po_mapping', ['PO1'])
                            q.setdefault('question_type', 'Short' if isinstance(q.get('marks', 0), (int, float)) and q['marks'] <= 2 else 'Long')
                            q.setdefault('difficulty_level', 'Medium')
                            q.setdefault('topic', 'General')
                            
                            try:
                                q['marks'] = int(q['marks'])
                            except (ValueError, TypeError):
                                q['marks'] = 1
                                
                            batch_questions.append(q)
                        accepted_batch_questions = []
                        for q in batch_questions:
                            m = q.get('marks')
                            if not isinstance(m, int):
                                continue
                            if remaining_counts.get(m, 0) <= 0:
                                continue
                            accepted_batch_questions.append(q)
                            remaining_counts[m] -= 1

                        if accepted_batch_questions:
                            all_questions.extend(accepted_batch_questions)
                            previous_questions.extend([q['question_text'] for q in accepted_batch_questions])
                            prev_questions_text = "\n".join([f"- {q[:200]}..." for q in previous_questions[-5:]])
                            continue
            except Exception as parse_error:
                print(f"Failed to extract JSON from response: {parse_error}")
                
            continue
            
        except Exception as e:
            error_msg = f"Error in batch processing: {str(e)}"
            print(error_msg)
            if 'response_text' in locals():
                print(f"Response text (first 500 chars): {response_text[:500]}")
            continue
    
    final_questions = []
    counts_left = dict(requested_counts)
    for q in all_questions:
        m = q.get('marks')
        if counts_left.get(m, 0) <= 0:
            continue
        final_questions.append(q)
        counts_left[m] -= 1

    for i, q in enumerate(final_questions, start=1):
        q['question_number'] = i

    return final_questions

@app.route('/api/generate/questions', methods=['POST'])
def generate_questions():
    """Generate questions using RAG with CO-PO mapping and question deduplication"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        question_counts = data.get('question_counts', {})
        
        if not question_counts:
            return jsonify({'error': 'Question counts not provided'}), 400
        
        query = data.get('query', 'Generate exam questions based on the uploaded documents')
        rag_context = rag_system.retrieve_context(query)
        
        copo_mapping = rag_context.get('copo_mapping', {})
        previous_questions = rag_context.get('previous_questions', [])
        context = rag_context.get('context', '')
        
        try:
            all_questions = generate_questions_in_batches(
                question_counts, 
                context, 
                copo_mapping, 
                previous_questions
            )
            
            co_coverage = list(set(co for q in all_questions for co in q['co_mapping']))
            po_coverage = list(set(po for q in all_questions for po in q['po_mapping']))
            
            return jsonify({
                'message': 'Questions generated successfully',
                'questions': all_questions,
                'metadata': {
                    'total_questions': len(all_questions),
                    'co_coverage': co_coverage,
                    'po_coverage': po_coverage,
                    'coverage_percentage': {
                        'co': len(co_coverage) / len(copo_mapping) * 100 if copo_mapping else 0,
                        'po': len(po_coverage) / len(set(po for pos in copo_mapping.values() for po in pos)) * 100 if copo_mapping else 0
                    }
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'error': 'Error generating questions',
                'details': str(e)
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

