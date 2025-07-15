# LinChat
🌟 Vision: The Best Deep Research Product

Your goal:

→ Build the best AI-powered deep research co-pilot that:

✅ Handles complex research questions
✅ Combines:

Private documents (PDFs, Word, Excel, PPT, etc.)
Live web data (via browsing & scraping)
✅ Synthesizes insights into:

Structured reports
Slide decks
Tables
Charts
PDF exports
Excel files
✅ Provides traceable citations for every claim

✅ Works for teams (~5 users) with:

Collaboration
Document sharing
Access control
✅ Ensures data privacy & security

✅ Analysis is a backend process.

Users care only about results
Not the code or tech used
→ A true virtual research analyst for professionals.

🏆 Market Opportunity

Gap in the market:

Consumer chatbots → shallow, lack citations
Enterprise tools (e.g. AlphaSense) → expensive, inaccessible to SMBs
No solution today that:
Synthesizes multi-source insights
Handles private + public data seamlessly
Produces structured, export-ready deliverables
Is affordable and private
→ Huge mid-market opportunity:

Consultants
Analysts
NGOs
Strategy teams
Knowledge workers
Potential TAM → hundreds of millions globally.

💡 Key Product Differentiators

✅ 1. Multi-Source Synthesis
Fuses insights from:
Private documents
Web searches
Proprietary data
No other tool bridges both worlds this deeply.
✅ 2. Live Web Browsing
Scrapes web in real time
Extracts text, tables
Updates research with fresh info
→ Beyond static knowledge bases like ChatGPT.

✅ 3. Citations & Traceability
Every claim linked to:
Document snippets
URLs
Uses advanced techniques like:
ContextCite
Chunk-level tagging
Users can click to verify sources.
✅ 4. Structured Outputs
Not just chat replies.
Generates:
Executive summaries
Bullet lists
Tables
Charts
Slide decks
All exportable:
PDF
Excel
PowerPoint
✅ 5. Excel & Data Analysis
Upload Excel → parse into structured data
Run analysis:
CAGR
Summaries
Charts
Merges across sheets
Export:
New Excel files
Charts as images
All seamless → user never has to see code.
✅ 6. Backend Analysis Engine
Users want speed and results → not code.
Analysis implemented as:
Rust services (e.g. Polars for DataFrames)
High-speed charting
Result:
Blazing fast analysis
Low resource costs
Optionally expose code downloads for enterprise clients → but hidden for regular users.
✅ 7. Collaboration for Teams
Team-based permissions:
Private vs shared docs
Versioning
Shared research threads
Centralized knowledge hub
Audit trails for data security
✅ 8. Privacy-First Design
Self-hostable or private cloud
No user data leaks to public APIs
Encryption at rest & in transit
Full compliance (SOC2, GDPR, etc.)
→ A trusted research assistant.

🛠 Technical Blueprint

LLM Layer
Large-context models:
LLaMA-3-70B
Mistral-XXB
Open-source → avoid vendor lock-in
RAG pipeline:
Document retrieval
Chunking
Context injection
Web Browsing
Live scraping:
Playwright
Selenium
Scraped pages converted to:
Clean text
Embedded tables
Indexed in vector DB alongside private docs.
Vector Database
ChromaDB or Qdrant
Holds:
Document embeddings
Web page chunks
Enables semantic search.
Analysis Engine
Backend microservice:
Rust + Polars:
~10-30x faster than pandas
Low latency
Computes:
Aggregations
Charts
Statistical analyses
Returns:
Images (charts)
Tables
Summaries
Structured Output & Export
LLM generates:
JSON schemas for reports
Slide structures
Backend converts:
Markdown/HTML → PDF (WeasyPrint)
DataFrames → Excel
Slide JSON → PowerPoint
Frontend UI
Upload docs
Ask complex research questions
View:
Summaries
Charts
Data tables
Export:
PDF
Excel
PPT

## Getting Started

This repository contains the initial code for a FastAPI service that integrates with [OpenRouter](https://openrouter.ai/) for language model access. To run the development server:

```bash
pip install -r requirements.txt
export ADMIN_PASSWORD="your-password"
uvicorn app.main:app --reload
```

The admin interface is protected via HTTP basic auth. The default username is `admin` and the password is read from the `admin_password` field in `app/config.json` or the `ADMIN_PASSWORD` environment variable when first run. Navigate to `/admin` to update the OpenRouter API key used for LLM queries.
You can also set the model used for completions by editing the `openrouter_model` value in `app/config.json` or via the admin page.
