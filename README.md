# Business Intelligence & Knowledge Management Platform

A unified web application combining RAG file search capabilitie3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** to http://localhost:5001

## Analytics Integration

This platform integrates with the **Daily_Reporting** contact center analytics system to provide unified business intelligence capabilities.

### 🎯 **Integrated Features**

- **Business Intelligence Search**: Search across both documents and analytics reports with AI-powered insights
- **Unified Dashboard**: Combined document management and analytics visualization
- **Report Ingestion**: Automatic monitoring and processing of business reports
- **Cross-System Intelligence**: Correlate operational data with policy documents

### 📊 **Analytics Dashboard**

Access the analytics dashboard at `/analytics` to:

- **Monitor System Health**: Real-time status of both RAG and analytics systems
- **Business Intelligence Search**: AI-powered search combining document context with analytics insights
- **Report Management**: Upload, monitor, and process business reports
- **Performance Metrics**: View contact center analytics and operational insights

### 🔄 **Auto-Ingestion**

The system automatically monitors the `Daily_Reporting/reports/` directory for new business reports and processes them into the Business_Analytics_Reports knowledge base for unified search capabilities.ness analytics, featuring file upload, vector storage, AI-powered search, and contact center analytics integration.

## 📚 Documentation

- **[Quick Start Card](QUICK_START.md)** - 5-minute setup guide
- **[Executive Overview](EXECUTIVE_OVERVIEW.md)** - Business value, use cases, and ROI analysis
- **[Complete User Instructions](USER_INSTRUCTIONS.md)** - Detailed setup and usage guide
- **[Completion Summary](COMPLETION_SUMMARY.md)** - Technical implementation overview
- **[Integration Plan](INTEGRATION_PLAN.md)** - Analytics integration architecture and strategy

## 🎯 Use Cases

### 🏢 **Enterprise Knowledge Management**
Transform scattered documents into an intelligent knowledge base. Ask questions like "What is our remote work policy?" and get instant, accurate answers with source citations.

### 💼 **Customer Support Excellence** 
Enable support teams to instantly find product documentation and troubleshooting guides. Reduce response times and improve accuracy.

### 📊 **Business Analytics & Reporting**
Analyze contact center performance, customer interactions, and business metrics. Search through analytics reports and get AI-powered insights from your business data.

### 🔄 **Unified Intelligence Platform**
Combine document search with business analytics for comprehensive organizational intelligence. Cross-reference operational data with policy documents and procedures.

### 📋 **Compliance & Legal Research**
Search through contracts, regulations, and compliance documents with AI-powered precision. Essential for legal and compliance teams.

## ⚡ Quick Demo

```bash
# Get started in 5 minutes
./setup_api_key.sh && pip install -r requirements.txt && python app.py
# Open http://localhost:5001
```

## Features

### 📄 **Document Management**
- **File Upload**: Support for multiple file formats (PDF, TXT, DOCX, etc.)
- **URL Import**: Upload files directly from URLs  
- **Vector Storage**: Manage multiple vector stores for organized file collections
- **AI-Powered Search**: Two search modes:
  - **Semantic Search**: Direct vector similarity search
  - **AI-Assisted Search**: Generated responses with source citations

### 📊 **Business Analytics Integration**
- **Contact Center Analytics**: Integrated Daily_Reporting system for call center insights
- **Business Intelligence Search**: AI-powered search across both documents and analytics reports
- **Report Ingestion**: Automatic monitoring and processing of business reports
- **Unified Dashboard**: Combined view of document search and business analytics

### 🎨 **Modern Interface**
- **Responsive Design**: Bootstrap-based interface with drag-and-drop functionality
- **Real-time Updates**: Progress tracking and status monitoring
- **Export Results**: Export search results in multiple formats
- **Analytics Dashboard**: Comprehensive business intelligence interface

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   OpenAI API    │    │ Daily_Reporting │
│   (HTML/CSS/JS) │◄──►│   (Python)      │◄──►│   (Vector Store)│    │   (Analytics)   │
│                 │    │                 │    │                 │    │                 │
│ • Document UI   │    │ • RAG System    │    │ • Embeddings    │    │ • ML Analytics  │
│ • Analytics UI  │    │ • Analytics API │    │ • Chat API      │    │ • Contact Center│
│ • Unified Search│    │ • Integration   │    │ • Search        │    │ • Reports       │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   File System   │
                       │   (Local/Cloud) │
                       └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- **OpenAI API key** (required)
- Modern web browser

### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd RAG
   ./setup.sh
   ```

2. **Configure OpenAI API Key** (REQUIRED):
   
   **Option A: Automated Setup**
   ```bash
   ./setup_api_key.sh
   ```
   
   **Option B: Manual Setup**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env file and add your API key
   nano .env  # or use your preferred editor
   # Set: OPENAI_API_KEY=your_actual_api_key_here
   ```
   
   **Get your API key:**
   - Visit: https://platform.openai.com/api-keys
   - Sign in to your OpenAI account
   - Click "Create new secret key"
   - Copy the generated key and add it to your .env file

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and go to: http://localhost:5000

### Verify Setup

Test your API key connection:
```bash
curl http://localhost:5000/api/test-api-key
```

Expected response:
```json
{
  "status": "success",
  "message": "OpenAI API key is working correctly"
}
```
   nano .env
   
   # Add your OpenAI API key
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Run the application**:
   ```bash
   source .venv/bin/activate
   python app.py
   ```

4. **Access the web interface**:
   Open [http://localhost:5000](http://localhost:5000) in your browser

### Docker Deployment

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_api_key_here

# Run with Docker Compose
docker-compose up --build

# For production with nginx
docker-compose --profile production up --build
```

## Usage Guide

### 1. Vector Store Management

**Create a Vector Store**:
- Enter a name for your vector store
- Click "Create" to initialize it
- Vector stores organize your files into logical collections

**Select Vector Stores**:
- Click on vector stores to select them for searching
- Selected stores appear as badges in the search section

### 2. File Upload

**Upload Files**:
- Drag and drop files onto the upload area, or
- Click to browse and select files
- Supported formats: PDF, TXT, DOCX, DOC, MD

**Upload from URL**:
- Enter a direct file URL
- Click "Upload" to fetch and process the file

### 3. Search

**AI-Assisted Search** (Recommended):
- Generates comprehensive answers using AI
- Includes source citations and references
- Best for complex queries requiring synthesis

**Semantic Search**:
- Direct vector similarity matching
- Returns ranked document excerpts
- Best for finding specific information

**Search Tips**:
- Use specific keywords for better results
- Combine multiple concepts in queries
- Adjust max results for different use cases

### 4. Results Management

- **View Results**: Formatted responses with source references
- **Export**: Download results as JSON for further analysis
- **Clear**: Remove current results to start fresh

## API Reference

### Health Check
```http
GET /health
```

### Vector Stores
```http
GET /api/vector-stores              # List all stores
POST /api/vector-stores             # Create new store
DELETE /api/vector-stores/{id}      # Delete store
GET /api/vector-stores/{id}/status  # Get store status
```

### File Upload
```http
POST /api/upload
Content-Type: multipart/form-data

file: <file_data>                   # File upload
url: <file_url>                     # URL upload
vector_store_id: <store_id>         # Target store
```

### Search
```http
POST /api/search
Content-Type: application/json

{
  "query": "search query",
  "vector_store_ids": ["store1", "store2"],
  "search_type": "assisted|semantic",
  "max_results": 10
}
```

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional
FLASK_ENV=development|staging|production
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
MAX_FILE_SIZE=16777216  # 16MB default
UPLOAD_FOLDER=uploads
```

### Configuration Profiles

- **Development**: Debug mode, verbose logging
- **Staging**: Production-like with debug info
- **Production**: Optimized, minimal logging

## File Structure

```
RAG/
├── app.py                 # Flask application
├── config.py              # Configuration management
├── search_system.py       # Main search orchestration
├── file_manager.py        # File upload handling
├── vector_store_manager.py # Vector store operations
├── search_interface.py    # Search implementations
├── templates/
│   └── index.html         # Web interface
├── static/
│   ├── css/styles.css     # Styling
│   └── js/script.js       # Frontend logic
├── tests/
│   ├── test_*.py          # Unit tests
│   └── test_integration.py # Integration tests
├── .env.*                 # Environment configs
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container config
├── docker-compose.yml    # Multi-container setup
└── README.md             # This file
```

## Development

### Running Tests

```bash
# Unit tests
python -m pytest test_search_system.py -v

# Integration tests
python -m pytest test_integration.py -v

# All tests
python -m pytest -v
```

### Code Quality

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

### Adding Features

1. **Backend**: Extend classes in respective modules
2. **API**: Add routes in `app.py`
3. **Frontend**: Update HTML/CSS/JS in static files
4. **Tests**: Add corresponding test cases

## Troubleshooting

### Common Issues

**"No module named 'openai'"**
- Run: `pip install -r requirements.txt`

**"API key not found"**
- Check `.env` file has `OPENAI_API_KEY=your_key`
- Verify the key is valid and has credits

**"File upload failed"**
- Check file size limits (default 16MB)
- Verify file format is supported
- Ensure vector store is selected

**"Search returns no results"**
- Upload files to the selected vector stores first
- Wait for file processing to complete
- Try different search terms

### Performance Tips

- Use specific vector stores for searches
- Limit max results for faster responses
- Monitor file processing status
- Consider file size and complexity

### Getting Help

1. Check the browser console for JavaScript errors
2. Review application logs in `logs/` directory
3. Verify OpenAI API status and quotas
4. Test with simple queries first

## Security Considerations

- **API Keys**: Never commit API keys to version control
- **File Uploads**: Validate file types and sizes
- **HTTPS**: Use SSL/TLS in production
- **Access Control**: Implement authentication as needed

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub
