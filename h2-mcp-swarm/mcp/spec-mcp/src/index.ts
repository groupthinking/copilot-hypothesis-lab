/**
 * spec-mcp/src/index.ts
 *
 * MCP server that returns a structured PRD slice for a GitHub Issue.
 * The swarm-orchestrator calls this as its first step before implementing.
 *
 * Tool: get_prd_slice
 * Input:  { issue_number: number, repo?: string }
 * Output: { title, acceptance_criteria, api_contract, data_model, notes }
 */

import * as http from "http";
import * as https from "https";

const PORT = parseInt(process.env.SPEC_MCP_PORT ?? "3001", 10);
const GITHUB_TOKEN = process.env.GITHUB_TOKEN ?? "";
const DEFAULT_REPO = process.env.REPO ?? "";

interface PrdSlice {
  issue_number: number;
  title: string;
  acceptance_criteria: string[];
  api_contract: Record<string, unknown>;
  data_model: Record<string, unknown>;
  notes: string;
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

async function fetchIssue(
  repo: string,
  issueNumber: number
): Promise<{ title: string; body: string | null }> {
  return new Promise((resolve, reject) => {
    const [owner, repoName] = repo.split("/");
    const options: https.RequestOptions = {
      hostname: "api.github.com",
      path: `/repos/${owner}/${repoName}/issues/${issueNumber}`,
      method: "GET",
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${GITHUB_TOKEN}`,
        "User-Agent": "copilot-hypothesis-lab/spec-mcp",
        "X-GitHub-Api-Version": "2022-11-28",
      },
    };
    const req = https.request(options, (res) => {
      const chunks: Buffer[] = [];
      res.on("data", (c: Buffer) => chunks.push(c));
      res.on("end", () => {
        const parsed = JSON.parse(Buffer.concat(chunks).toString());
        resolve({ title: parsed.title ?? "", body: parsed.body ?? null });
      });
    });
    req.on("error", reject);
    req.end();
  });
}

function parseAcceptanceCriteria(body: string | null): string[] {
  if (!body) return ["(No acceptance criteria found in issue body)"];
  const lines = body.split("\n");
  const criteria: string[] = [];
  let inAcSection = false;
  for (const line of lines) {
    const lower = line.toLowerCase();
    if (lower.includes("acceptance criteria") || lower.includes("ac:")) {
      inAcSection = true;
      continue;
    }
    if (inAcSection) {
      const trimmed = line.trim();
      if (trimmed.startsWith("-") || trimmed.startsWith("*") || /^\d+\./.test(trimmed)) {
        criteria.push(trimmed.replace(/^[-*\d.]\s*/, ""));
      } else if (trimmed === "" && criteria.length > 0) {
        break;
      }
    }
  }
  return criteria.length > 0
    ? criteria
    : ["Implement the feature as described in the issue title and body."];
}

async function getPrdSlice(args: Record<string, unknown>): Promise<PrdSlice> {
  const issueNumber = Number(args.issue_number);
  const repo = String(args.repo ?? DEFAULT_REPO);

  if (!issueNumber || isNaN(issueNumber)) {
    throw new Error("issue_number must be a positive integer");
  }
  if (!repo || !repo.includes("/")) {
    throw new Error("repo must be in owner/repo format");
  }

  const issue = await fetchIssue(repo, issueNumber);
  const criteria = parseAcceptanceCriteria(issue.body);

  return {
    issue_number: issueNumber,
    title: issue.title,
    acceptance_criteria: criteria,
    api_contract: {
      note: "Derive API contract from the issue body and acceptance criteria above.",
      endpoints: [],
    },
    data_model: {
      note: "Derive data model from acceptance criteria and existing codebase conventions.",
      entities: [],
    },
    notes: issue.body ?? "(empty issue body)",
  };
}

const server = http.createServer(async (req, res) => {
  if (req.method === "GET" && req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok", server: "spec-mcp", port: PORT }));
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
      if (body.tool !== "get_prd_slice") {
        throw new Error(`Unknown tool: ${body.tool}. Available: get_prd_slice`);
      }
      response.result = await getPrdSlice(body.args ?? {});
    } catch (err: unknown) {
      // Log detailed error server-side; expose only a sanitized message to callers
      console.error("spec-mcp error:", err);
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
  console.log(`spec-mcp listening on http://localhost:${PORT}/mcp`);
  console.log(`Health: http://localhost:${PORT}/health`);
});
