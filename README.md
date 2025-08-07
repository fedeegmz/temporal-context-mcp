# Temporal Context MCP

A Model Context Protocol (MCP) server that provides intelligent temporal context, enabling AI agents to adapt their
responses based on the user's schedule and routines.

## How It Works

The system operates on a simple yet effective loop:

1. **Context Definition**: The user defines a set of `TemporalContext` objects in a `contexts.json` file. Each context
   represents a specific period or activity (e.g., work, study, exercise).
2. **Time Pattern Matching**: Each `TemporalContext` is associated with a `TimePattern`, which is a `cron` expression (
   e.g., `0 9 * * 1-5` for 9 AM on weekdays).
3. **Active Context Resolution**: The server continuously evaluates the current time against all defined time patterns.
   When a match is found, the corresponding `TemporalContext` becomes active. If multiple contexts match, a `priority`
   field is used to resolve conflicts.
4. **Recommendation Derivation**: The active context's `context_type` (e.g., `WORK`, `HOME`) is used to look up a
   corresponding `Recommendation` object. This mapping is managed internally by the `RecommendationRepository`.
5. **API Exposure**: The primary AI agent calls the `get_current_context()` endpoint, which returns the active
   `TemporalContext` along with its derived `Recommendation`.

Persistence is handled by a simple JSON file, making the system transparent and easy to configure.

## Key Components

### `TemporalContext`

This is the core domain model, representing a specific, user-defined block of time.

```python
class TemporalContext(BaseModel):
    id: str
    name: str
    context_type: ContextType  # Enum: WORK, HOME, STUDY, etc.
    time_pattern: TimePattern  # A cron expression
    active: bool = True
    priority: Priority = Priority.LOW  # Enum: LOW, MEDIUM, HIGH
```

### `Recommendation`

This object provides actionable guidance to the AI agent. It is not stored but is derived from the active
`TemporalContext`.

```python
class Recommendation(BaseModel):
    context_type: ContextType
    response_style: ResponseStyle  # e.g., NORMAL, CONCISE
    formality_level: FormalityLevel  # e.g., INFORMAL, FORMAL
    detail_level: DetailLevel  # e.g., LOW, MEDIUM, HIGH
    suggested_tools: list[str]  # Tools to prefer
    avoid_topics: list[str]  # Topics to avoid
```

## API

The server exposes its functionality via MCP tools.

### `get_current_context()`

Returns the currently active temporal context and the associated recommendation. This is the primary endpoint for AI
agents.

**Example Response:**

```json
{
  "temporal_context": {
    "id": "ctx_work_hours",
    "name": "Work Hours",
    "context_type": "WORK",
    "time_pattern": {
      "pattern": "0 9 * * 1-5"
    },
    "active": true,
    "created_at": "2023-10-27T09:00:00Z",
    "last_used": null,
    "priority": "MEDIUM"
  },
  "recommendation": {
    "context_type": "WORK",
    "response_style": "NORMAL",
    "formality_level": "FORMAL",
    "detail_level": "HIGH",
    "suggested_tools": [
      "calendar",
      "jira"
    ],
    "avoid_topics": [
      "personal_finance"
    ],
    "time_sensitive": true
  }
}
```

### `list_contexts()`

Lists all defined temporal contexts.

- `context_type` (str, optional): Filter by context type.
- `actives` (bool, optional): Filter by active/inactive status.

## Installation and Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/fedeegmz/temporal-context-mcp.git
   cd temporal-context-mcp
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure Contexts:**
   Create a `contexts.json` file in the `data` directory. This file should contain an array of `TemporalContext`objects.

   **Example `data/contexts.json`:**
   ```json
   [
     {
       "id": "ctx_work_hours_1",
       "name": "Work Hours",
       "context_type": "WORK",
       "time_pattern": {
         "pattern": "0 9 * * 1-5"
       },
       "priority": "MEDIUM"
     },
     {
       "id": "ctx_evening_leisure_1",
       "name": "Evening Leisure",
       "context_type": "LEISURE",
       "time_pattern": {
         "pattern": "0 19 * * *"
       },
       "priority": "LOW"
     }
   ]
   ```

4. **Run the server:**
   The project is packaged with a console script.
   ```bash
   uv run temporal-context-mcp
   ```
   The server will start and listen for requests on stdio.

## Development

To set up a development environment:

1. Install in editable mode with development dependencies:
   ```bash
   uv sync --group dev
   ```

2. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

3. Run tests:
   ```bash
   uv run pytest
   ```

4. Run web inspector:
   ```bash
   mcp-inspector uv run temporal-context-mcp
   ```
