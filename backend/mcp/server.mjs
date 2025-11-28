import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { exec } from "node:child_process";
import { promisify } from "node:util";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const execAsync = promisify(exec);

const server = new McpServer(
  {
    name: "docker-error-mcp",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const PROJECT_ROOT = path.resolve(__dirname, "../..");
const MCP_TEMP_DIR = path.resolve(__dirname, "temp");

function sanitizeFileLocationId(fileLocationId) {
  return String(fileLocationId).replace(/[^a-zA-Z0-9_.-]/g, "_");
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function formEncode(body) {
  return Object.entries(body)
    .map(([key, value]) => {
      const safeValue =
        value === undefined || value === null ? "" : String(value);
      return `${encodeURIComponent(key)}=${encodeURIComponent(safeValue)}`;
    })
    .join("&");
}

function normalizeErrorMessage(message) {
  if (!message) return "";
  let normalized = String(message);
  normalized = normalized.replace(
    /\b[0-9a-fA-F]{8,}\b/g,
    "<HEX_OR_ID>"
  );
  normalized = normalized.replace(/\d+/g, "<NUM>");
  return normalized;
}

async function captureApiLogs() {
  ensureDir(MCP_TEMP_DIR);

  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  const logFilePath = path.join(
    MCP_TEMP_DIR,
    `api-logs-${timestamp}.log`
  );

  try {
    const { stdout } = await execAsync(`docker-compose logs --no-color api`, {
      cwd: PROJECT_ROOT,
      maxBuffer: 50 * 1024 * 1024,
    });
    fs.writeFileSync(logFilePath, stdout, "utf8");
    return { logFilePath };
  } catch (logErr) {
    const errorDetail =
      (logErr && (logErr.stderr || logErr.message)) || String(logErr);
    const fallbackMessage = [
      "Failed to capture docker logs for 'api' service.",
      `Error: ${errorDetail}`,
      logErr && logErr.stdout ? `Stdout:\n${logErr.stdout}` : "",
    ]
      .filter(Boolean)
      .join("\n\n");
    fs.writeFileSync(logFilePath, fallbackMessage, "utf8");
    return { logFilePath, logError: String(errorDetail) };
  }
}

async function buildToolResponse(payload) {
  try {
    const logResult = await captureApiLogs();
    if (logResult.logError) {
      console.warn("[test_endpoint] Log capture warning:", logResult.logError);
    }
  } catch (err) {
    console.error(
      "[test_endpoint] Failed to capture logs for api service:",
      err
    );
  }

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(payload, null, 2),
      },
    ],
    structuredContent: payload,
  };
}

// Tool 1: test_endpoint - Test an API endpoint with a payload using curl
server.registerTool(
  "test_endpoint",
  {
    description:
      "Test an API endpoint by sending a curl request with the provided payload. Assumes the server is already running.",
    inputSchema: z.object({
      endpoint: z
        .string()
        .describe(
          "The API endpoint URL to test, e.g., '/api/v1/trading/orders' or full URL 'http://localhost:8000/api/v1/trading/orders'"
        ),
      payload: z
        .object({})
        .passthrough()
        .optional()
        .describe("JSON payload to send in the request body"),
      method: z
        .enum(["GET", "POST", "PUT", "DELETE", "PATCH"])
        .optional()
        .default("POST")
        .describe("HTTP method to use"),
      host: z
        .string()
        .optional()
        .default("http://localhost:8000")
        .describe("Base URL of the API server"),
    }),
  },
  async (input) => {
    const endpoint = String(input.endpoint);
    const method = input.method || "POST";
    const host = input.host || "http://localhost:8000";
    const payload = input.payload || {};

    // First, authenticate and get token
    let accessToken = null;
    try {
      const loginUrl = `${host}/api/v1/auth/login`;
      const loginBody = formEncode({
        grant_type: "password",
        username: process.env.MCP_USERNAME || "admin",
        password: process.env.MCP_PASSWORD || "pass",
      });
      const escapedLoginBody = loginBody.replace(/"/g, '\\"');
      const loginCommand = `curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "${escapedLoginBody}" "${loginUrl}"`;

      const { stdout: loginStdout } = await execAsync(loginCommand, {
        maxBuffer: 10 * 1024 * 1024,
      });

      let loginResponse;
      try {
        loginResponse = JSON.parse(loginStdout);
        accessToken = loginResponse.access_token;
      } catch {
        // If parsing fails, try to extract token from raw output
        const tokenMatch = loginStdout.match(/"access_token"\s*:\s*"([^"]+)"/);
        if (tokenMatch) {
          accessToken = tokenMatch[1];
        }
      }
    } catch (loginErr) {
      return buildToolResponse({
        success: false,
        error: "Failed to authenticate",
        login_error: String(loginErr),
      });
    }

    if (!accessToken) {
      return buildToolResponse({
        success: false,
        error: "Failed to extract access token from login response",
      });
    }

    // Construct full URL
    const fullUrl = endpoint.startsWith("http")
      ? endpoint
      : `${host}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;

    // Build curl command with authentication
    let curlCommand = `curl -X ${method} -H "Content-Type: application/json" -H "Authorization: Bearer ${accessToken}"`;

    if (payload && Object.keys(payload).length > 0) {
      const payloadJson = JSON.stringify(payload);
      // Escape the JSON for shell
      const escapedPayload = payloadJson.replace(/"/g, '\\"');
      curlCommand += ` -d "${escapedPayload}"`;
    }

    curlCommand += ` "${fullUrl}"`;

    try {
      const { stdout, stderr } = await execAsync(curlCommand, {
        maxBuffer: 10 * 1024 * 1024,
      });

      let responseBody;
      try {
        responseBody = JSON.parse(stdout);
      } catch {
        responseBody = stdout;
      }

      return buildToolResponse({
        success: true,
        method,
        endpoint: fullUrl,
        payload,
        response: responseBody,
        stderr: stderr || null,
      });
    } catch (err) {
      const stdout = err.stdout ?? "";
      const stderr = err.stderr ?? String(err);

      let responseBody;
      try {
        responseBody = JSON.parse(stdout);
      } catch {
        responseBody = stdout;
      }

      return buildToolResponse({
        success: false,
        method,
        endpoint: fullUrl,
        payload,
        error: String(err),
        response: responseBody,
        stderr: stderr || null,
      });
    }
  }
);

// Tool 2: start_docker - Force restart the FastAPI pod/container
server.registerTool(
  "start_docker",
  {
    description:
      "Delete the FastAPI pod (docker container) and start it again via docker-compose.",
    inputSchema: z.object({}),
  },
  async () => {
    const FASTAPI_POD_NAME = "fastapi";
    const FASTAPI_COMPOSE_SERVICE = "api";
    const projectRoot = path.resolve(__dirname, "../..");

    const commandOutputs = [];

    const recordResult = (command, stdout, stderr, failed = false) => {
      commandOutputs.push({
        command,
        stdout: stdout || "",
        stderr: stderr || "",
        failed,
      });
    };

    const runCommand = async (command, { ignoreError = false } = {}) => {
      try {
        const result = await execAsync(command, {
          maxBuffer: 10 * 1024 * 1024,
          cwd: projectRoot,
        });
        recordResult(command, result.stdout, result.stderr, false);
        return result;
      } catch (err) {
        const stdout = err.stdout ?? "";
        const stderr = err.stderr ?? String(err);
        recordResult(command, stdout, stderr, true);
        if (!ignoreError) {
          throw err;
        }
        return { stdout, stderr };
      }
    };

    const formatCombinedOutput = (key) =>
      commandOutputs
        .map(({ command, [key]: value }) =>
          value ? `$ ${command}\n${value}`.trim() : ""
        )
        .filter(Boolean)
        .join("\n\n") || null;

    const deleteCommand = `docker-compose rm -sf ${FASTAPI_COMPOSE_SERVICE}`;
    const startCommand = `docker-compose up -d ${FASTAPI_COMPOSE_SERVICE}`;

    try {
      // Always delete the FastAPI pod/container before starting it again
      await runCommand(deleteCommand, { ignoreError: true });
      await runCommand(startCommand);

      // Check if service is running
      const { stdout: psOutput } = await execAsync(
        `docker-compose ps ${FASTAPI_COMPOSE_SERVICE}`,
        { cwd: projectRoot }
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                success: true,
                pod: FASTAPI_POD_NAME,
                service: FASTAPI_COMPOSE_SERVICE,
                stdout: formatCombinedOutput("stdout"),
                stderr: formatCombinedOutput("stderr"),
                commands: commandOutputs,
                status: psOutput,
              },
              null,
              2
            ),
          },
        ],
        structuredContent: {
          success: true,
          pod: FASTAPI_POD_NAME,
          service: FASTAPI_COMPOSE_SERVICE,
          stdout: formatCombinedOutput("stdout"),
          stderr: formatCombinedOutput("stderr"),
          commands: commandOutputs,
          status: psOutput,
        },
      };
    } catch (err) {
      const stdout = err.stdout ?? "";
      const stderr = err.stderr ?? String(err);
      const combinedStdout = formatCombinedOutput("stdout") || stdout || null;
      const combinedStderr = formatCombinedOutput("stderr") || stderr || null;

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                success: false,
                pod: FASTAPI_POD_NAME,
                service: FASTAPI_COMPOSE_SERVICE,
                error: String(err),
                stdout: combinedStdout,
                stderr: combinedStderr,
                commands: commandOutputs,
              },
              null,
              2
            ),
          },
        ],
        structuredContent: {
          success: false,
          pod: FASTAPI_POD_NAME,
          service: FASTAPI_COMPOSE_SERVICE,
          error: String(err),
          stdout: combinedStdout,
          stderr: combinedStderr,
          commands: commandOutputs,
        },
      };
    }
  }
);
// Tool 3: compare_error_logs - Compare two log files from temp directory
server.registerTool(
  "compare_error_logs",
  {
    description:
      "Compare two log files from the temp folder and return the differences. If there are more than 2 files, picks the 2 most recent ones.",
    inputSchema: z.object({
      file_location_id: z
        .string()
        .optional()
        .describe(
          "Optional: Stable identifier for the error context (kept for backward compatibility, but not used)."
        ),
    }),
  },
  async (input) => {
    const tempDir = MCP_TEMP_DIR;
    
    if (!fs.existsSync(tempDir)) {
      throw new Error(`Temp directory not found at ${tempDir}`);
    }

    // Get all log files in temp directory
    const files = fs.readdirSync(tempDir)
      .filter(file => file.endsWith('.log'))
      .map(file => ({
        name: file,
        path: path.join(tempDir, file),
        mtime: fs.statSync(path.join(tempDir, file)).mtime.getTime()
      }))
      .sort((a, b) => b.mtime - a.mtime); // Sort by modification time, most recent first

    if (files.length === 0) {
      throw new Error(`No log files found in ${tempDir}`);
    }

    if (files.length === 1) {
      throw new Error(`Only one log file found in ${tempDir}. Need at least 2 files to compare.`);
    }

    // Pick the 2 most recent files
    const file1 = files[0];
    const file2 = files[1];

    // Read both files
    const content1 = fs.readFileSync(file1.path, "utf8");
    const content2 = fs.readFileSync(file2.path, "utf8");

    // Split into lines
    const lines1 = content1.split(/\r?\n/);
    const lines2 = content2.split(/\r?\n/);

    // Perform line-by-line diff
    const diff = [];
    const maxLines = Math.max(lines1.length, lines2.length);

    for (let i = 0; i < maxLines; i++) {
      const line1 = i < lines1.length ? lines1[i] : null;
      const line2 = i < lines2.length ? lines2[i] : null;

      if (line1 === line2) {
        // Lines are the same
        continue;
      } else if (line1 === null) {
        // Line added in file2
        diff.push({
          type: "added",
          line: i + 1,
          content: line2
        });
      } else if (line2 === null) {
        // Line removed from file1
        diff.push({
          type: "removed",
          line: i + 1,
          content: line1
        });
      } else {
        // Line changed
        diff.push({
          type: "changed",
          line: i + 1,
          old_content: line1,
          new_content: line2
        });
      }
    }

    const result = {
      file1: {
        name: file1.name,
        path: file1.path,
        line_count: lines1.length,
        modified: new Date(file1.mtime).toISOString()
      },
      file2: {
        name: file2.name,
        path: file2.path,
        line_count: lines2.length,
        modified: new Date(file2.mtime).toISOString()
      },
      diff: diff,
      diff_count: diff.length,
      total_lines_file1: lines1.length,
      total_lines_file2: lines2.length
    };

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
      structuredContent: result,
    };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("docker-error-mcp server failed to start:", err);
  process.exit(1);
});
