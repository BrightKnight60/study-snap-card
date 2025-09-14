from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import logging
from datetime import datetime
import sqlite3
import anthropic
from typing import List, Dict, Any
import uuid
import re
import html
import base64
from dotenv import load_dotenv
from config import Config
from models import init_db, create_document, create_flashcard, get_flashcards_by_document, get_all_documents

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
logging.basicConfig(
    level=logging.INFO if app.config['DEBUG'] else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'app.log'))
    ]
)
logger = logging.getLogger(__name__)

# Configure CORS with specific origins
CORS(app, origins=app.config['CORS_ORIGINS'])

# Initialize Anthropic client with error handling
def init_anthropic_client():
    """Initialize Anthropic client with proper error handling"""
    api_key = app.config.get('ANTHROPIC_API_KEY')

    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in environment variables. "
            "Please set your API key in the .env file or environment."
        )

    try:
        return anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        raise ValueError(f"Failed to initialize Anthropic client: {str(e)}")

# Initialize client
try:
    client = init_anthropic_client()
    logger.info("✅ Anthropic client initialized successfully")
except ValueError as e:
    logger.error(f"❌ Anthropic client initialization failed: {e}")
    client = None

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
logger.info(f"📁 Upload directory ready: {app.config['UPLOAD_FOLDER']}")

# Initialize database with app context
with app.app_context():
    init_db()
    logger.info("📊 Database initialized successfully")

# System prompt for Claude
SYSTEM_PROMPT = """You are a diligent, hard-working student that is trying to learn new course content by creating notecards to learn the most important information. Meticulously analyze this document ({filename}) containing course content and identify all important concepts and methodologies you need to master. For instance, important information for flashcards could include equations or example problems. Create flashcards by listing extracted information in small chunks to optimize learning. IMPORTANT: flashcards must take information DIRECTLY from the user uploaded file. DO NOT DEVIATE FROM UPLOADED CONTENT."""

def sanitize_text(text: str, max_length: int = 1000) -> str:
    """Sanitize text input to prevent XSS and limit length"""
    if not text:
        return ""

    # Remove HTML tags and entities
    text = html.escape(text.strip())

    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)

    # Limit length
    if len(text) > max_length:
        text = text[:max_length] + "..."

    return text

def validate_process_id(process_id: str) -> bool:
    """Validate process ID format (UUID4)"""
    if not process_id:
        return False

    try:
        uuid.UUID(process_id, version=4)
        return True
    except ValueError:
        return False

def get_media_type(filename: str) -> str:
    """Get media type for Claude API based on file extension"""
    file_ext = filename.rsplit('.', 1)[1].lower()
    media_types = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'txt': 'text/plain'
    }
    return media_types.get(file_ext, 'application/octet-stream')

def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename or '.' not in filename:
        return False

    # Get extension and ensure it's safe
    file_ext = filename.rsplit('.', 1)[1].lower()

    # Check for double extensions (security risk)
    if filename.count('.') > 1:
        # Allow only if all extensions are safe
        parts = filename.lower().split('.')
        for part in parts[1:]:  # Skip filename part
            if part not in app.config['ALLOWED_EXTENSIONS'] and part not in ['compressed']:
                return False

    return file_ext in app.config['ALLOWED_EXTENSIONS']

def validate_file_size(file):
    """Check if file size is within limit"""
    try:
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer

        if file_size == 0:
            return False, "File is empty"

        if file_size > app.config['MAX_FILE_SIZE']:
            return False, f"File size ({file_size} bytes) exceeds {app.config['MAX_FILE_SIZE']} byte limit"

        return True, None
    except Exception as e:
        return False, f"Error checking file size: {str(e)}"

def encode_file_to_base64(file_path: str) -> str:
    """Encode file to base64 for Claude API document processing"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
            if len(file_bytes) == 0:
                raise ValueError("File is empty")
            base64_data = base64.b64encode(file_bytes).decode('utf-8')
            return base64_data
    except Exception as e:
        raise Exception(f"Error encoding file to base64: {str(e)}")

def process_document_with_claude(file_path: str, filename: str) -> str:
    """Send document directly to Claude API for flashcard generation"""
    if not client:
        raise Exception("Claude API client is not initialized")

    try:
        # Encode file to base64
        base64_data = encode_file_to_base64(file_path)
        media_type = get_media_type(filename)

        logger.info(f"Processing document {filename} ({media_type}) with Claude API")

        # Create the message using Claude's document API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20000,  # Increased for better flashcard generation
            temperature=0.3,   # Lower temperature for consistent JSON output
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_data
                            }
                        },
                        {
                            "type": "text",
                            "text": f"""You are a diligent, hard-working student that is trying to learn new course content by creating notecards to learn the most important information. Meticulously analyze this document ({filename}) containing course content and identify all important concepts and methodologies you need to master. For instance, important information for flashcards could include equations or example problems. Create flashcards by listing extracted information in small chunks to optimize learning. IMPORTANT: flashcards must take information DIRECTLY from the user uploaded file. DO NOT DEVIATE FROM UPLOADED CONTENT".

IMPORTANT: Format your response as a JSON array of objects, where each object has "front" and "back" properties. Focus on key concepts, definitions, formulas, and important facts. Create 5-20 flashcards depending on content richness. The output text should be fully human readable, with no formatting or markdown.

Example format:
[
  {{"front": "What is the capital of France?", "back": "Paris"}},
  {{"front": "Define photosynthesis", "back": "The process by which plants convert light energy into chemical energy"}}
]

Start your response with the JSON array:"""
                        }
                    ]
                },
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "Here are the core concepts from the document, formatted as flashcards in JSON:"
                        }
                    ]
                }
            ]
        )

        if not response.content or len(response.content) == 0:
            raise Exception("Claude API returned empty response")

        response_text = response.content[0].text

        if not response_text or not response_text.strip():
            raise Exception("Claude API returned empty text content")

        logger.info(f"Received {len(response_text)} characters from Claude API")
        return response_text

    except Exception as e:
        # Enhanced error handling for Claude API
        error_msg = str(e)
        logger.error(f"Claude API error for {filename}: {error_msg}")

        if "rate_limit" in error_msg.lower():
            raise Exception("API rate limit exceeded. Please try again in a few minutes.")
        elif "insufficient_quota" in error_msg.lower() or "quota" in error_msg.lower():
            raise Exception("API quota exceeded. Please check your Anthropic account.")
        elif "invalid_api_key" in error_msg.lower():
            raise Exception("Invalid API key. Please check your ANTHROPIC_API_KEY configuration.")
        elif "file_size" in error_msg.lower() or "too large" in error_msg.lower():
            raise Exception("Document is too large for processing. Please try a smaller file.")
        else:
            raise Exception(f"Claude API processing failed: {error_msg}")

def parse_claude_response(response_text, filename="document"):
    """Parse Claude's response to extract flashcards"""
    if not response_text or not response_text.strip():
        raise ValueError("Response text is empty")

    valid_flashcards = []

    try:
        # Primary: Try to extract JSON from the response
        start = response_text.find('[')
        end = response_text.rfind(']') + 1

        if start != -1 and end > start:
            json_str = response_text[start:end]

            try:
                flashcards = json.loads(json_str)

                if isinstance(flashcards, list) and len(flashcards) > 0:
                    for i, card in enumerate(flashcards):
                        if isinstance(card, dict) and 'front' in card and 'back' in card:
                            front = str(card['front']).strip()
                            back = str(card['back']).strip()

                            # Validate content length and quality
                            if len(front) > 5 and len(back) > 5 and len(front) <= 500 and len(back) <= 1000:
                                valid_flashcards.append({
                                    'front': sanitize_text(front, 500),
                                    'back': sanitize_text(back, 1000)
                                })
                            else:
                                logger.warning(f"Skipping invalid flashcard {i+1} (front: {len(front)} chars, back: {len(back)} chars)")

                    if valid_flashcards:
                        logger.info(f"Successfully parsed {len(valid_flashcards)} flashcards from JSON")
                        return valid_flashcards

            except json.JSONDecodeError as e:
                logger.info(f"JSON parsing failed: {str(e)}")

        # Secondary: Try to parse structured text format
        lines = response_text.split('\n')
        current_card = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith(('Q:', 'Question:', 'Front:')):
                if 'front' in current_card and 'back' in current_card:
                    # Save previous card before starting new one
                    front = current_card['front'].strip()
                    back = current_card['back'].strip()
                    if len(front) > 5 and len(back) > 5:
                        valid_flashcards.append({
                            'front': sanitize_text(front, 500),
                            'back': sanitize_text(back, 1000)
                        })

                current_card = {'front': line.split(':', 1)[1].strip()}

            elif line.startswith(('A:', 'Answer:', 'Back:')):
                if 'front' in current_card:
                    current_card['back'] = line.split(':', 1)[1].strip()

        # Don't forget the last card
        if 'front' in current_card and 'back' in current_card:
            front = current_card['front'].strip()
            back = current_card['back'].strip()
            if len(front) > 5 and len(back) > 5:
                valid_flashcards.append({
                    'front': sanitize_text(front, 500),
                    'back': sanitize_text(back, 1000)
                })

        if valid_flashcards:
            logger.info(f"Successfully parsed {len(valid_flashcards)} flashcards from structured text")
            return valid_flashcards

        # Tertiary: Last resort - try to extract key information
        logger.warning("Using fallback parsing method")
        sentences = [s.strip() for s in response_text.replace('\n', ' ').split('.') if len(s.strip()) > 20]

        if len(sentences) >= 2:
            # Create cards from pairs of sentences
            for i in range(0, min(len(sentences) - 1, 10), 2):  # Limit to 5 cards max
                front = sentences[i].strip()
                back = sentences[i + 1].strip()

                if len(front) > 10 and len(back) > 10:
                    valid_flashcards.append({
                        'front': sanitize_text(f"What can you tell me about: {front}?", 500),
                        'back': sanitize_text(back, 1000)
                    })

        if valid_flashcards:
            logger.info(f"Created {len(valid_flashcards)} flashcards using fallback method")
            return valid_flashcards

        # Ultimate fallback
        raise ValueError("Could not extract any valid flashcards from the response")

    except Exception as e:
        logger.error(f"Error in parse_claude_response: {str(e)}")
        # Create a single diagnostic flashcard
        return [{
            'front': f'Error processing {filename}',
            'back': f'The document was uploaded but could not be processed into flashcards. Error: {str(e)[:200]}'
        }]

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process with Claude API"""
    # Check if Anthropic client is available
    if client is None:
        return jsonify({
            'error': 'Anthropic client not initialized. Please check your ANTHROPIC_API_KEY configuration.'
        }), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Supported types: txt, pdf, doc, docx'}), 400

    # Validate file size with improved error handling
    is_valid_size, size_error = validate_file_size(file)
    if not is_valid_size:
        return jsonify({'error': size_error}), 400

    # Initialize variables for cleanup
    file_path = None
    document_id = None
    process_id = str(uuid.uuid4())

    try:
        # Save file temporarily with secure filename
        filename = secure_filename(file.filename)
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{process_id}_{filename}")

        # Save uploaded file
        try:
            file.save(file_path)
        except Exception as e:
            return jsonify({'error': f'Failed to save uploaded file: {str(e)}'}), 500

        # Create document record first
        try:
            file_size = os.path.getsize(file_path)
            document_id = create_document(filename, file_size, process_id)
            logger.info(f"Created document record with ID: {document_id} for file: {filename} ({file_size} bytes)")
        except Exception as e:
            logger.error(f"Failed to create document record for {filename}: {str(e)}")
            return jsonify({'error': f'Failed to create document record: {str(e)}'}), 500

        # Process document directly with Claude API (no OCR needed)
        try:
            logger.info(f"Processing document {filename} directly with Claude API")
            claude_response = process_document_with_claude(file_path, filename)
            logger.info(f"Received Claude response: {len(claude_response)} characters")
        except Exception as e:
            logger.error(f"Claude processing failed for {filename}: {str(e)}")
            return jsonify({'error': f'Claude processing failed: {str(e)}'}), 500

        # Parse flashcards from Claude response
        try:
            flashcards = parse_claude_response(claude_response, filename)
            if not flashcards or len(flashcards) == 0:
                return jsonify({'error': 'No valid flashcards could be extracted from the document'}), 400
            logger.info(f"Parsed {len(flashcards)} flashcards")
        except Exception as e:
            return jsonify({'error': f'Failed to parse flashcards: {str(e)}'}), 500

        # Store flashcards in database
        try:
            stored_count = 0
            for i, card in enumerate(flashcards):
                try:
                    create_flashcard(document_id, card['front'], card['back'])
                    stored_count += 1
                except Exception as e:
                    logger.warning(f"Failed to store flashcard {i+1}: {str(e)}")

            if stored_count == 0:
                return jsonify({'error': 'Failed to store any flashcards in database'}), 500

            logger.info(f"Successfully stored {stored_count} flashcards")
        except Exception as e:
            return jsonify({'error': f'Database storage failed: {str(e)}'}), 500

        # Clean up temporary file
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary file: {str(e)}")

        return jsonify({
            'message': f'Successfully processed {filename} and created {len(flashcards)} flashcards',
            'process_id': process_id,
            'document_id': document_id,
            'flashcards_count': len(flashcards),
            'flashcards': flashcards
        }), 200

    except Exception as e:
        # Comprehensive cleanup on any failure
        error_msg = f'Processing failed: {str(e)}'
        logger.error(f"Upload error: {error_msg}")

        # Clean up temporary file
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file after error: {file_path}")
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temporary file: {str(cleanup_error)}")

        return jsonify({'error': error_msg}), 500

@app.route('/flashcards/<process_id>', methods=['GET'])
def get_flashcards(process_id):
    """Get flashcards for a specific document by process_id"""
    # Validate process_id format
    if not validate_process_id(process_id):
        logger.warning(f"Invalid process_id format: {process_id}")
        return jsonify({'error': 'Invalid process ID format'}), 400

    try:
        logger.info(f"Retrieving flashcards for process_id: {process_id}")

        # Get document by process_id using the models function
        with app.app_context():
            conn = sqlite3.connect(app.config['DATABASE'])
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM documents WHERE process_id = ?", (process_id,))
            result = cursor.fetchone()
            conn.close()

            if not result:
                logger.info(f"Document not found for process_id: {process_id}")
                return jsonify({'error': 'Document not found'}), 404

            document_id = result[0]
            flashcards = get_flashcards_by_document(document_id)

            logger.info(f"Retrieved {len(flashcards)} flashcards for document_id: {document_id}")

            return jsonify({
                'process_id': process_id,
                'flashcards': flashcards
            })

    except Exception as e:
        logger.error(f"Error retrieving flashcards for process_id {process_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/documents', methods=['GET'])
def get_documents():
    """Get all processed documents"""
    try:
        documents = get_all_documents()
        return jsonify({'documents': documents})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = app.config['FLASK_PORT']
    logger.info(f"🌐 Starting Flask server on http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)