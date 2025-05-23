# English Buddy MVP

**English Buddy** is an AI-powered English learning chatbot. This MVP focuses on a single-user, single-agent system for Telegram, built with LangGraph, LangChain, and PostgreSQL.

## Features (MVP)
- Telegram bot for English conversation and practice
- Grammar correction, vocabulary suggestions, and feedback
- Adaptive quizzes and progress tracking
- PostgreSQL with pgvector for embeddings and user data

## Tech Stack
- Python 3.10+
- LangChain, LangGraph
- PostgreSQL 14+ with pgvector
- python-telegram-bot
- SQLAlchemy, Pydantic

## Setup Instructions
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up PostgreSQL 14+ and enable the `pgvector` extension
4. Configure environment variables (see below)
5. Run the bot (implementation in progress)

## Environment Variables
- `TELEGRAM_BOT_TOKEN`: Telegram bot API token
- `OPENAI_API_KEY`: OpenAI API key (for LLM and embeddings)
- `DATABASE_URL`: PostgreSQL connection string

## Project Structure
- `src/` — Source code
- `tests/` — Tests
- `docs/` — Documentation

---

This MVP is for development and testing only. Production features and multi-agent support will be added in future phases. 