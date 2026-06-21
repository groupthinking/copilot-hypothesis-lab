#!/usr/bin/env ts-node
/**
 * append_lesson.ts
 *
 * Fetches PR metadata from the GitHub API and appends a LESSON: block
 * to h1-memory-flywheel/MEMORY.md.
 *
 * Usage:
 *   npx ts-node append_lesson.ts --pr <number> --repo <owner/repo> [--dry-run]
 *
 * Environment:
 *   GITHUB_TOKEN  — required unless --dry-run
 */

import * as fs from "fs";
import * as path from "path";
import * as https from "https";

interface ParsedArgs {
  pr: number;
  repo: string;
  title?: string;
  author?: string;
  dryRun: boolean;
}

interface Review {
  state: string;
  body: string;
  user: { login: string };
}

interface CheckRun {
  name: string;
  conclusion: string | null;
  started_at: string;
  completed_at: string | null;
}

interface PRData {
  number: number;
  title: string;
  body: string | null;
  merged_at: string | null;
  user: { login: string };
  head: { sha: string };
}

function parseArgs(argv: string[]): ParsedArgs {
  const args = argv.slice(2);
  const get = (flag: string): string | undefined => {
    const idx = args.indexOf(flag);
    return idx >= 0 ? args[idx + 1] : undefined;
  };
  const prStr = get("--pr");
  const repo = get("--repo");
  if (!prStr || !repo) {
    console.error("Usage: append_lesson.ts --pr <number> --repo <owner/repo> [--dry-run]");
    process.exit(1);
  }
  return {
    pr: parseInt(prStr, 10),
    repo,
    title: get("--title"),
    author: get("--author"),
    dryRun: args.includes("--dry-run"),
  };
}

function githubRequest<T>(path: string, token: string): Promise<T> {
  return new Promise((resolve, reject) => {
    const options: https.RequestOptions = {
      hostname: "api.github.com",
      path,
      method: "GET",
      headers: {
        "Accept": "application/vnd.github+json",
        "Authorization": `Bearer ${token}`,
        "User-Agent": "copilot-hypothesis-lab/memory-writer",
        "X-GitHub-Api-Version": "2022-11-28",
      },
    };
    const req = https.request(options, (res) => {
      const chunks: Buffer[] = [];
      res.on("data", (chunk: Buffer) => chunks.push(chunk));
      res.on("end", () => {
        try {
          resolve(JSON.parse(Buffer.concat(chunks).toString()));
        } catch (e) {
          reject(new Error(`Failed to parse GitHub API response: ${e}`));
        }
      });
    });
    req.on("error", reject);
    req.end();
  });
}

function formatDate(iso: string | null): string {
  if (!iso) return new Date().toISOString().slice(0, 10);
  return iso.slice(0, 10);
}

function buildLessonBlock(
  prNumber: number,
  date: string,
  outcome: string,
  whatFailed: string[],
  whatWorked: string[],
  convention: string
): string {
  const noFailures = whatFailed.length === 0 || whatFailed[0] === "";
  const failedSection = noFailures
    ? `WHAT_FAILED: none`
    : [`WHAT_FAILED: |`, ...whatFailed.map((l) => `  - ${l}`)].join("\n");

  const workedLines =
    whatWorked.length === 0
      ? "  - (no specific wins recorded)"
      : whatWorked.map((l) => `  - ${l}`).join("\n");

  return [
    `LESSON: Auto-recorded lesson from PR #${prNumber}`,
    `PR: #${prNumber}`,
    `DATE: ${date}`,
    `OUTCOME: ${outcome}`,
    failedSection,
    `WHAT_WORKED: |`,
    workedLines,
    `CONVENTION: |`,
    `  ${convention}`,
    "",
  ].join("\n");
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv);
  const token = process.env.GITHUB_TOKEN ?? "";

  if (!args.dryRun && !token) {
    console.error("GITHUB_TOKEN is required unless --dry-run is set.");
    process.exit(1);
  }

  const [owner, repoName] = args.repo.split("/");
  const prNumber = args.pr;

  let prData: PRData;
  let reviews: Review[] = [];
  let checkRuns: CheckRun[] = [];

  if (args.dryRun) {
    prData = {
      number: prNumber,
      title: args.title ?? `PR #${prNumber} (dry-run)`,
      body: null,
      merged_at: new Date().toISOString(),
      user: { login: args.author ?? "dry-run-user" },
      head: { sha: "0000000000000000000000000000000000000000" },
    };
    reviews = [];
    checkRuns = [];
  } else {
    console.log(`Fetching PR #${prNumber} from ${args.repo}...`);
    prData = await githubRequest<PRData>(
      `/repos/${owner}/${repoName}/pulls/${prNumber}`,
      token
    );
    reviews = await githubRequest<Review[]>(
      `/repos/${owner}/${repoName}/pulls/${prNumber}/reviews`,
      token
    );

    const checksResponse = await githubRequest<{ check_runs: CheckRun[] }>(
      `/repos/${owner}/${repoName}/commits/${prData.head.sha}/check-runs`,
      token
    );
    checkRuns = checksResponse.check_runs ?? [];
  }

  // Determine outcome
  const hasRevisions = reviews.some(
    (r) => r.state === "CHANGES_REQUESTED"
  );
  const outcome = hasRevisions ? "REVISED" : "APPROVED";

  // Collect what failed
  const whatFailed: string[] = reviews
    .filter((r) => r.state === "CHANGES_REQUESTED" && r.body)
    .slice(0, 3)
    .map((r) => r.body.split("\n")[0].slice(0, 120));

  const failedChecks = checkRuns
    .filter((c) => c.conclusion === "failure")
    .slice(0, 2)
    .map((c) => `CI check failed: ${c.name}`);

  const allFailed = [...whatFailed, ...failedChecks];

  // What worked
  const approved = reviews.filter((r) => r.state === "APPROVED");
  const whatWorked: string[] = approved.length > 0
    ? [`Approved by ${approved.map((r) => r.user.login).join(", ")} without changes`]
    : ["Implementation merged successfully"];

  // Convention — derive from title or use generic
  const titleLower = (prData.title ?? "").toLowerCase();
  let convention = "Review the LESSON blocks before starting similar tasks.";
  if (titleLower.includes("auth") || titleLower.includes("oauth")) {
    convention = "Auth PRs require integration tests covering token expiry and refresh flows.";
  } else if (titleLower.includes("test")) {
    convention = "Test PRs must not decrease coverage; use `--coverage` flag in CI.";
  } else if (titleLower.includes("ci") || titleLower.includes("workflow")) {
    convention = "Workflow changes must be validated with act or a manual dispatch before merging.";
  }

  const date = formatDate(prData.merged_at);
  const block = buildLessonBlock(prNumber, date, outcome, allFailed, whatWorked, convention);

  // Find MEMORY.md path relative to repo root
  const memoryPath = path.resolve(
    __dirname,
    "..",
    "MEMORY.md"
  );

  if (args.dryRun) {
    console.log("\n--- DRY RUN: Would append to MEMORY.md ---\n");
    console.log(block);
    console.log("---\n");
    return;
  }

  if (!fs.existsSync(memoryPath)) {
    console.error(`MEMORY.md not found at ${memoryPath}`);
    process.exit(1);
  }

  const existing = fs.readFileSync(memoryPath, "utf-8");
  const separator = existing.endsWith("\n---\n") ? "" : "\n---\n";
  fs.appendFileSync(memoryPath, `${separator}${block}---\n`);

  console.log(`✅ Appended LESSON block for PR #${prNumber} to ${memoryPath}`);
}

main().catch((err) => {
  console.error("Error:", err);
  process.exit(1);
});
