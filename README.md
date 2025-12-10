# Library Desk Agent 📚

An AI-powered chat interface for library management using LangChain, OpenAI, FastAPI, and Streamlit.

## Features

- 🤖 **AI Agent** powered by OpenAI and LangChain
- 📖 **Book Search** by title or author
- 🛒 **Order Management** - Create and track customer orders
- 📦 **Inventory Control** - Restock books and update prices
- 📊 **Inventory Reports** - View low-stock items
- 💬 **Chat Interface** - Natural language interaction with Streamlit
- 🗄️ **SQLite Database** - Lightweight local storage
- 📝 **Session Management** - Multiple chat sessions with history

## Project Structure

```
library-desk-agent/
├── app/                      # Streamlit frontend
│   └── main.py              # Chat UI
├── server/                   # FastAPI backend
│   ├── main.py              # API server
│   ├── agent/               # LangChain agent
│   │   ├── agent.py         # Agent setup
│   │   └── tools.py         # Tool definitions
│   └── database/            # Database layer
│       ├── db.py            # Database queries
│       └── models.py        # Pydantic models
├── db/                      # Database files
│   ├── schema.sql           # Table definitions
│   ├── seed.sql             # Sample data
│   ├── init_db.py           # DB initialization script
│   └── library.db           # SQLite database (generated)
├── prompts/                 # LLM prompts
│   └── system_prompt.txt    # Agent system prompt
├── requirements.txt         # Python dependencies
├── env.example              # Environment template
└── README.md               # This file
```

## Prerequisites

- Python 3.9 or higher
- OpenAI API key (get one at https://platform.openai.com/)

## Installation

### 1. Clone or Download the Project

```bash
cd library-desk-agent
```

### 2. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv MenaDevs
MenaDevs\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv MenaDevs
source MenaDevs/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file by copying the example:

```bash
# Windows
copy env.example .env

# macOS/Linux
cp env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 5. Initialize Database

```bash
python db/init_db.py
```

You should see:
```
✅ Database initialized successfully!
   📚 Books: 10
   👥 Customers: 6
   📦 Orders: 4
```

## Running the Application

You need to run **two** servers: the backend API and the frontend UI.

### Terminal 1: Start Backend Server

```bash
python server/main.py
```

Expected output:
```
🚀 Starting Library Desk Agent API on http://127.0.0.1:8000
📚 Database: ./db/library.db
🤖 LLM Model: gpt-4o-mini
```

### Terminal 2: Start Frontend UI

Open a **new terminal** (keep the backend running):

```bash
streamlit run app/main.py
```

The Streamlit app will open in your browser at: `http://localhost:8501`

## Usage

### Starting a New Chat

1. Click **"➕ New Session"** in the sidebar
2. Start typing your questions in the chat input

### Sample Queries

Try these example queries:

**Search Books:**
```
Find books by Robert Martin
Show me all books by Andrew Hunt
```

**Create Orders:**
```
We sold 3 copies of Clean Code to customer 2 today. Create the order and adjust stock.
Customer 1 wants to buy 2 copies of Effective Java
```

**Inventory Management:**
```
Restock The Pragmatic Programmer by 10
Update the price of Clean Code to 45.99
Show me all low-stock items
```

**Order Status:**
```
What's the status of order 3?
Show me details for order 1
```

### Session Management

- **Recent Sessions**: View and switch between previous conversations
- **Session History**: All messages are saved and restored when you switch sessions
- **New Session**: Start fresh conversations anytime

## Available Tools

The agent has access to these tools:

| Tool | Description | Example |
|------|-------------|---------|
| `find_books` | Search by title or author | "Find books by Martin" |
| `create_order` | Create order and reduce stock | "Create order for customer 2: 1x Clean Code" |
| `restock_book` | Add stock to inventory | "Restock ISBN 978-0132350884 by 10" |
| `update_price` | Change book price | "Update price of Clean Code to 49.99" |
| `order_status` | Get order details | "Status of order 3" |
| `inventory_summary` | Show low-stock items | "Show inventory summary" |

## Database Schema

### Domain Tables

**books**
- isbn (PK), title, author, price, stock

**customers**
- id (PK), name, email

**orders**
- id (PK), customer_id (FK), status, created_at

**order_items**
- id (PK), order_id (FK), isbn (FK), quantity, price_at_purchase

### Chat Storage

**sessions**
- id (PK), created_at, updated_at

**messages**
- id (PK), session_id (FK), role, content, created_at

**tool_calls**
- id (PK), session_id (FK), tool_name, args_json, result_json, created_at

## Seed Data

The database comes pre-populated with:

- **10 Books**: Programming classics (Clean Code, Pragmatic Programmer, etc.)
- **6 Customers**: Sample customers with emails
- **4 Orders**: Example past orders

## Configuration

Edit `.env` to customize:

```env
# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4o, gpt-3.5-turbo

# Server
BACKEND_PORT=8000
BACKEND_HOST=127.0.0.1

# Database
DATABASE_PATH=./db/library.db
```

## API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Main Endpoints

- `POST /api/chat` - Send message to agent
- `GET /api/sessions` - List all sessions
- `POST /api/sessions/new` - Create new session
- `GET /api/sessions/{id}` - Get session with history
- `GET /health` - Health check

## Troubleshooting

### Backend won't start

**Error**: `Database not found`
- **Solution**: Run `python db/init_db.py`

**Error**: `OPENAI_API_KEY not found`
- **Solution**: Check your `.env` file has the correct API key

### Frontend shows "Backend not running"

- Make sure the backend server is running on port 8000
- Check terminal for backend errors
- Try accessing http://127.0.0.1:8000/health in browser

### Agent not responding

- Check your OpenAI API key is valid
- Check you have API credits
- Look at backend terminal for error messages

### Database errors

To reset the database:
```bash
python db/init_db.py
```

This will delete and recreate the database with fresh seed data.

## Development

### Adding New Tools

1. Add tool function in `server/agent/tools.py`
2. Decorate with `@tool`
3. Add to `ALL_TOOLS` list
4. Tool will automatically be available to the agent

Example:
```python
@tool
def my_new_tool(param: str) -> str:
    """Tool description for the LLM"""
    # Your logic here
    return json.dumps({"result": "success"})
```

### Customizing the System Prompt

Edit `prompts/system_prompt.txt` to change how the agent behaves.

## Tech Stack

- **Frontend**: Streamlit 1.28.0
- **Backend**: FastAPI 0.104.1
- **Agent**: LangChain 0.1.0
- **LLM**: OpenAI GPT-4o-mini
- **Database**: SQLite3
- **Python**: 3.9+

## License

This project is created for educational purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review backend terminal logs
3. Verify your OpenAI API key is valid

## Acknowledgments

Built for the MenaDevs GenAI Assessment using:
- LangChain for agent orchestration
- OpenAI for language models
- Streamlit for rapid UI development
- FastAPI for modern Python APIs

---

**Happy Library Management! 📚✨**

