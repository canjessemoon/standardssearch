# 🤖 LLM-Enhanced Document Search

Your document search tool now supports **AI-powered semantic search** and **natural language querying**! This upgrade transforms your keyword-based search into an intelligent assistant that can understand context and provide meaningful answers.

## 🎯 What's New

### 1. **AI Chat Interface** 
- Ask questions in natural language
- Get intelligent responses based on document content
- Automatic context extraction and relevance scoring
- Source attribution with page numbers

### 2. **Semantic Search**
- Find relevant content even when exact keywords don't match
- Understanding of synonyms and related concepts
- Vector-based similarity matching

### 3. **Hybrid Search**
- Combines keyword search with AI analysis
- Best of both worlds: precision + intelligence

## 🚀 Quick Start

### Option 1: Automatic Setup
```powershell
.\setup_llm.ps1
```

### Option 2: Manual Setup
1. **Install dependencies:**
   ```bash
   pip install openai tiktoken scikit-learn
   ```

2. **Get OpenAI API key:**
   - Visit https://platform.openai.com/api-keys
   - Create a new API key

3. **Set environment variable:**
   ```powershell
   $env:OPENAI_API_KEY = "your-api-key-here"
   ```

4. **Restart backend server:**
   ```bash
   cd backend
   python -m app.main
   ```

## 💬 Using the AI Assistant

### Example Queries:
```
"What are the safety requirements for head clearance?"
"Explain procedures for preventing accidental activation"
"What noise level standards apply to equipment design?"
"How should emergency controls be positioned?"
"What materials are recommended for high-temperature applications?"
```

### Features:
- **Context-Aware**: Understands technical terminology and relationships
- **Source Attribution**: Shows which documents and pages contain answers
- **Multi-Document**: Searches across all selected documents simultaneously
- **Relevance Scoring**: Ranks results by semantic similarity

## 🔧 API Endpoints

### Chat Interface
```bash
POST /api/llm/chat
{
  "query": "What are the head clearance requirements?",
  "documents": ["MIL-STD-1472H.pdf"]
}
```

### Enhanced Search (with LLM analysis)
```bash
POST /api/search
{
  "query": "safety procedures",
  "use_llm": true,
  "documents": [],
  "language": "en"
}
```

### Check LLM Status
```bash
GET /api/llm/status
```

### Create Semantic Index
```bash
POST /api/llm/index
```

## 📊 How It Works

### 1. **Document Processing**
- PDF content is chunked into semantically meaningful sections
- Each chunk gets converted to vector embeddings
- Embeddings capture semantic meaning, not just keywords

### 2. **Query Processing** 
- User questions are converted to vector embeddings
- Cosine similarity finds most relevant document sections
- Results are ranked by relevance score

### 3. **AI Analysis**
- GPT analyzes the user question and relevant context
- Generates human-readable answers with citations
- Maintains accuracy by staying grounded in document content

### 4. **Hybrid Results**
- Combines traditional keyword matches with semantic results
- Provides both specific quotes and contextual understanding

## 🛠️ Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_api_key_here          # Required for LLM features
OPENAI_MODEL=gpt-3.5-turbo                # Optional: specify model
EMBEDDING_MODEL=text-embedding-ada-002     # Optional: specify embedding model
```

### Customization Options
- **Models**: Switch between GPT-3.5-turbo, GPT-4, etc.
- **Chunk Size**: Adjust document chunking (default: 800 tokens)
- **Similarity Threshold**: Tune relevance filtering (default: 0.7)
- **Max Results**: Control number of results returned (default: 10)

## 💰 Cost Considerations

### Token Usage:
- **Embeddings**: ~$0.0001 per 1K tokens (one-time indexing cost)
- **Chat**: ~$0.001-0.03 per 1K tokens (depending on model)
- **Typical Query**: $0.01-0.05 per question

### Cost Control:
- Embeddings are cached (create once, use many times)
- Context is truncated to stay under token limits
- Choose appropriate model for your use case

## 🔍 Comparison: Before vs After

### Traditional Search:
```
Query: "head clearance"
Results: Exact keyword matches only
❌ Misses: "cranial space", "overhead room", "vertical spacing"
```

### AI-Enhanced Search:
```
Query: "head clearance requirements"
Results: 
✅ Direct matches: "head clearance"
✅ Related concepts: "overhead space", "vertical clearance"
✅ Contextual understanding: safety requirements, design standards
✅ Intelligent summary: "Head clearance must be minimum 76 inches according to MIL-STD-1472H, Section 5.8.2..."
```

## 🚨 Troubleshooting

### "LLM capabilities not available"
- Run `pip install openai tiktoken scikit-learn`
- Restart backend server

### "API key not configured" 
- Set `OPENAI_API_KEY` environment variable
- Check API key is valid at https://platform.openai.com

### "Rate limit exceeded"
- Your API key has usage limits
- Upgrade your OpenAI plan or wait for reset

### Slow responses
- Embeddings are being created (one-time process)
- Try smaller document sets
- Use faster GPT-3.5-turbo instead of GPT-4

## 🔐 Security Notes

- API keys are stored as environment variables (not in code)
- No document content is sent to OpenAI for training
- All queries are processed through your API key
- Consider data privacy requirements for your organization

## 📈 Future Enhancements

Possible additions:
- **Local LLM Support** (Ollama, LlamaCpp)
- **Custom Embeddings** (domain-specific models)
- **Query History** and learning
- **Multi-language AI** (beyond translation)
- **Advanced Analytics** (trending topics, gaps)

---

**Ready to transform your document search? Run `.\setup_llm.ps1` and start asking questions! 🚀**
