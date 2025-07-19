# 🕒 Temporal Context MCP Server

An innovative MCP (Model Context Protocol) server that enables AI assistants to intelligently adapt based on the user's
temporal context.

## 🌟 Key Features

- **Intelligent temporal contexts**: Define specific behaviors for different times of day, days of the week, or custom
  patterns
- **Multiple context types**: Work schedules, mood patterns, response styles, availability, and focus time
- **Flexible patterns**: Support for fixed schedules, cron patterns, specific dates, and time ranges
- **Automatic recommendations**: The system automatically suggests appropriate response styles, tools, and
  configurations
- **Persistent storage**: Contexts are saved locally in JSON format

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- UV (recommended) or pip

## 🚀 Basic Usage

### 1. Get current context

```python
# Through MCP
await call_tool("get_current_context")
```

This will show you:

- Active contexts at this moment
- Response style recommendations
- Suggested tools
- Topics to avoid

### 2. Create a custom context

```python
await call_tool("add_temporal_context", {
    "id": "monday_meetings",
    "name": "Monday meetings",
    "context_type": "work_schedule",
    "time_pattern": {
        "days_of_week": [1],  # Monday only
        "hour_range": [14, 16]  # 2PM-4PM
    },
    "context_data": {
        "preferences": {
            "response_style": "professional",
            "formality_level": "high",
            "detail_level": "high"
        },
        "suggested_tools": ["calendar", "notes", "tasks"],
        "avoid_topics": ["personal", "entertainment"]
    },
    "priority": 1
})
```

### 3. List all contexts

```python
await call_tool("list_contexts")
```

### 4. Preview future contexts

```python
await call_tool("preview_context", {
    "datetime": "2024-12-25T09:00:00",
    "timezone": "local"
})
```

## 🔧 Context Types

### `work_schedule` - Work Schedule

- Activates professional mode during work hours
- Suggests productivity tools
- Avoids personal topics

### `focus_time` - Focus Time

- More concise responses
- Avoids interruptions
- Prioritizes efficiency

### `mood_pattern` - Mood Patterns

- Adapts tone based on your emotional state
- Suggests appropriate activities
- Customizes motivation level

### `response_style` - Response Style

- Defines formality and detail level
- Adapts vocabulary and structure
- Customizes based on situation

### `availability` - Availability

- Indicates when you're available/busy
- Adjusts response urgency
- Manages time expectations

## 📅 Time Patterns

### Days of the week

```
"days_of_week": [1, 2, 3, 4, 5]  # Mon-Fri (0=Sunday)
```

### Hour ranges

```
"hour_range": [9, 17]  # 9AM to 5PM
```

### Specific hours

```
"hours": [9, 13, 17]  # 9AM, 1PM, 5PM
```

### Cron patterns

```
"cron_pattern": "0 9 * * 1-5"  # 9AM, weekdays
```

### Specific dates

```
"specific_dates": ["2024-12-25", "2024-01-01"]  # Christmas and New Year
```

## 🔄 Useful Context Examples

### Strict work hours

```python
{
    "id": "strict_work",
    "name": "Office hours",
    "context_type": "work_schedule",
    "time_pattern": {
        "days_of_week": [1, 2, 3, 4, 5],
        "hour_range": [9, 18]
    },
    "context_data": {
        "preferences": {
            "response_style": "professional",
            "formality_level": "high",
            "detail_level": "high"
        },
        "time_sensitive": True
    }
}
```

### Creative night mode

```python
{
    "id": "creative_night",
    "name": "Night creative sessions",
    "context_type": "mood_pattern",
    "time_pattern": {
        "hour_range": [20, 23]
    },
    "context_data": {
        "mood": "creative",
        "preferences": {
            "response_style": "inspiring",
            "detail_level": "high"
        },
        "suggested_tools": ["brainstorm", "research", "writing"]
    }
}
```

### Relaxed weekend

```python
{
    "id": "weekend_chill",
    "name": "Weekend relaxation",
    "context_type": "response_style",
    "time_pattern": {
        "days_of_week": [0, 6]
    },
    "context_data": {
        "preferences": {
            "response_style": "casual",
            "formality_level": "low"
        },
        "encourage_fun": True
    }
}
```

## 🔧 Advanced Customization

### Priorities

Contexts have priorities (1=high, 3=low). When multiple contexts are active, higher priority ones take precedence.

### Custom context data

You can add any field to `context_data`:

```python
"context_data": {
    "preferences": {...},
    "custom_field": "custom value",
    "user_mood": "motivated",
    "project_context": "machine_learning"
}
```

### Dynamic updates

```python
await call_tool("update_context", {
    "context_id": "strict_work",
    "updates": {
        "active": False,
        "context_data": {"new_preference": "value"}
    }
})
```

## 🗂️ File Structure

```
temporal-context-mcp/
├── src/temporal_context_mcp/
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   ├── temporal_store.py  # Persistent storage
│   ├── time_utils.py      # Time utilities
│   └── models.py          # Pydantic data models
├── data/
│   └── temporal_contexts.json  # Local storage
├── pyproject.toml
└── README.md
```

## 🤝 MCP Client Integration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "temporal-context": {
      "command": "temporal-context-mcp"
    }
  }
}
```

### Other clients

The server implements the standard MCP protocol and is compatible with any MCP-supporting client.

## 📊 Use Cases

1. **Adaptive productivity**: Automatically switch between work and personal modes
2. **Energy management**: Gentler responses when you're tired
3. **Project context**: Different configurations for different types of work
4. **Daily routines**: Automate changes based on your personal routine
5. **Remote work**: Clearly separate work and personal time

## 🛠️ Development

### Run in development mode

```bash
uv run python -m temporal_context_mcp.server
```

### Tests (to be implemented)

```bash
uv run pytest
```

### Contributing

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

MIT License - see LICENSE file for details.

## 🎯 Roadmap

- [ ] Web interface for visual management
- [ ] External calendar synchronization
- [ ] Machine learning for context prediction
- [ ] Integration with productivity services
- [ ] Geographic contexts (location-based)
- [ ] Collaborative contexts (team work)

## 🚀 Available Tools

### `get_current_context`

Get the current temporal context and recommendations.

**Parameters:**

- `timezone` (optional): Timezone (default: "local")

### `add_temporal_context`

Add a new temporal context.

**Required parameters:**

- `id`: Unique context ID
- `name`: Descriptive name
- `context_type`: Type of context (work_schedule, mood_pattern, etc.)
- `time_pattern`: Time pattern definition
- `context_data`: Context data and preferences

**Optional parameters:**

- `priority`: Priority level (1-3, default: 1)

### `list_contexts`

List all temporal contexts.

**Parameters:**

- `context_type` (optional): Filter by context type
- `active_only` (optional): Show only currently active contexts

### `update_context`

Update an existing temporal context.

**Parameters:**

- `context_id`: ID of context to update
- `updates`: Fields to update

### `delete_context`

Delete a temporal context.

**Parameters:**

- `context_id`: ID of context to delete

### `preview_context`

Preview which contexts would be active at a specific time.

**Parameters:**

- `datetime` (optional): Target datetime in ISO format
- `timezone` (optional): Timezone (default: "local")

## 💡 Pro Tips

1. **Start simple**: Begin with basic work/personal contexts, then add complexity
2. **Use priorities**: Set important contexts (like focus time) to priority 1
3. **Test patterns**: Use `preview_context` to verify your time patterns work correctly
4. **Layer contexts**: Multiple contexts can be active simultaneously
5. **Monitor usage**: Check `last_used` timestamps to see which contexts are most valuable

## 🤖 Example Integration

Here's how the assistant might use this information:

```
User: "Help me write an email"

Context Active: 
- Work Schedule (Mon-Fri 9-5)
- Focus Time (9-11 AM)

AI Response: "I'll help you draft a professional email. Since you're in focus time, I'll keep this efficient and to the point. What's the purpose of this email?"
```

vs.

```
User: "Help me write an email"

Context Active:
- Weekend Casual
- Creative Mode

AI Response: "Sure! Let's craft something great. Is this a fun personal email or something more creative? I can help make it engaging and expressive."
```