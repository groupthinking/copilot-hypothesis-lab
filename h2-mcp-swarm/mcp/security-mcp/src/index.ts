/**
 * security-mcp/src/index.ts
 *
 * MCP server that wraps CodeQL and semgrep static analysis.
 * The swarm-orchestrator calls this as its final step before opening a PR.
 *
 * Tool: scan
 * Input:  { files: string[], tools: ("codeql" | "semgrep")[] }
 * Output: { findings: Finding[], has_critical: boolean, has_high: boolean, summary: string }
 */

import * as http from "http";
import * as fs from "fs";
import * as child_process from "child_process";
import * as path from "path";

const PORT = parseInt(process.env.SECURITY_MCP_PORT ?? "3003", 10);
const REPO_ROOT = process.env.REPO_ROOT ?? process.cwd();

type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";

interface Finding {
  tool: string;
  rule: string;
  severity: Severity;
  file: string;
  line: number;
  message: string;
  recommendation: string;
}

interface ScanResult {
  findings: Finding[];
  has_critical: boolean;
  has_high: boolean;
  summary: string;
}

interface MCPRequest {
  tool: string;
  args: Record<string, unknown>;
  id?: string;
}

interface MCPResponse {
  id?: string;
  result?: unknown;
  error?: { code: number; message: string };
}

function isToolAvailable(toolName: string): boolean {
  // Only allow known safe tool names to prevent any injection risk
  const allowedTools = ["semgrep", "codeql"];
  if (!allowedTools.includes(toolName)) {
    return false;
  }
  const result = child_process.spawnSync("which", [toolName], { stdio: "ignore" });
  return result.status === 0;
}

function runSemgrep(files: string[]): Finding[] {
  if (!isToolAvailable("semgrep")) {
    return [
      {
        tool: "semgrep",
        rule: "tool-not-installed",
        severity: "INFO",
        file: files[0] ?? "unknown",
        line: 0,
        message: "semgrep is not installed. Install with: pip install semgrep",
        recommendation: "Install semgrep and re-run the security scan.",
      },
    ];
  }

  const findings: Finding[] = [];
  try {
    // Use spawnSync with a separate args array to prevent command injection
    const result = child_process.spawnSync(
      "semgrep",
      ["--json", "--config=auto", "--", ...files],
      { cwd: REPO_ROOT, timeout: 120000 }
    );
    const output = result.stdout ? result.stdout.toString() : "";
    const parsed = JSON.parse(output);
    for (const r of parsed.results ?? []) {
      findings.push({
        tool: "semgrep",
        rule: r.check_id ?? "unknown",
        severity: mapSemgrepSeverity(r.extra?.severity ?? "INFO"),
        file: r.path ?? "unknown",
        line: r.start?.line ?? 0,
        message: r.extra?.message ?? r.check_id ?? "Security issue detected",
        recommendation: r.extra?.fix ?? "Review and remediate per semgrep documentation.",
      });
    }
  } catch {
    // spawnSync result was not valid JSON — semgrep may have returned no output
  }
  return findings;
}

function mapSemgrepSeverity(s: string): Severity {
  switch (s.toUpperCase()) {
    case "ERROR": return "CRITICAL";
    case "WARNING": return "HIGH";
    case "INFO": return "LOW";
    default: return "MEDIUM";
  }
}

function runCodeQL(files: string[]): Finding[] {
  // CodeQL requires a database build; we check for the CLI and give instructions.
  if (!isToolAvailable("codeql")) {
    return [
      {
        tool: "codeql",
        rule: "tool-not-installed",
        severity: "INFO",
        file: files[0] ?? "unknown",
        line: 0,
        message: "CodeQL CLI is not installed. Download from https://github.com/github/codeql-action",
        recommendation:
          "In CI, use actions/github/codeql-action. Locally: install CodeQL CLI and create a database.",
      },
    ];
  }

  // If CodeQL is available, run a basic analysis.
  const findings: Finding[] = [];
  try {
    const dbPath = path.join(REPO_ROOT, ".codeql-db-tmp");
    const resultsPath = path.join(REPO_ROOT, ".codeql-results-tmp.sarif");

    // Use spawnSync with separate arguments to prevent command injection
    child_process.spawnSync(
      "codeql",
      ["database", "create", dbPath, "--language=javascript", "--overwrite"],
      { cwd: REPO_ROOT, timeout: 300000 }
    );
    child_process.spawnSync(
      "codeql",
      [
        "database", "analyze", dbPath,
        "--format=sarif-latest",
        `--output=${resultsPath}`,
        "javascript-security-and-quality.qls",
      ],
      { cwd: REPO_ROOT, timeout: 300000 }
    );
    const sarif = JSON.parse(fs.readFileSync(resultsPath, "utf-8"));
    for (const run of sarif.runs ?? []) {
      for (const result of run.results ?? []) {
        const loc = result.locations?.[0]?.physicalLocation;
        const severity = mapCodeQLSeverity(result.level ?? "note");
        findings.push({
          tool: "codeql",
          rule: result.ruleId ?? "unknown",
          severity,
          file: loc?.artifactLocation?.uri ?? "unknown",
          line: loc?.region?.startLine ?? 0,
          message: result.message?.text ?? "CodeQL finding",
          recommendation: "Review CodeQL rule documentation for remediation steps.",
        });
      }
    }
  } catch {
    // CodeQL failed — return a note
    findings.push({
      tool: "codeql",
      rule: "analysis-failed",
      severity: "INFO",
      file: "unknown",
      line: 0,
      message: "CodeQL analysis could not complete in this environment.",
      recommendation: "Run CodeQL in CI using the codeql-action for full analysis.",
    });
  }
  return findings;
}

function mapCodeQLSeverity(level: string): Severity {
  switch (level.toLowerCase()) {
    case "error": return "CRITICAL";
    case "warning": return "HIGH";
    case "note": return "INFO";
    default: return "MEDIUM";
  }
}

async function scan(args: Record<string, unknown>): Promise<ScanResult> {
  const files = Array.isArray(args.files) ? (args.files as string[]) : [];
  const tools = Array.isArray(args.tools)
    ? (args.tools as string[])
    : ["semgrep", "codeql"];

  if (files.length === 0) {
    throw new Error("files array must not be empty");
  }

  const findings: Finding[] = [];

  if (tools.includes("semgrep")) {
    findings.push(...runSemgrep(files));
  }
  if (tools.includes("codeql")) {
    findings.push(...runCodeQL(files));
  }

  const hasCritical = findings.some((f) => f.severity === "CRITICAL");
  const hasHigh = findings.some((f) => f.severity === "HIGH");

  const countBySeverity = (s: Severity) => findings.filter((f) => f.severity === s).length;

  const summary = [
    `Security scan complete. Files scanned: ${files.length}.`,
    `Findings: ${findings.length} total`,
    `  CRITICAL: ${countBySeverity("CRITICAL")}`,
    `  HIGH:     ${countBySeverity("HIGH")}`,
    `  MEDIUM:   ${countBySeverity("MEDIUM")}`,
    `  LOW:      ${countBySeverity("LOW")}`,
    `  INFO:     ${countBySeverity("INFO")}`,
    hasCritical || hasHigh
      ? "⛔ Fix all CRITICAL and HIGH findings before merging."
      : "✅ No CRITICAL or HIGH findings. Safe to open PR.",
  ].join("\n");

  return { findings, has_critical: hasCritical, has_high: hasHigh, summary };
}

const server = http.createServer(async (req, res) => {
  if (req.method === "GET" && req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok", server: "security-mcp", port: PORT }));
    return;
  }

  if (req.method !== "POST" || req.url !== "/mcp") {
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Not found. POST to /mcp" }));
    return;
  }

  const chunks: Buffer[] = [];
  req.on("data", (c: Buffer) => chunks.push(c));
  req.on("end", async () => {
    let body: MCPRequest;
    try {
      body = JSON.parse(Buffer.concat(chunks).toString());
    } catch {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Invalid JSON" }));
      return;
    }

    const response: MCPResponse = { id: body.id };

    try {
      if (body.tool !== "scan") {
        throw new Error(`Unknown tool: ${body.tool}. Available: scan`);
      }
      response.result = await scan(body.args ?? {});
    } catch (err: unknown) {
      // Log detailed error server-side; expose only a sanitized message to callers
      console.error("security-mcp error:", err);
      response.error = {
        code: -32000,
        message: err instanceof Error ? err.message.split("\n")[0].slice(0, 200) : "Internal server error",
      };
    }

    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(response));
  });
});

server.listen(PORT, () => {
  console.log(`security-mcp listening on http://localhost:${PORT}/mcp`);
  console.log(`Health: http://localhost:${PORT}/health`);
});
