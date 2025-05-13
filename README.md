# DealFinder AI

An intelligent shopping assistant that uses AI to help users find the best deals across multiple e-commerce platforms.

## Features

- Real-time web scraping from major e-commerce platforms (Amazon, Walmart, eBay)
- AI-powered product search optimization using Google Gemini
- Advanced relevance filtering and ranking
- Multi-agent architecture for modular and scalable design
- Real-time price comparison and deal detection
- Natural language query processing
- Detailed product information extraction

## Architecture

The system is built using a sophisticated Multi-Agent Communication Protocol (MCP) architecture designed for modularity and scalability:

### Core Components

1. **Scraping Agents**
   - **RealAmazonScraperAgent**
     - Uses Gemini AI for optimized search queries
     - Implements intelligent retry mechanisms
     - Extracts product data including:
       - ASIN (Amazon Standard Identification Number)
       - Product title and description
       - Price information
       - Image URLs
       - Review ratings
       - Availability status
     - Implements rate limiting and caching
     - Uses rotating user agents for reliability

   - **RealWalmartScraperAgent**
     - Gemini-powered search optimization
     - Extracts detailed product information
     - Handles Walmart's dynamic pricing
     - Supports bulk product data extraction
     - Implements session management

   - **RealEbayScraperAgent**
     - Optimized for eBay's search algorithms
     - Extracts auction and fixed-price listings
     - Handles seller ratings and shipping information
     - Supports multiple currency conversions
     - Implements auction-specific data extraction

2. **AI Components**
   - **Gemini Agent**
     - Natural language understanding
     - Query optimization
     - Product relevance scoring
     - Price trend analysis
     - Follow-up question handling

   - **LangChain Integration**
     - LangGraph workflow management
     - State management across conversations
     - Context-aware responses
     - Product comparison logic
     - Price trend analysis

3. **Agent Communication Protocol (MCP)**
   - Message-based communication between agents
   - Standard message formats:
     ```python
     class MCPMessage:
         sender: str
         receiver: str
         message_type: str
         data: Dict[str, Any]
     ```
   - Message types:
     - SEARCH_REQUEST
     - SEARCH_RESULTS
     - PRODUCT_DETAILS
     - PRICE_COMPARISON
     - FOLLOW_UP_REQUEST

4. **Data Flow**
   ```mermaid
   graph TD
       A[User Query] --> B[Query Parser]
       B --> C[Gemini Agent]
       C --> D[Search Optimizer]
       D --> E[Scraping Agents]
       E --> F[Results Aggregator]
       F --> G[Ranking Engine]
       G --> H[Response Generator]
   ```

### Key Features

1. **Smart Query Optimization**
   - Gemini-powered search term refinement
   - Context-aware query expansion
   - Platform-specific search optimization
   - Brand and feature detection

2. **Advanced Product Comparison**
   - Price normalization across platforms
   - Feature-based comparison
   - Review aggregation
   - Shipping cost analysis
   - Availability tracking

3. **Follow-up Conversations**
   - Context persistence
   - Product reference tracking
   - Comparative analysis
   - Price trend tracking
   - Detailed information retrieval

4. **Performance Optimization**
   - Caching mechanisms
   - Rate limiting
   - Parallel processing
   - Error handling and retries
   - Memory management

### Technical Details

1. **Scraping Implementation**
   - Uses BeautifulSoup and requests for web scraping
   - Implements intelligent retry mechanisms
   - Supports proxy rotation
   - Implements session management
   - Uses rotating user agents

2. **AI Integration**
   - Gemini API integration
   - LangChain workflow management
   - Context-aware responses
   - Follow-up question handling
   - Product comparison logic

3. **Performance Metrics**
   - Request rate limiting
   - Response time tracking
   - Error rate monitoring
   - Cache hit ratio
   - Memory usage optimization

## Requirements

- Python 3.8 or higher
- Google Gemini API key (sign up at [Google AI Studio](https://ai.google.dev/))

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dealfinder-ai.git
   cd dealfinder-ai
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment:
   - Set up your Google Gemini API key in the configuration
   - Configure any platform-specific settings in the config files

## Usage

The system can be used to:

1. Search for products across multiple platforms simultaneously
2. Get real-time price comparisons
3. Find the best deals based on various criteria
4. Get detailed product information including reviews and ratings

## Project Structure

```
dealfinder-ai/
├── dealfinder/
│   ├── agents/
│   │   ├── base.py          # Base agent class
│   │   ├── scraping/        # Web scraping agents
│   │   ├── presentation.py  # User interaction agent
│   │   └── gemini_agent.py  # Gemini integration
│   ├── langchain_integration/
│   │   └── graph.py         # Knowledge graph integration
│   └── utils/
│       └── logging.py       # Logging utilities
└── config/                  # Configuration files
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Uses Google Gemini for AI-powered features
- Built with Python and modern web scraping techniques
- Inspired by the need for better shopping assistants
