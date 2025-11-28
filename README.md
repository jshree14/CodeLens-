# CodeLens AI

An intelligent code analysis platform powered by AI that provides comprehensive code review, quality assessment, and real-time execution across multiple programming languages.

![CodeLens AI](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![React](https://img.shields.io/badge/react-18.0+-blue)

## Features

- **Multi-Language Support**: Python, JavaScript, Java, and C++
- **AI-Powered Analysis**: Leverages Google Gemini for intelligent code insights
- **Static Code Analysis**: Comprehensive quality checks and metrics
- **Real-Time Execution**: Safe code execution with output capture
- **Quality Scoring**: 0-100 score based on multiple factors
- **Security Analysis**: Identifies potential security vulnerabilities
- **Performance Suggestions**: Optimization recommendations
- **Modern UI**: Beautiful, responsive interface with animations

## Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **MongoDB**: Document database for analysis history
- **Google Gemini AI**: Advanced code analysis
- **Motor**: Async MongoDB driver

### Frontend
- **React**: Modern UI library
- **Vite**: Fast build tool
- **Framer Motion**: Smooth animations
- **Tailwind CSS**: Utility-first styling

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB
- Google Gemini API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/codelens-ai.git
cd codelens-ai
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

3. **Frontend Setup**
```bash
npm install
```

4. **Start MongoDB**
```bash
# Make sure MongoDB is running on localhost:27017
mongod
```

5. **Run the Application**

Terminal 1 (Backend):
```bash
cd backend
python main.py
```

Terminal 2 (Frontend):
```bash
npm run dev
```

6. **Access the Application**
```
http://localhost:3000
```

## Usage Examples

### Python Example
```python
def fibonacci(n):
    """Calculate Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Test
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### JavaScript Example
```javascript
function isPrime(num) {
    if (num < 2) return false;
    for (let i = 2; i <= Math.sqrt(num); i++) {
        if (num % i === 0) return false;
    }
    return true;
}

// Test
console.log(isPrime(17)); // true
```

### Java Example
```java
public class Calculator {
    public static void main(String[] args) {
        int result = add(5, 3);
        System.out.println("5 + 3 = " + result);
    }
    
    public static int add(int a, int b) {
        return a + b;
    }
}
```

### C++ Example
```cpp
#include <iostream>
using namespace std;

int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

int main() {
    cout << "5! = " << factorial(5) << endl;
    return 0;
}
```

## API Documentation

### Analyze Code
```bash
POST /api/analyze
Content-Type: application/json

{
    "code": "print('Hello World')",
    "language": "python",
    "execute": true
}
```

### Response
```json
{
    "summary": {
        "score": 95,
        "purpose": "Simple output statement",
        "overview": "Basic Python print statement"
    },
    "execution": {
        "output": "Hello World",
        "success": true,
        "execution_time": 0.05
    },
    "issues": [],
    "improvements": [],
    "metrics": {
        "lines": 1,
        "complexity": 1
    }
}
```

### Other Endpoints

- `GET /api/health` - Health check
- `GET /api/report` - Analysis history
- `GET /api/cache/stats` - Cache statistics
- `POST /api/cache/clear` - Clear cache

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=codelens_ai

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## Architecture

```
codelens-ai/
├── backend/
│   ├── analyzers/          # Code analysis engines
│   │   ├── ai_analyzer.py  # AI-powered analysis
│   │   └── static_analyzer.py
│   ├── executors/          # Code execution
│   │   └── code_executor.py
│   ├── routes/             # API endpoints
│   │   └── api.py
│   ├── utils/              # Utilities
│   ├── cache.py            # Caching layer
│   ├── database.py         # MongoDB operations
│   ├── models.py           # Data models
│   └── main.py             # Application entry
├── src/
│   ├── components/         # React components
│   │   ├── CodeEditor.jsx
│   │   ├── AnalysisResults.jsx
│   │   └── Dashboard.jsx
│   ├── App.jsx
│   └── main.jsx
└── README.md
```

## Features in Detail

### Code Analysis
- **Syntax Checking**: Validates code structure
- **Complexity Analysis**: Cyclomatic complexity calculation
- **Code Metrics**: Lines, functions, classes, etc.
- **Quality Indicators**: Documentation, error handling, naming conventions

### AI Insights
- **Purpose Detection**: Understands code intent
- **Bug Detection**: Identifies potential issues
- **Improvement Suggestions**: Actionable recommendations
- **Security Analysis**: Vulnerability detection
- **Performance Tips**: Optimization suggestions

### Code Execution
- **Safe Execution**: Sandboxed environment
- **Timeout Protection**: 5-second limit
- **Output Capture**: stdout and stderr
- **Error Handling**: Comprehensive error messages

### Performance
- **Caching**: In-memory cache for repeated analyses
- **Rate Limiting**: 30 requests/minute per IP
- **Database Indexing**: Optimized queries
- **Parallel Processing**: Concurrent analysis

## Development

### Project Structure
```
backend/
├── analyzers/      # Analysis engines
├── executors/      # Code execution
├── routes/         # API routes
├── utils/          # Helper functions
└── tests/          # Unit tests

src/
├── components/     # React components
├── contexts/       # React contexts
└── styles/         # CSS files
```

### Adding a New Language

1. Add language detector in `utils/language_detector.py`
2. Implement executor in `executors/code_executor.py`
3. Add static analysis rules in `analyzers/static_analyzer.py`
4. Update frontend language selector

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
npm test
```

## Deployment

### Docker (Recommended)

```bash
# Build
docker-compose build

# Run
docker-compose up
```

### Manual Deployment

1. Set up production MongoDB
2. Configure environment variables
3. Build frontend: `npm run build`
4. Run backend with gunicorn
5. Serve frontend with nginx

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Google Gemini AI for intelligent code analysis
- FastAPI for the excellent web framework
- React community for amazing tools and libraries

## Support

For issues and questions:
- Open an issue on GitHub
- Email: support@codelens-ai.com

## Roadmap

- [ ] More language support (Go, Rust, PHP)
- [ ] User authentication
- [ ] Team collaboration features
- [ ] Custom analysis rules
- [ ] IDE plugins
- [ ] CI/CD integration

---

Built with ❤️ by developers, for developers
