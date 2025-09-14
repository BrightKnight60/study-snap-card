# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Frontend Development
- **Start dev server**: `npm run dev` - Runs Vite development server with hot reload
- **Build for production**: `npm run build` - Creates optimized production build
- **Build for development**: `npm run build:dev` - Creates development build
- **Lint code**: `npm run lint` - Run ESLint on the codebase
- **Preview build**: `npm run preview` - Serve the production build locally
- **Install dependencies**: `npm i` - Install all project dependencies

### Backend Development
- **Install Python dependencies**: `cd backend && pip install -r requirements.txt`
- **Setup environment**: Copy `.env.example` to `backend/.env` and add your `ANTHROPIC_API_KEY`
- **Start backend server**: `cd backend && python run.py` - Runs Flask server on port 5001 (configurable)
- **Alternative backend start**: `cd backend && python app.py`

### Full Stack Development
1. **Setup backend environment**: Copy `.env.example` to `backend/.env` and configure
2. **Setup frontend environment**: Copy `.env.example.frontend` to `.env.local` (optional)
3. **Start backend**: `cd backend && python run.py` (runs on port 5001 by default)
4. **Start frontend**: `npm run dev` (in a separate terminal, runs on port 5173)
5. **Access app**: Frontend at `http://localhost:5173`, API at `http://localhost:5001`

### Troubleshooting

**Backend Issues:**
- **"Address already in use" or "Port 5000 is in use"**:
  - The default port is now 5001 to avoid macOS AirPlay conflicts
  - Customize port in `backend/.env`: `FLASK_PORT=5002`
- **"Client.__init__() got an unexpected keyword argument 'proxies'"**:
  - Run `pip install --upgrade anthropic` to update to version 0.45.2 or later
  - This error occurs with older Anthropic SDK versions incompatible with newer httpx
- **"ANTHROPIC_API_KEY not found"**:
  - Copy `.env.example` to `backend/.env`
  - Add your Anthropic API key: `ANTHROPIC_API_KEY=your_key_here`
- **Module import errors**:
  - Run `cd backend && pip install -r requirements.txt`
  - Consider using a virtual environment: `python -m venv venv && source venv/bin/activate`

**Frontend Issues:**
- **API connection errors**:
  - Ensure backend is running on the expected port (default 5001)
  - Check `VITE_API_BASE_URL` in `.env.local` if you changed the backend port
  - Verify CORS settings allow your frontend origin

## Architecture

This is a full-stack flashcard study application with a React frontend and Flask backend.

### Tech Stack

**Frontend:**
- **Vite**: Build tool and development server
- **React 18**: UI framework with hooks
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Component library built on Radix UI primitives
- **React Router**: Client-side routing
- **TanStack Query**: Data fetching and caching
- **React Hook Form + Zod**: Form handling and validation

**Backend:**
- **Flask**: Python web framework
- **Anthropic Claude API**: AI document processing and flashcard generation
- **SQLite**: Database for storing documents and flashcards
- **Flask-CORS**: Cross-origin resource sharing
- **PyPDF2**: PDF document processing
- **python-docx**: Word document processing

### Project Structure
```
├── src/                     # Frontend React application
│   ├── components/          # React components
│   │   ├── ui/              # shadcn/ui components (Button, Card, etc.)
│   │   ├── Flashcard.tsx    # Core flashcard component with flip animation
│   │   ├── StudyMode.tsx    # Study session management
│   │   └── CreateCardForm.tsx # Card creation and document upload interface
│   ├── pages/               # Page components
│   │   ├── Index.tsx        # Main application page
│   │   └── NotFound.tsx     # 404 page
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility functions
│   └── App.tsx             # Root application component
├── backend/                 # Flask backend application
│   ├── app.py              # Main Flask application with API endpoints
│   ├── models.py           # Database models and operations
│   ├── config.py           # Configuration management
│   ├── requirements.txt    # Python dependencies
│   └── run.py             # Backend startup script
├── .env.example            # Environment variables template
└── flashcards.db          # SQLite database (created automatically)
```

### Core Application Flow

**Frontend Flow:**
1. **Index.tsx** serves as the main application container, managing:
   - Flashcard data state (cards array)
   - Mode switching between "study" and "create"
   - Integration with backend for document processing

2. **CreateCardForm.tsx** provides dual functionality:
   - Manual flashcard creation with front/back text inputs
   - Document upload with automatic flashcard generation via Claude API

3. **Flashcard Component** provides:
   - Interactive 3D flip animation
   - Front/back card content display
   - CSS 3D transforms for smooth transitions

4. **Study Mode** handles:
   - Card navigation and progress tracking
   - Study session management
   - User interaction flow

**Backend Flow:**
1. **File Upload** (`POST /upload`):
   - Validates file size (5MB limit) and type (TXT, PDF, DOC, DOCX)
   - Extracts text content from documents
   - Sends content to Claude API with study prompt
   - Parses Claude response into flashcard format
   - Stores documents and flashcards in SQLite database

2. **Data Retrieval** (`GET /flashcards/<process_id>`):
   - Retrieves generated flashcards for specific document
   - Returns structured JSON for frontend consumption

### Backend API Endpoints
- `POST /upload` - Process document and generate flashcards
- `GET /flashcards/<process_id>` - Get flashcards for specific document
- `GET /documents` - List all processed documents
- `GET /health` - Health check endpoint

### State Management
- **Frontend**: Local React state for flashcard data
- **Backend**: SQLite database with documents and flashcards tables
- Cards stored as objects with id, front, back properties
- Document metadata tracked with process IDs

### Database Schema
```sql
documents (id, filename, file_size, upload_time, process_id, status)
flashcards (id, document_id, front, back, created_at)
```

### Claude API Integration
- **System Prompt**: Instructs Claude to act as a diligent student creating study notecards
- **User Prompt**: Provides document content and requests JSON flashcard format
- **Response Parsing**: Handles both JSON and fallback text parsing methods
- **Error Handling**: Graceful degradation for API failures

### Environment Configuration

**Backend Configuration (backend/.env):**
- **Required**: `ANTHROPIC_API_KEY` for Claude API access
- **Optional**: `FLASK_PORT` (default 5001), database path, upload folder, file size limits
- **CORS**: Configured for local development (localhost:5173)

**Frontend Configuration (.env.local):**
- **Optional**: `VITE_API_BASE_URL` (default http://localhost:5001)
- Automatically detects backend URL from environment variables

### Document Processing with Claude API
- **Direct Document Processing**: Files are sent directly to Claude API without OCR
- **PDF**: Native Claude processing (no extraction needed)
- **DOC/DOCX**: Native Claude processing via document API
- **TXT**: Native Claude processing
- **Base64 Encoding**: Files encoded for secure API transmission
- **Enhanced Model**: Using claude-sonnet-4-20250514 for optimal results