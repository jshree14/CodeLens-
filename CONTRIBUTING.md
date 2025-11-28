# Contributing to CodeLens AI

Thank you for your interest in contributing to CodeLens AI! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/codelens-ai.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit: `git commit -m "Add: your feature description"`
7. Push: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
npm install
npm run dev
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Maximum line length: 100 characters

### JavaScript/React
- Use ES6+ features
- Follow Airbnb style guide
- Use functional components
- Add PropTypes or TypeScript

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

## Commit Messages

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

Example: `feat: add support for Go language`

## Pull Request Process

1. Update README.md if needed
2. Add tests for new features
3. Ensure CI passes
4. Request review from maintainers
5. Address review comments
6. Squash commits if requested

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

## Questions?

Open an issue or reach out to the maintainers.

Thank you for contributing! 🎉
