# DealFinder AI

A Python-based chatbot that finds the best deals across multiple shopping sites using natural language queries and the Gemini API.

## Features

- **Natural Language Understanding**: Uses Google's Gemini API to understand complex shopping queries
- **Multi-Source Search**: Searches across Amazon, Walmart, and eBay to find the best deals
- **Intelligent Ranking**: Ranks products based on price, ratings, shipping options, and more
- **Multiple Interfaces**: Works in both terminal mode and as a web service
- **Real Web Scraping**: Option to use real web scraping or mock data for development
- **MCP Architecture**: Uses a multi-agent communication protocol for modular design

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (sign up at [Google AI Studio](https://ai.google.dev/))

### From Source

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

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

### Using pip

```bash
pip install dealfinder-ai
```

After installation, create a `.env` file in your working directory with your Gemini API key.

## Usage

### Terminal Interface

Run the chatbot in terminal mode:

```bash
# Using real web scrapers
dealfinder --real-scrapers

# Using mock scrapers (faster for development)
dealfinder
```

### Web Interface

Run the chatbot as a web service:

```bash
# Using real web scrapers
dealfinder --web --real-scrapers

# Using mock scrapers
dealfinder --web
```

Then open a browser and go to http://localhost:5000

### Command Line Options

```
usage: dealfinder [-h] [--api-key API_KEY] [--web] [--port PORT] [--real-scrapers]

DealFinder AI - Find the best deals online

options:
  -h, --help           show this help message and exit
  --api-key API_KEY    Gemini API Key (optional, can also use GEMINI_API_KEY env var)
  --web                Run as a web service instead of terminal
  --port PORT          Port for web service (default: 5000)
  --real-scrapers      Use real web scrapers instead of mock implementations
```

## Example Queries

- "Find me the best deals on wireless headphones"
- "I need a budget laptop for college under $500"
- "What are the top-rated coffee makers on sale right now?"
- "Show me the cheapest gaming keyboards with mechanical switches"
- "Find deals on 4K monitors with USB-C"

## Project Structure

```
dealfinder-ai/
├── dealfinder/                  # Main package directory
│   ├── __init__.py              # Package initialization
│   ├── agents/                  # All agent implementations
│   │   ├── __init__.py
│   │   ├── base.py              # Base Agent and MCPMessage classes
│   │   ├── gemini_agent.py      # Gemini API integration
│   │   ├── aggregator_agent.py  # Results aggregation and ranking
│   │   ├── presentation_agent.py # Result presentation formatting
│   │   └── scrapers/            # Scraper implementations
│   │       ├── __init__.py
│   │       ├── amazon.py        # Amazon scraper implementation
│   │       ├── walmart.py       # Walmart scraper implementation
│   │       ├── ebay.py          # eBay scraper implementation
│   │       └── mock/            # Mock implementations for testing
│   ├── controller.py            # Main controller class
│   ├── config.py                # Configuration settings
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── logging.py           # Logging configuration
│       └── parsing.py           # Text parsing utilities
├── templates/                   # Web interface templates
│   └── index.html               # Main HTML template
├── static/                      # Static web assets
├── main.py                      # Main entry point script
├── setup.py                     # Package setup file
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## Extending the Project

### Adding New Shopping Sites

1. Create a new scraper agent class in `dealfinder/agents/scrapers/`
2. Implement the required methods (similar to existing scrapers)
3. Update the `get_scraper_agents` function in `dealfinder/agents/scrapers/__init__.py`
4. Add the new scraper to the controller in `dealfinder/controller.py`

### Improving the Ranking Algorithm

Modify the `_rank_products` method in `dealfinder/agents/aggregator_agent.py` to adjust how products are scored and ranked.

### Enhancing the User Interface

- Terminal UI: Modify the presentation formatting in `dealfinder/agents/presentation_agent.py`
- Web UI: Update the HTML/CSS/JS in the `templates` and `static` directories

## Web Scraping Notice

This project includes functionality for scraping public product information from e-commerce websites. When using the real web scrapers, please be respectful of the websites' terms of service and implement appropriate rate limiting and caching to minimize server load.

The mock scrapers are provided as an alternative for development and testing purposes.

## License

MIT

## Acknowledgments

- Google Gemini API for natural language processing
- BeautifulSoup and requests for web scraping capabilities
- Flask for the web interface
- Rich for beautiful terminal output
