#!/usr/bin/env node
// apply-unified-patch.mjs — minimal, exact unified-diff applier (change c-182).
//
// Why this exists: the pinned base image n8nio/n8n:2.11.2 is an Alpine hardened
// image that ships NEITHER `patch` NOR `python3` (only `node` is guaranteed).
// This applier keeps the versioned `.patch` file as the single source of truth
// while patching the vendored package at image build time.
//
// It applies EXACTLY one removed line and one added line by full-line
// substitution (no fuzz). It exits non-zero if the target line is absent or
// ambiguous, so the derived image can never be built on top of a package layout
// or a signature that no longer matches.
//
// Usage:
//   node apply-unified-patch.mjs <target-file> <unified-diff-file>

import { readFileSync, writeFileSync } from "node:fs";

function fail(message) {
  process.stderr.write(`apply-unified-patch: ERROR: ${message}\n`);
  process.exit(1);
}

const [, , targetPath, patchPath] = process.argv;
if (!targetPath || !patchPath) {
  fail("usage: apply-unified-patch.mjs <target-file> <unified-diff-file>");
}

let removed = null;
let added = null;
let inHunk = false;

for (const line of readFileSync(patchPath, "utf8").split("\n")) {
  if (line.startsWith("@@")) {
    inHunk = true;
    continue;
  }
  if (!inHunk || line === "" || line.startsWith("\\")) {
    continue;
  }
  if (line.startsWith("-")) {
    if (removed !== null) fail("diff changes more than one removed line");
    removed = line.slice(1);
  } else if (line.startsWith("+")) {
    if (added !== null) fail("diff changes more than one added line");
    added = line.slice(1);
  }
}

if (removed === null || added === null) {
  fail("diff must contain exactly one removed line and one added line");
}

const sourceLines = readFileSync(targetPath, "utf8").split("\n");
const matches = sourceLines.reduce(
  (acc, line, index) => (line === removed ? [...acc, index] : acc),
  [],
);

if (matches.length !== 1) {
  fail(
    `target line not found exactly once (matches=${matches.length}) in ${targetPath}`,
  );
}

sourceLines[matches[0]] = added;
writeFileSync(targetPath, sourceLines.join("\n"));
process.stdout.write(
  `apply-unified-patch: applied 1 line at ${targetPath}:${matches[0] + 1}\n`,
);
