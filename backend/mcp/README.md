## Docker Error MCP for Cursor

This MCP server lets Cursor (and the model) validate error fixes by:

- **Running your app/tests in Docker and capturing error logs as JSON**
- **Storing logs as `/temp/<file_location-id>-before` and `-after`**
- **Diffing JSON logs to see if the original error disappeared and whether any new ones were introduced**

Cursor and the model handle code edits; this MCP handles **runtime execution + log capture + diffing**.

---

### 0. Preconditions / assumptions

- **Docker**: Docker Desktop (or equivalent) is running on your machine.
- **Dockerfile**: There is a `Dockerfile` at the repo root that:
  - **Installs dependencies**
  - **Can run your test/app command**, e.g. `pytest -q`, `npm test`, `python main.py`
- **Run command**: A canonical command that reproduces the error, e.g.:
  - `RUN_COMMAND="pytest -q"`
  - `RUN_COMMAND="python -m my_service"`
- **Temp directory**: This server writes logs under `./temp` inside the repo.

You can set a default run command via environment:

```bash
export RUN_COMMAND="pytest -q"
```

If a `run_command` is passed in tool input, it wins over `RUN_COMMAND`. If neither is provided, the server defaults to `pytest -q`.

---

### 1. Installing dependencies

From the repo root (`/Users/akyukii/validation` in this setup):

```bash
cd /Users/akyukii/validation
npm install
```

This installs `@modelcontextprotocol/sdk`, which the MCP server uses.

---

### 2. MCP tools exposed

The server (in `server.mjs`) exposes three tools:

- **`store_before_error_logs`**
- **`run_docker_and_capture_logs`**
- **`compare_error_logs`**

#### Tool: `store_before_error_logs`

**Purpose**:

- Ingest the **“before”** error state from:
  - a user-pasted traceback, or
  - (later) a Grafana API call keyed by `trace_id`
- Parse it into structured JSON
- Save to: `temp/<file_location_id>-before/errors.json`

**Input schema (conceptual)**:

```json
{
  "file_location_id": "string",
  "raw_trace": "string",
  "trace_id": "string (optional)",
  "source": "\"manual\" | \"grafana\" (optional)"
}
```

**Behavior**:

- Ensures `temp/` and `temp/<sanitized_file_location_id>-before/` exist
- Parses `raw_trace` using the same heuristics as Docker logs
- Writes:

```json
{
  "meta": {
    "file_location_id": "src/foo.py:42",
    "phase": "before",
    "timestamp": "2025-11-27T11:05:00Z",
    "source": "manual",
    "trace_id": "abc123"
  },
  "errors": [ /* parsed error objects */ ],
  "raw": "original raw_trace text"
}
```

The model can call this tool immediately after you paste an error, **without running Docker at all**.

#### Tool: `run_docker_and_capture_logs`

**Purpose**:

- Build the Docker image
- Run your test/app command inside the container
- Capture `stdout`/`stderr`
- Parse logs into structured JSON
- Save to: `temp/<file_location_id>-<phase>/errors.json`
- Return a lightweight summary (error counts, phase, etc.)

**Input schema (conceptual)**:

```json
{
  "file_location_id": "string",
  "phase": "before | after",
  "run_command": "string (optional)"
}
```

**Behavior**:

- Ensures `temp/` and `temp/<file_location_id>-<phase>/` exist
- Sanitizes `file_location_id` to be filesystem-safe
- Runs:
  - `docker build -t docker-error-mcp-image .`
  - `docker run --rm docker-error-mcp-image sh -c "<run_command>"`
- Captures combined `stdout + stderr`
- Parses logs into an array of error objects, e.g.:

```json
{
  "meta": {
    "file_location_id": "src/foo.py:42",
    "phase": "before",
    "run_command": "pytest -q",
    "timestamp": "2025-11-27T11:05:00Z",
    "docker_step": "run",
    "docker_ok": false,
    "exit_code": 1
  },
  "errors": [
    {
      "timestamp": null,
      "level": "ERROR",
      "type": "KeyError",
      "file": "src/foo.py",
      "line": 42,
      "message": "KeyError: 'user_id'",
      "raw": "Traceback (most recent call last): ..."
    }
  ],
  "raw": "full stdout/stderr text"
}
```

> Note: The parser starts simple (Traceback/Error/Exception heuristics + Python `File "..."` lines) and can be refined later.

It writes this JSON to:

- `temp/<sanitized_file_location_id>-before/errors.json` or
- `temp/<sanitized_file_location_id>-after/errors.json`

and returns a small summary for the model.

#### Tool: `compare_error_logs`

**Purpose**:

- Load `before` and `after` JSON logs for a given `file_location_id`
- Compare errors and compute:
  - **fixed errors**
  - **new errors**
  - **persistent errors**
  - Boolean flags:
    - `is_error_gone`
    - `has_new_errors`

**Input schema (conceptual)**:

```json
{
  "file_location_id": "string"
}
```

**Behavior**:

- Loads:
  - `temp/<file_location_id>-before/errors.json`
  - `temp/<file_location_id>-after/errors.json`
- Defines an error “key”:

  \[
  \text{key} = (\text{file} : \text{line} : \text{type} : \text{normalized\_message})
  \]

  where `normalized_message` strips dynamic parts like IDs and numbers.

- Converts `before.errors` and `after.errors` into sets/maps by this key
- Computes:
  - `fixed_errors = before_set - after_set`
  - `new_errors = after_set - before_set`
  - `persistent_errors = before_set ∩ after_set`
- Returns:

```json
{
  "file_location_id": "src/foo.py:42",
  "fixed_errors": [/* array of error objects */],
  "new_errors": [/* array of error objects */],
  "persistent_errors": [/* array of error objects */],
  "is_error_gone": true,
  "has_new_errors": false,
  "before_error_count": 3,
  "after_error_count": 0
}
```

`is_error_gone` is `true` when there were errors before and none of them persist after. `has_new_errors` is `true` if any new error keys appear in the `after` logs.

---

### 3. Wiring this MCP into Cursor

In your Cursor MCP config (for example `cursor.mcp.json` or equivalent), register this server. A minimal example:

```json
{
  "mcpServers": {
    "docker-error-mcp": {
      "command": "node",
      "args": [
        "/Users/akyukii/validation/server.mjs"
      ]
    }
  }
}
```

Adjust the absolute path to `server.mjs` as needed.

Once registered, Cursor will expose the tools:

- `run_docker_and_capture_logs`
- `compare_error_logs`

to the model when the MCP is available.

---

### 4. Intended end-to-end UX in Cursor

#### Step 1: User pastes an error into chat

- User: “Here’s a traceback I’m seeing in `src/foo.py` line 42: …”
- The model:
  - Extracts a `file_location_id`, e.g. `src/foo.py:42`
  - Optionally records the target error message (`KeyError: 'user_id'`) in its own context

#### Step 2: Capture **before** logs in Docker

The model calls:

```json
{
  "tool": "run_docker_and_capture_logs",
  "arguments": {
    "file_location_id": "src/foo.py:42",
    "phase": "before",
    "run_command": "pytest -q"
  }
}
```

The MCP:

- Builds and runs Docker
- Captures error logs
- Writes `/temp/src_foo_py_42-before/errors.json`
- Returns an error summary

The model confirms that the original error is present in the `before` logs.

#### Step 3: Model/Cursor applies code fixes

- The MCP is idle here.
- Cursor + the LLM edit the code in the repo to attempt to fix the error.

#### Step 4: Capture **after** logs in Docker

The model calls:

```json
{
  "tool": "run_docker_and_capture_logs",
  "arguments": {
    "file_location_id": "src/foo.py:42",
    "phase": "after",
    "run_command": "pytest -q"
  }
}
```

The MCP:

- Rebuilds and reruns Docker with the updated workspace
- Writes `/temp/src_foo_py_42-after/errors.json`
- Returns a summary

#### Step 5: Compare JSON error traces

The model calls:

```json
{
  "tool": "compare_error_logs",
  "arguments": {
    "file_location_id": "src/foo.py:42"
  }
}
```

The MCP:

- Loads the `before` and `after` error JSON
- Computes `fixed_errors`, `new_errors`, `persistent_errors`
- Returns the structured diff with `is_error_gone` and `has_new_errors`

#### Step 6: Model reports back to the user

Using the diff, the model can say things like:

- **If clean**:
  - “The original `KeyError('user_id')` in `src/foo.py:42` is gone.”
  - “No new errors were introduced by the change.”
- **If not clean**:
  - “The original error is fixed, but a new `TypeError` appeared in `src/bar.py:17`.”

and then optionally iterate with more code changes + another `before/after` cycle.

---

### 5. Minimal v1 behavior

This implementation already:

- Stores full raw logs and a parsed error list in JSON
- Normalizes error messages when diffing to ignore obvious dynamic parts (IDs, numbers)
- Uses a simple parser tuned for:
  - Python tracebacks (`Traceback (most recent call last):`, `File "..." line N`)
  - Generic `Error`/`Exception` lines
