# RAG File Search System - Complete User Instructions

## 🚀 Quick Start Guide

### Prerequisites Checklist
- [ ] Python 3.10 or higher installed
- [ ] OpenAI API key obtained
- [ ] Modern web browser (Chrome, Firefox, Safari, Edge)
- [ ] Internet connection for OpenAI API access

### 5-Minute Setup

1. **Download and Setup**
   ```bash
   # Navigate to your project directory
   cd /Users/cpconnor/projects/RAG
   
   # Run the automated setup script
   ./setup_api_key.sh
   ```

2. **Configure Your API Key**
   - Get your API key from: https://platform.openai.com/api-keys
   - The setup script will guide you through configuration
   - Alternatively, manually edit `.env` file

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Application**
   ```bash
   python app.py
   ```

5. **Access the Web Interface**
   - Open your browser to: http://localhost:5001
   - You should see the RAG File Search System interface

## 📖 Detailed User Manual

### 🔧 System Administration

#### Initial Configuration
```bash
# Check system health
curl http://localhost:5001/health

# Verify API key is working
curl http://localhost:5001/api/test-api-key
```

#### Environment Configuration
Edit `.env` file for custom settings:
```bash
# Core Settings
OPENAI_API_KEY=your_actual_api_key_here
ENV=development  # or staging, production

# Performance Settings
CHUNK_SIZE=512
TIMEOUT=30
LOG_LEVEL=INFO

# Web Server Settings
FLASK_RUN_PORT=5001
MAX_CONTENT_LENGTH=16777216  # 16MB file limit
```

### 📁 Knowledge Base Management

#### Creating Knowledge Bases

**Method 1: Web Interface**
1. Navigate to the "Vector Stores" section
2. Enter a descriptive name (e.g., "Company Policies", "Technical Documentation")
3. Click "Create Vector Store"
4. Note the Vector Store ID for file uploads

**Method 2: API Command**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "My Knowledge Base"}' \
  http://localhost:5001/api/vector-stores
```

#### Managing Knowledge Bases

**List All Knowledge Bases**
```bash
curl http://localhost:5001/api/vector-stores
```

**Check Knowledge Base Status**
```bash
curl http://localhost:5001/api/vector-stores/{store_id}/status
```

**Delete Knowledge Base**
```bash
curl -X DELETE http://localhost:5001/api/vector-stores/{store_id}
```

### 📄 File Upload & Management

#### Supported File Types
- **Documents**: PDF, DOC, DOCX, TXT, RTF
- **Spreadsheets**: XLS, XLSX, CSV
- **Presentations**: PPT, PPTX
- **Web Content**: HTML, MD (Markdown)
- **Code**: PY, JS, JSON, XML, YAML

#### Upload Methods

**Method 1: Drag & Drop (Recommended)**
1. Select your target knowledge base
2. Drag files from your computer to the upload area
3. Watch the progress indicator
4. Confirm successful upload

**Method 2: File Browser**
1. Click "Choose Files" button
2. Select one or multiple files
3. Choose target knowledge base
4. Click "Upload"

**Method 3: URL Import**
1. Select "Upload from URL" option
2. Enter the complete URL (e.g., https://example.com/document.pdf)
3. Choose target knowledge base
4. Click "Upload from URL"

**Method 4: API Upload**
```bash
# Upload local file
curl -X POST -F "file=@/path/to/document.pdf" \
  -F "vector_store_id=vs_xxx" \
  http://localhost:5001/api/upload

# Upload from URL
curl -X POST -F "url=https://example.com/doc.pdf" \
  -F "vector_store_id=vs_xxx" \
  http://localhost:5001/api/upload
```

#### Upload Best Practices
- **File Size**: Keep files under 16MB for optimal performance
- **File Names**: Use descriptive names for better search results
- **Organization**: Group related documents in the same knowledge base
- **Quality**: Ensure documents are text-searchable (not scanned images)

### 🔍 Search Functionality

#### Search Types

**1. Semantic Search**
- **When to Use**: Finding documents similar to your query
- **Best For**: Broad topic exploration, finding related documents
- **Example Query**: "employee benefits policies"
- **Response**: List of relevant documents with similarity scores

**2. AI-Assisted Search**
- **When to Use**: Getting specific answers to questions
- **Best For**: Fact-finding, detailed explanations, analysis
- **Example Query**: "What is the maximum vacation time for senior employees?"
- **Response**: AI-generated answer with source citations

#### Search Interface

**Web Interface Search**
1. Select search type (Semantic or AI-Assisted)
2. Choose target knowledge bases (can select multiple)
3. Enter your query in natural language
4. Review results with source citations
5. Export results if needed

**API Search**
```bash
# Semantic search
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "marketing strategies", "search_type": "semantic", "vector_store_ids": ["vs_xxx"]}' \
  http://localhost:5001/api/search

# AI-assisted search
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "What are our Q4 revenue targets?", "search_type": "assisted", "vector_store_ids": ["vs_xxx"]}' \
  http://localhost:5001/api/search
```

#### Writing Effective Queries

**✅ Good Query Examples**
- "What is the approval process for capital expenditures over $50,000?"
- "Compare our product performance metrics from last quarter"
- "Find safety protocols for chemical handling in manufacturing"
- "What are the requirements for remote work eligibility?"

**❌ Avoid These Query Patterns**
- Single word searches ("sales")
- Overly complex technical jargon
- Questions about information not in your documents
- Requests for real-time data not in uploaded files

### 📊 Results Management

#### Understanding Results

**Semantic Search Results**
- Document titles and excerpts
- Relevance scores (0.0 to 1.0)
- Source file information
- Direct links to original documents

**AI-Assisted Search Results**
- Generated comprehensive answer
- Source citations with page/section references
- Confidence indicators
- Follow-up question suggestions

#### Export Options
- **JSON**: For programmatic processing
- **CSV**: For spreadsheet analysis
- **HTML**: For sharing and presentation
- **Text**: For simple text processing

### 🛠️ Advanced Features

#### Batch Operations

**Bulk File Upload**
```bash
# Upload multiple files from directory
for file in /path/to/documents/*; do
  curl -X POST -F "file=@$file" -F "vector_store_id=vs_xxx" \
    http://localhost:5001/api/upload
  sleep 2  # Rate limiting
done
```

#### Search Filtering
```bash
# Search with date filters (if supported by your documents)
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "budget reports", "filters": {"date_range": "2024"}}' \
  http://localhost:5001/api/search
```

#### Performance Monitoring
```bash
# Check system performance
curl http://localhost:5001/health

# Monitor knowledge base processing
curl http://localhost:5001/api/vector-stores/{store_id}/status
```

### 🔒 Security & Privacy

#### Data Protection
- All files are encrypted in transit to OpenAI
- API keys are stored securely in environment variables
- No data is permanently stored by OpenAI after processing
- Local file uploads are handled securely

#### Access Control
- Knowledge bases are isolated by ID
- API endpoints require proper authentication
- Audit logs track all system activities

#### Privacy Considerations
- Documents are processed by OpenAI's APIs
- Ensure compliance with your organization's data policies
- Consider on-premises deployment for highly sensitive data

### 🚨 Troubleshooting

#### Common Issues

**1. API Key Errors**
```bash
# Test API key
curl http://localhost:5001/api/test-api-key

# Fix: Check .env file or run setup script
./setup_api_key.sh
```

**2. File Upload Failures**
- Check file size (must be under 16MB)
- Verify file format is supported
- Ensure internet connection for OpenAI processing

**3. Search Not Working**
- Verify knowledge base contains processed files
- Check that vector store status is "completed"
- Ensure query is in English (other languages have limited support)

**4. Application Won't Start**
```bash
# Check dependencies
pip install -r requirements.txt

# Check port availability
lsof -i :5001

# Use different port
python app.py 5002
```

#### Getting Help

**1. Check Logs**
```bash
# Application logs show in terminal
python app.py

# Check for error messages in browser console (F12)
```

**2. Validate Configuration**
```bash
# Check all settings
cat .env

# Test system health
curl http://localhost:5001/health
```

**3. Reset and Restart**
```bash
# Stop application (Ctrl+C)
# Clear any cached data
rm -rf __pycache__/
# Restart
python app.py
```

### 📈 Best Practices

#### Document Organization
- Create separate knowledge bases for different topics
- Use consistent naming conventions
- Regularly update and remove outdated documents
- Maintain document quality (clear, well-formatted text)

#### Search Optimization
- Use specific, well-formed questions
- Include context in your queries
- Experiment with both search types for different needs
- Save frequently used queries for quick access

#### Performance Tips
- Upload files during off-peak hours for faster processing
- Monitor API usage to manage costs
- Regularly clean up unused knowledge bases
- Use semantic search for exploration, AI-assisted for specific answers

#### Cost Management
- Monitor OpenAI API usage through their dashboard
- Use local caching when possible
- Optimize document sizes before upload
- Set up usage alerts to prevent unexpected charges

---

## 🎯 Quick Reference Commands

```bash
# Setup and Start
./setup_api_key.sh
pip install -r requirements.txt
python app.py

# Health Checks
curl http://localhost:5001/health
curl http://localhost:5001/api/test-api-key

# Create Knowledge Base
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "My Docs"}' http://localhost:5001/api/vector-stores

# Upload File
curl -X POST -F "file=@document.pdf" \
  -F "vector_store_id=vs_xxx" http://localhost:5001/api/upload

# Search
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "your question", "search_type": "assisted", "vector_store_ids": ["vs_xxx"]}' \
  http://localhost:5001/api/search
```

**Support**: For technical issues, check the troubleshooting section or review the application logs for specific error messages.
