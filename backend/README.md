# CodeLens AI Backend

AI-powered Intelligent Code Review Dashboard backend built with FastAPI.

## Features

- **AI Analysis**: Uses Google Gemini AI for intelligent code quality assessment
- **Static Analysis**: Performs complexity analysis, syntax checking, and code metrics
- **Multi-language Support**: Python, JavaScript, TypeScript, Java, C++, Go, Rust
- **MongoDB Integration**: Stores analysis history and results
- **RESTful API**: Clean API endpoints for frontend integration
- **CORS Support**: Ready for React frontend integration

## Project Structure

```
backend/
├── analyzers/
│   ├── __init__.py
│   ├── ai_analyzer.py          # AI-powered code analysis
│   └── static_analyzer.py      # Static code analysis
├── routes/
│   ├── __init__.py
│   └── api.py                  # API route definitions
├── utils/
│   ├── __init__.py
│   └── language_detector.py    # Programming language detection
├── models.py                   # MongoDB/Pydantic models
├── database.py                 # Database operations
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
└── README.md                  # This file
```

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install MongoDB (optional):**
   - For full functionality, install MongoDB locally or use MongoDB Atlas
   - The app will work without MongoDB but won't persist analysis results

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Google Gemini API key (optional - uses mock analysis if not provided)
- `MONGODB_URL`: MongoDB connection string (default: mongodb://localhost:27017)
- `DATABASE_NAME`: Database name (default: codelens_ai)
- `COLLECTION_NAME`: Collection name (default: analysis_results)

### MongoDB Setup

If using MongoDB locally:
```bash
# Install MongoDB Community Edition
# Start MongoDB service
mongod --dbpath /path/to/your/db
```

For MongoDB Atlas (cloud):
```bash
# Use connection string in MONGODB_URL
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/codelens_ai
```

## Running the Server

### Development Mode
```bash
python main.py
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### POST /api/analyze
Analyze code and return comprehensive results.

**Request:**
```json
{
  "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
  "language": "python",
  "user_id": "optional_user_id",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "id": "analysis_id",
  "summary": {
    "purpose": "Calculates factorial using recursion",
    "overview": "Simple recursive implementation...",
    "score": 85
  },
  "issues": [
    {
      "title": "Missing Docstring",
      "description": "Function lacks documentation",
      "severity": "warning",
      "suggestion": "Add docstring to describe function",
      "source": "static"
    }
  ],
  "metrics": {
    "lines": 4,
    "functions": 1,
    "classes": 0,
    "loops": 0,
    "conditions": 1,
    "complexity": 2
  },
  "language": "python",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### GET /api/report
Get analysis history and statistics.

**Query Parameters:**
- `user_id` (optional): Filter by user
- `days` (optional): Number of days to include (default: 30)

**Response:**
```json
{
  "total_analyses": 25,
  "languages_used": ["python", "javascript", "java"],
  "average_score": 78.5,
  "recent_analyses": [...],
  "language_stats": {
    "python": 15,
    "javascript": 8,
    "java": 2
  }
}
```

### GET /api/analysis/{analysis_id}
Get specific analysis result by ID.

### GET /api/languages
Get supported programming languages.

### GET /api/health
Health check endpoint.

## Code Analysis Features

### AI Analysis (ai_analyzer.py)
- **Purpose Detection**: Identifies what the code does
- **Quality Assessment**: Evaluates code quality and structure
- **Issue Detection**: Finds logic issues and improvement opportunities
- **Scoring**: Provides 0-100 quality score
- **Mock Mode**: Works without Gemini API key for development

### Static Analysis (static_analyzer.py)
- **Syntax Checking**: Detects syntax errors
- **Complexity Metrics**: Calculates cyclomatic complexity
- **Code Metrics**: Lines, functions, classes, loops, conditions
- **Language-specific Analysis**: Python (AST + Pylint), JavaScript patterns
- **Performance**: Fast analysis without external API calls

### Language Detection (language_detector.py)
- **Auto-detection**: Identifies programming language from code patterns
- **Multi-language Support**: 10+ programming languages
- **Fallback Logic**: Graceful handling of unknown languages

## Database Schema

### CodeAnalysisResult
```python
{
  "_id": ObjectId,
  "code_snippet": str,          # First 1000 chars of analyzed code
  "language": str,              # Programming language
  "summary": {
    "purpose": str,             # What the code does
    "overview": str,            # Detailed analysis
    "score": int               # Quality score 0-100
  },
  "issues": [                  # Array of detected issues
    {
      "title": str,
      "description": str,
      "severity": str,          # error, warning, info
      "suggestion": str,
      "source": str            # static, ai
    }
  ],
  "metrics": {
    "lines": int,
    "functions": int,
    "classes": int,
    "loops": int,
    "conditions": int,
    "complexity": int
  },
  "created_at": datetime,
  "user_id": str,              # Optional user identifier
  "session_id": str            # Optional session grouping
}
```

## Development

### Adding New Language Support

1. **Update language_detector.py:**
   ```python
   patterns = {
       'your_language': [
           r'pattern1',
           r'pattern2'
       ]
   }
   ```

2. **Extend static_analyzer.py:**
   ```python
   async def _analyze_your_language(self, code: str):
       # Language-specific analysis logic
       pass
   ```

### Adding New Analysis Features

1. **Extend analyzers** with new detection logic
2. **Update models.py** if new data fields are needed
3. **Update API responses** in routes/api.py

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when test files are created)
pytest
```

## Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
```bash
GEMINI_API_KEY=your_production_key
MONGODB_URL=your_production_mongodb_url
DEBUG=False
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check MongoDB is running
   - Verify connection string in .env
   - Check network connectivity

2. **Gemini API Errors**
   - Verify API key is valid
   - Check API quota and billing
   - App falls back to mock analysis automatically

3. **Pylint Not Found**
   - Install pylint: `pip install pylint`
   - Static analyzer works without pylint but with reduced features

4. **CORS Issues**
   - Update CORS_ORIGINS in environment
   - Check frontend URL matches allowed origins

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## License

MIT License - see LICENSE file for details.