import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from flask import current_app

def get_db_connection():
    """Get database connection"""
    try:
        # Try to get from Flask app context
        database_path = current_app.config.get('DATABASE', 'flashcards.db')
    except RuntimeError:
        # Fallback for when called outside app context (e.g., during init)
        import os
        database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flashcards.db')

    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            process_id TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'completed'
        )
    ''')

    # Create flashcards table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
        )
    ''')

    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_process_id ON documents(process_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_flashcards_document_id ON flashcards(document_id)')

    conn.commit()
    conn.close()

def create_document(filename: str, file_size: int, process_id: str, status: str = 'completed') -> int:
    """Create a new document record and return its ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO documents (filename, file_size, process_id, status)
        VALUES (?, ?, ?, ?)
    ''', (filename, file_size, process_id, status))

    document_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return document_id

def create_flashcard(document_id: int, front: str, back: str) -> int:
    """Create a new flashcard and return its ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO flashcards (document_id, front, back)
        VALUES (?, ?, ?)
    ''', (document_id, front, back))

    flashcard_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return flashcard_id

def get_flashcards_by_document(document_id: int) -> List[Dict[str, Any]]:
    """Get all flashcards for a specific document"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, front, back, created_at
        FROM flashcards
        WHERE document_id = ?
        ORDER BY created_at ASC
    ''', (document_id,))

    rows = cursor.fetchall()
    conn.close()

    flashcards = []
    for row in rows:
        flashcards.append({
            'id': row['id'],
            'front': row['front'],
            'back': row['back'],
            'created_at': row['created_at']
        })

    return flashcards

def get_document_by_process_id(process_id: str) -> Optional[Dict[str, Any]]:
    """Get document by process_id"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, filename, file_size, upload_time, process_id, status
        FROM documents
        WHERE process_id = ?
    ''', (process_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'id': row['id'],
            'filename': row['filename'],
            'file_size': row['file_size'],
            'upload_time': row['upload_time'],
            'process_id': row['process_id'],
            'status': row['status']
        }
    return None

def get_all_documents() -> List[Dict[str, Any]]:
    """Get all documents with flashcard counts"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT d.id, d.filename, d.file_size, d.upload_time, d.process_id, d.status,
               COUNT(f.id) as flashcard_count
        FROM documents d
        LEFT JOIN flashcards f ON d.id = f.document_id
        GROUP BY d.id, d.filename, d.file_size, d.upload_time, d.process_id, d.status
        ORDER BY d.upload_time DESC
    ''')

    rows = cursor.fetchall()
    conn.close()

    documents = []
    for row in rows:
        documents.append({
            'id': row['id'],
            'filename': row['filename'],
            'file_size': row['file_size'],
            'upload_time': row['upload_time'],
            'process_id': row['process_id'],
            'status': row['status'],
            'flashcard_count': row['flashcard_count']
        })

    return documents

def delete_document(document_id: int) -> bool:
    """Delete a document and all its flashcards"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Delete flashcards first (due to foreign key constraint)
        cursor.execute('DELETE FROM flashcards WHERE document_id = ?', (document_id,))

        # Delete document
        cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))

        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_document_status(process_id: str, status: str) -> bool:
    """Update document status"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE documents
        SET status = ?
        WHERE process_id = ?
    ''', (status, process_id))

    conn.commit()
    success = cursor.rowcount > 0
    conn.close()

    return success

def get_flashcard_by_id(flashcard_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific flashcard by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT f.id, f.front, f.back, f.created_at, f.document_id,
               d.filename
        FROM flashcards f
        JOIN documents d ON f.document_id = d.id
        WHERE f.id = ?
    ''', (flashcard_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'id': row['id'],
            'front': row['front'],
            'back': row['back'],
            'created_at': row['created_at'],
            'document_id': row['document_id'],
            'filename': row['filename']
        }
    return None