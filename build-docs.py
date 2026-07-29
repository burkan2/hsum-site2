#!/usr/bin/env python3
"""Build the hSUM documentation pages from a single shell + per-page bodies.

Every command, flag, and JSON payload in these pages was captured from the real
0.1.0-alpha.4 binary. Re-verify with scripts/release-smoke.sh before a release.
"""
import shutil
from pathlib import Path

VERSION = "0.1.0-alpha.4"
ERROR_SOURCE_VERSION = "0.1.0-alpha.2"
BASE = f"/docs/{VERSION}"
ROOT = Path(__file__).parent / "docs" / VERSION

NAV = [
    ("Getting started", [
        ("", "Overview"),
        ("quickstart/", "Quickstart"),
    ]),
    ("Guides", [
        ("concepts/", "Concepts"),
        ("agents/", "Connect an agent"),
        ("mcp/", "MCP reference"),
    ]),
    ("Reference", [
        ("cli/", "CLI reference"),
        ("errors/", "Error codes"),
        ("troubleshooting/", "Troubleshooting"),
    ]),
]


def sidebar(active: str) -> str:
    active = "errors/" if active.startswith("errors/") else active
    out = []
    for heading, links in NAV:
        out.append(f"<h4>{heading}</h4><ul>")
        for href, label in links:
            cur = ' aria-current="page"' if href == active else ""
            out.append(f'<li><a href="{BASE}/{href}"{cur}>{label}</a></li>')
        out.append("</ul>")
    return "\n".join(out)


def page(slug: str, title: str, desc: str, body: str, crumb: str) -> str:
    canonical = f"https://hsum.burkankale.com{BASE}/{slug}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — hSUM {VERSION}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="/docs/assets/docs.css">
</head>
<body>
<header class="site">
  <div class="bar">
    <a class="brand" href="/">h<span>SUM</span></a>
    <span class="ver">{VERSION}</span>
    <nav>
      <a href="{BASE}/">Docs</a>
      <a href="{BASE}/cli/">CLI</a>
      <a href="{BASE}/mcp/">MCP</a>
      <a href="{BASE}/errors/">Errors</a>
      <a href="https://github.com/burkan2/hSUM">GitHub</a>
    </nav>
  </div>
</header>
<div class="shell">
  <aside class="side">{sidebar(slug)}</aside>
  <main>
    <p class="crumbs"><a href="/">hSUM</a> / <a href="{BASE}/">docs {VERSION}</a>{crumb}</p>
{body}
  </main>
</div>
<footer class="site">
  <div class="in">
    <span>hSUM {VERSION} — alpha</span>
    <a href="/llms.txt">llms.txt</a>
    <a href="https://github.com/burkan2/hSUM">Source</a>
    <a href="https://github.com/burkan2/hSUM/blob/main/SECURITY.md">Security</a>
  </div>
</footer>
</body>
</html>
"""


def write(slug: str, title: str, desc: str, body: str) -> None:
    crumb = f" / {title.lower()}" if slug else ""
    target = ROOT / slug / "index.html" if slug else ROOT / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page(slug, title, desc, body, crumb), encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT.parent.parent)}")


def build_error_catalog() -> None:
    """Carry the unchanged alpha.2 catalog into the shared alpha.4 docs shell."""
    source = Path(__file__).parent / "docs" / ERROR_SOURCE_VERSION / "errors"
    target = ROOT / "errors"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)

    for target_page in target.rglob("*.html"):
        rendered = target_page.read_text(encoding="utf-8")
        rendered = rendered.replace(ERROR_SOURCE_VERSION, VERSION)
        rendered = rendered.replace("alpha.2", "alpha.4")
        rendered = rendered.replace("All 64 public hSUM error subcodes",
                                    "All 65 public hSUM error subcodes")

        title_start = rendered.index("<title>") + len("<title>")
        title_end = rendered.index("</title>", title_start)
        source_title = rendered[title_start:title_end]
        desc_marker = '<meta name="description" content="'
        desc_start = rendered.index(desc_marker) + len(desc_marker)
        desc_end = rendered.index('">', desc_start)
        description = rendered[desc_start:desc_end]
        main_start = rendered.index('<main class="wrap">') + len('<main class="wrap">')
        main_end = rendered.index("</main>", main_start)
        source_body = rendered[main_start:main_end]
        body_start = source_body.index("<h1")
        body = source_body[body_start:].strip().replace(
            '<h1 style="font-size:28px">', "<h1>"
        )

        script_start = rendered.find("<script>", main_end)
        if script_start != -1:
            script_end = rendered.index("</script>", script_start) + len("</script>")
            body += "\n" + rendered[script_start:script_end]

        if target_page == target / "index.html":
            title = "Error codes"
            slug = "errors/"
            crumb = " / error codes"
        else:
            subcode = target_page.parent.name
            title = source_title.split(" — ", 1)[0]
            slug = f"errors/{subcode}/"
            crumb = f' / <a href="{BASE}/errors/">error codes</a> / {subcode}'

        target_page.write_text(
            page(slug, title, description, body, crumb), encoding="utf-8"
        )

    print(f"wrote {(target / 'index.html').relative_to(ROOT.parent.parent)} + 65 subcodes")


# ---------------------------------------------------------------- overview
write("", "Documentation", "hSUM documentation: local, offline evidence retrieval for coding agents.", """
<h1>hSUM documentation</h1>
<p class="lede">hSUM indexes a local filesystem into an immutable, citable evidence store,
then serves it to coding agents over a read-only MCP server. No account, no model
download, no network.</p>

<div class="note">
<p><strong>Alpha</strong></p>
<p>This documents <code>0.1.0-alpha.4</code>. Supported release archives are macOS
arm64 and Linux x86_64 on local filesystems. The crate is not published to crates.io.
See <a href="#boundaries">boundaries</a> for what is deliberately absent.</p>
</div>

<div class="note">
<p><strong>Compatible update</strong></p>
<p>Alpha.2 and alpha.3 indexes and citations remain compatible. Restart any
in-flight MCP pagination after upgrading because cursors are release-bound.</p>
</div>

<div class="cards">
  <div class="card"><h3><a href="quickstart/">Quickstart</a></h3><p>Install, index a repo, and run your first search in about five minutes.</p></div>
  <div class="card"><h3><a href="concepts/">Concepts</a></h3><p>Generations, citations, trust bindings, and why evidence is immutable.</p></div>
  <div class="card"><h3><a href="agents/">Connect an agent</a></h3><p>Install Codex once for repository-aware tools, or configure another MCP client.</p></div>
  <div class="card"><h3><a href="cli/">CLI reference</a></h3><p>Every command and flag in the alpha.4 surface.</p></div>
  <div class="card"><h3><a href="mcp/">MCP reference</a></h3><p>The four evidence tools, their inputs, and their JSON output.</p></div>
  <div class="card"><h3><a href="errors/">Error codes</a></h3><p>Every stable subcode with cause and fix.</p></div>
</div>

<h2>What hSUM does</h2>
<p>An agent asking "how does auth work here?" usually gets an answer assembled from
whatever happened to fit in context. hSUM answers with <em>passages</em>, each one
addressed by an immutable citation that resolves to exact bytes at an exact revision.</p>
<ol>
  <li><strong>Ingest</strong> walks a filesystem root and writes one atomic generation into a private SQLite index.</li>
  <li><strong>Search</strong> combines exact identifier matching, conservative quoted-phrase matching, and lexical BM25.</li>
  <li><strong>Get</strong> resolves an <code>hsum://v1</code> citation back to the exact bytes that were indexed.</li>
</ol>
<p>Retrieval is deterministic. The same query against the same generation returns the
same passages in the same order.</p>

<h2 id="boundaries">Boundaries</h2>
<p>Absent in alpha.4, deliberately — so you can rely on what is present:</p>
<div class="tablewrap">
<table>
<thead><tr><th>Area</th><th>Status</th></tr></thead>
<tbody>
<tr><td>Local filesystem ingest, lexical + exact retrieval</td><td><span class="badge yes">included</span></td></tr>
<tr><td>Read-only MCP stdio server</td><td><span class="badge yes">included</span></td></tr>
<tr><td>Immutable citations with revision pinning</td><td><span class="badge yes">included</span></td></tr>
<tr><td>Vector or semantic search, embeddings</td><td><span class="badge no">not in alpha.4</span></td></tr>
<tr><td>Account, telemetry, HTTP server, remote connectors</td><td><span class="badge no">not in alpha.4</span></td></tr>
<tr><td>File watcher, backup, restore, prune, migration</td><td><span class="badge no">not in alpha.4</span></td></tr>
</tbody>
</table>
</div>

<h2>Agent-readable docs</h2>
<p>A machine-readable summary of this site lives at
<a href="/llms.txt"><code>/llms.txt</code></a>, following the
<a href="https://llmstxt.org/">llms.txt</a> convention. Every documentation page is
static HTML with no client-side rendering, so agents can fetch any URL directly.</p>
""")

# --------------------------------------------------------------- quickstart
write("quickstart/", "Quickstart", "Install hSUM, index a repository, and run your first cited search.", """
<h1>Quickstart</h1>
<p class="lede">From a clean checkout to a cited search result. Nothing leaves your machine.</p>

<h2>Requirements</h2>
<ul>
  <li>macOS arm64 or Linux x86_64</li>
  <li>A local repository to index</li>
</ul>

<h2>1. Install and connect Codex</h2>
<p>Run these commands from the Git repository you want hSUM to index. The
version-pinned installer verifies the release archive, installs without
<code>sudo</code>, registers one user-wide Codex MCP server, activates this exact
repository, and completes an end-to-end citation probe.</p>
<pre><code>version=0.1.0-alpha.4
base_url="https://github.com/burkan2/hSUM/releases/download/v$version"
curl -fsSLO "$base_url/install-hsum.sh"
curl -fsSLO "$base_url/SHA256SUMS"
grep ' install-hsum.sh$' SHA256SUMS | shasum -a 256 -c -
bash install-hsum.sh --activate . --confirm</code></pre>
<div class="note warn">
<p><strong>Unsigned macOS prerelease</strong></p>
<p>The linker-generated ad-hoc signature passes <code>codesign --verify</code>, but
the alpha.4 binary has no Developer ID identity and is not notarized. On first launch,
the installer requires the explicit <code>--allow-unnotarized-alpha</code> flag after
you verify its checksum and read this warning.</p>
</div>
<p>On macOS, repeat the final command as:</p>
<pre><code>bash install-hsum.sh --activate . --confirm --allow-unnotarized-alpha</code></pre>
<p>Confirm the installed integration at any time:</p>
<pre><code>hsum --version
hsum integration status codex --json</code></pre>

<details>
<summary>Build from source instead</summary>
<pre><code>git clone https://github.com/burkan2/hSUM.git
cd hSUM
cargo build --locked --release</code></pre>
<p>This requires Rust <code>1.91.0</code>, pinned in
<code>rust-toolchain.toml</code>. The binary lands at
<code>target/release/hsum</code>.</p>
</details>

<h2>2. Initialize an index manually (optional)</h2>
<p>The installer already activates and indexes the selected repository. For a
manual or non-Codex setup, run <code>init</code> from inside the repository you want
indexed. hSUM selects the enclosing Git root by default.</p>
<pre><code>hsum init .</code></pre>
<p>Real output:</p>
<pre><code>hSUM index initialized.
Root: /path/to/repo
Index: repo
Project: default
Data: ~/.local/share/hsum/indexes/repo/index.sqlite
Binding: 495d788b-897c-46b6-86c2-5d28d80b3d42
Eligible files: 2
Eligible bytes: 194
Skipped files: 0
Pointer: not requested
Active documents: 2
Active passages: 2
Lexical search is ready. No model or network was used.</code></pre>
<p>Save that <strong>binding UUID</strong>. It authorizes MCP access to this project and
is required by <code>hsum mcp --binding</code>.</p>

<div class="note">
<p><strong>Preview first</strong></p>
<p>Use <code>hsum init . --dry-run</code> to inspect file selection and corpus estimates
without writing anything.</p>
</div>

<h2>3. Search</h2>
<pre><code>hsum search 'bearer token'</code></pre>
<pre><code>1  repo://src/auth.rs:1-4  [metadata_unchanged]
   BM25 #1
   /// Validate a bearer token against the session store.
   citation: 'hsum://v1/30bf24f0-.../c06745b2-...?rev=a893b630...#bytes=0-152'
stop: unique_exhausted</code></pre>
<p>Each result carries a citation. That string is the durable handle to the passage.</p>

<h2>4. Resolve a citation</h2>
<pre><code>hsum get 'hsum://v1/30bf24f0-.../c06745b2-...?rev=a893b630...#bytes=0-152'</code></pre>
<pre><code>Citation: hsum://v1/30bf24f0-.../c06745b2-...?rev=a893b630...#bytes=0-152
Source: repo://src/auth.rs
Title: auth.rs
Lines: 1-4
Source hash: not_requested
Content: /// Validate a bearer token against the session store.</code></pre>
<p>Quote the citation in your shell — it contains <code>?</code> and <code>#</code>,
which most shells will otherwise interpret.</p>

<h2>5. Refresh after edits</h2>
<p>hSUM has no file watcher in alpha.4. Re-run <code>ingest</code> after changing files:</p>
<pre><code>hsum ingest</code></pre>
<p>Each run commits one atomic generation. Existing citations keep resolving to the
revision they pinned.</p>

<h2>Upgrading an alpha.1 index</h2>
<p>Indexes created by alpha.1 use an older indexing pipeline. If a command reports
<code>PIPELINE_FINGERPRINT</code>, rebuild the trusted index under the current rules:</p>
<pre><code>hsum init --rebuild --dry-run
hsum init --rebuild</code></pre>
<p>The dry run previews the replacement without writing. The rebuild creates a new
index and trust binding, then removes the old index. Evidence and citations created by
alpha.1 do not survive this replacement.</p>
<p>Alpha.2 and alpha.3 indexes do not need a rebuild for alpha.4. Existing citations
continue to resolve; restart any in-flight MCP pagination after replacing the binary.</p>

<h2>Next</h2>
<ul>
  <li><a href="../agents/">Connect an agent</a> so your assistant can query this index</li>
  <li><a href="../concepts/">Concepts</a> for how generations and citations work</li>
  <li><a href="../cli/">CLI reference</a> for every flag</li>
</ul>
""")

# ----------------------------------------------------------------- concepts
write("concepts/", "Concepts", "Generations, citations, trust bindings, and the guarantees hSUM makes.", """
<h1>Concepts</h1>
<p class="lede">Five ideas explain most of hSUM's behavior.</p>

<h2>Index and project</h2>
<p>An <strong>index</strong> is one SQLite database bound to one filesystem root. A
<strong>project</strong> is a named scope inside it; alpha.4 creates <code>default</code>
automatically. Both get a stable UUID that appears in every citation.</p>
<pre><code>hsum context</code></pre>
<pre><code>Index: repo
Index ID: 30bf24f0-457f-4bf2-b56d-cb33ba0eb547
Project: default
Project ID: d385f3cf-c799-45fb-9851-18071cc86059
Source root: /path/to/repo
Binding: 495d788b-897c-46b6-86c2-5d28d80b3d42
Selection: trusted_root</code></pre>

<h2>Generations</h2>
<p>Every <code>ingest</code> commits one <strong>generation</strong> — an atomic snapshot
of the source. Either the whole generation lands or none of it does; there is no
half-updated index. <code>hsum status</code> reports the current generation number.</p>
<p>A single-writer advisory lock serializes ingests. Concurrent readers are never
blocked, so an agent can search while an ingest runs.</p>

<h2>Citations</h2>
<p>A citation names exact bytes at an exact revision:</p>
<pre><code>hsum://v1/&lt;index_id&gt;/&lt;source_id&gt;/&lt;document_id&gt;?rev=&lt;sha256&gt;#bytes=&lt;start&gt;-&lt;end&gt;</code></pre>
<div class="tablewrap">
<table>
<thead><tr><th>Part</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td><code>index_id</code></td><td>UUID of the index that produced the passage</td></tr>
<tr><td><code>source_id</code></td><td>UUID of the source file</td></tr>
<tr><td><code>document_id</code></td><td>UUID of the indexed document</td></tr>
<tr><td><code>rev</code></td><td>SHA-256 of the file revision at index time</td></tr>
<tr><td><code>bytes</code></td><td>Half-open byte span within that revision</td></tr>
</tbody>
</table>
</div>
<p>Because <code>rev</code> pins content, a citation cannot silently drift. Edit the file
and the old citation still resolves to what was actually indexed. Pass
<code>--verify-source-hash</code> to <code>get</code> to check the current file against
the pinned revision.</p>

<div class="note">
<p><strong>Why this matters for agents</strong></p>
<p>An agent that answers with a citation is making a checkable claim. You can resolve it
yourself and see the exact bytes, rather than trusting a paraphrase.</p>
</div>

<h2>Trust bindings</h2>
<p>The MCP server refuses to serve a project unless the caller presents a
<strong>binding UUID</strong> created by <code>hsum init</code> or <code>hsum trust</code>.
The binding is user-side state, not a secret embedded in the repo, so cloning a
repository grants no access to anyone's index.</p>
<pre><code>hsum trust /path/to/repo --confirm</code></pre>
<p><code>--confirm</code> is required; hSUM never creates a trust binding implicitly.</p>

<h2>Untrusted content</h2>
<p>Every search and get result carries <code>"untrusted_content": true</code>. Indexed
files are data, not instructions — if a repository contains text telling an agent to take
an action, that text is content to be reported, never a command to follow.</p>
<div class="note warn">
<p><strong>Prompt injection</strong></p>
<p>Treat retrieved passages as untrusted input. hSUM marks them, but the agent runtime
must honor the marking.</p>
</div>

<h2>Retrieval</h2>
<p>alpha.4 runs three retrievers and merges them: exact identifier matching, conservative
quoted-phrase matching, and lexical BM25. <code>--mode auto</code> and
<code>--mode lexical</code> are equivalent in this release. There is no vector search and
no embedding model, which is why first-run needs no download.</p>
<p>Retrieval is bounded. <code>--timeout-ms</code> (default <code>3000</code>) caps work,
and the response reports a <code>stop_reason</code> such as <code>limit_reached</code> or
<code>unique_exhausted</code> so you can tell a complete result from a truncated one.</p>
""")

# ------------------------------------------------------------------- agents
write("agents/", "Connect an agent", "Give Codex automatic repository-scoped hSUM tools, or generate binding-pinned MCP config for other clients.", """
<h1>Connect an agent</h1>
<p class="lede">Codex gets one user-wide hSUM registration that resolves each task to
its exact trusted repository. Other clients keep the explicit, binding-pinned MCP
configuration path.</p>

<h2>Codex: install once, use in every task</h2>
<pre><code>hsum integration install codex --activate . --confirm
hsum integration status codex --json</code></pre>
<p>The install command uses Codex's supported <code>mcp add/get</code> CLI, reads the
effective registration back, launches that exact server command, verifies all four
read-only tools, and completes an <code>evidence_search</code> to
<code>evidence_get</code> citation round trip. It also installs a bounded managed
block in Codex's user-global agent instructions so future agents know when to call
hSUM. No copied TOML or Codex restart is required.</p>
<p>Every later Codex task in this repository sees hSUM automatically. In another
repository the first tool call returns a structured activation request with the exact
repository root and command. After repository-specific consent, the agent can activate
that repository and retry the same tool without restarting MCP.</p>

<h2>Many repositories</h2>
<pre><code>hsum integration authorize-workspace codex --path ~/Projects --confirm
hsum integration revoke-workspace codex --path ~/Projects --confirm</code></pre>
<p>Authorization does not recursively scan or combine <code>~/Projects</code>. The
first hSUM tool call below that directory initializes only the exact Git repository for
the current task. Each repository keeps a separate index, trust binding, generation,
and citation namespace. Home, filesystem root, overly broad paths, and Git repositories
themselves are refused as workspace scopes.</p>

<h2>Claude Code / Claude Desktop</h2>
<p>Run this from inside an indexed repository. hSUM emits a copyable snippet with the
correct absolute binary path and binding UUID already filled in:</p>
<pre><code>hsum client config claude-code</code></pre>
<pre><code>{
  "mcpServers": {
    "hsum": {
      "args": [
        "mcp",
        "--binding",
        "495d788b-897c-46b6-86c2-5d28d80b3d42"
      ],
      "command": "/absolute/path/to/hsum"
    }
  }
}</code></pre>

<p>Also supported: <code>claude-desktop</code> and <code>generic</code>. Add
<code>--format toml</code> for TOML instead of JSON. <code>client config codex</code>
remains a low-level escape hatch and emits the workspace-dynamic
<code>hsum mcp</code> command.</p>

<h2>Memory and company-brain tools</h2>
<p>hSUM can run beside claude-mem and other agent-memory or company-brain
systems. Each MCP server keeps its own registration and storage. The hSUM
installer claims the <code>hsum</code> server name and appends one checksummed
block to Codex's user instructions. It preserves other MCP entries and
instruction text. If another command owns the <code>hsum</code> name, hSUM stops
installation and reports the conflict.</p>

<div class="tablewrap">
<table>
<thead><tr><th>Need</th><th>Use</th></tr></thead>
<tbody>
<tr><td>Current repository structure and implementation</td><td>hSUM search and citations</td></tr>
<tr><td>Past sessions, decisions, and unfinished work</td><td>Your agent-memory system</td></tr>
<tr><td>Knowledge shared across repositories or teams</td><td>Your company-brain system</td></tr>
<tr><td>Current contents of a file you are editing</td><td>An ordinary file read</td></tr>
</tbody>
</table>
</div>

<p>hSUM does not read another tool's SQLite database, vector store, worker,
hooks, or cloud API. In alpha.4, hSUM indexes supported files inside an
authorized repository. If a memory tool writes supported Markdown or text files
into that repository, hSUM includes them in the corpus. hSUM may return that
content to the MCP client, which may forward it to a model provider under the
client's policy.</p>

<p>A memory system may record hSUM tool calls and summarize returned passages.
Keep the <code>hsum://v1</code> citation when you need exact evidence. If a
memory summary conflicts with the current repository, read the file and call
<code>evidence_get</code> with source-hash verification.</p>

<div class="note warn">
<p><strong>Privacy</strong></p>
<p>hSUM uploads no corpus data and no telemetry. But a cloud-backed agent may send
returned passages to its model provider under that client's policy. The boundary is the
client, not hSUM.</p>
</div>

<h2>Verify or repair the connection</h2>
<pre><code>hsum integration status codex
hsum integration repair codex --confirm
hsum client doctor claude-code</code></pre>
<p><code>integration status</code> checks the effective Codex registration and managed
agent policy. <code>repair</code> restores drifted managed state. The lower-level
<code>client doctor</code> validates a binding-pinned client command and read-only MCP
probe.</p>

<h2>Use it well</h2>
<p>Three habits make hSUM materially better in an agent loop:</p>
<ul>
  <li><strong>Ask for citations.</strong> Instruct the agent to cite <code>hsum://v1</code>
      URIs for claims about the codebase, so you can verify them.</li>
  <li><strong>Let managed Codex tasks refresh.</strong> An activated repository attempts
      one bounded refresh before the first search or citation read in each task. Manual
      integrations still use <code>hsum ingest</code>.</li>
  <li><strong>Treat passages as data.</strong> Results are marked
      <code>untrusted_content</code> — never let retrieved text act as instructions.</li>
</ul>

<p>You do not need to edit each repository's <code>AGENTS.md</code>. The managed
user-global policy supplies the bounded guidance while preserving existing user
instructions.</p>
""")

# ---------------------------------------------------------------------- mcp
write("mcp/", "MCP reference", "The four read-only evidence tools exposed by the hSUM MCP server.", """
<h1>MCP reference</h1>
<p class="lede"><code>hsum mcp</code> is workspace-dynamic for the managed Codex
integration; <code>hsum mcp --binding &lt;UUID&gt;</code> is the binding-pinned manual
form. Both speak MCP over stdio and expose exactly four read-only evidence tools.</p>

<h2>Tools</h2>
<div class="tablewrap">
<table>
<thead><tr><th>Tool</th><th>Purpose</th></tr></thead>
<tbody>
<tr><td><code>evidence_search</code></td><td>Search ranked immutable passages with stable citations and live-source state.</td></tr>
<tr><td><code>evidence_get</code></td><td>Resolve a citation to exact indexed bytes and optionally compare the live source hash.</td></tr>
<tr><td><code>evidence_project</code></td><td>Describe the bound filesystem root, indexed extensions, sources, and generation.</td></tr>
<tr><td><code>evidence_status</code></td><td>Report corpus counts, source health, and actionable index or storage problems.</td></tr>
</tbody>
</table>
</div>

<h2>evidence_search</h2>
<p>Returns ranked passages, each with a citation. Bounded by a deadline; the response
always reports why it stopped.</p>
<p>Representative response shape. IDs, hashes, timestamps, content, and byte counts
depend on the indexed project:</p>
<pre><code>{
  "schema_version": "hsum.api.v1",
  "request_id": "dd2ce7eb-0210-4558-ac59-1b8f6d77f0bd",
  "project_id": "bed633a6-3104-4010-8f1d-1742eed33e37",
  "scope_revision": 0,
  "generation": 1,
  "index_epoch": 1,
  "requested_mode": "auto",
  "effective_mode": "lexical",
  "retrievers": ["exact", "lexical"],
  "results": [
    {
      "citation_uri": "hsum://v1/72d90a91-8ae9-4086-b6d1-fc5d57ec99d6/8f6e262c-8776-51f1-a6f6-1f00f59eb5ac/920f61f9-8e4b-4b9d-b956-74be23e208ab?rev=3df02786a19348563b8df57f99c27835d2ea7f6fd963e5d340314993dcf78780#bytes=0-152",
      "index_id": "72d90a91-8ae9-4086-b6d1-fc5d57ec99d6",
      "source_id": "8f6e262c-8776-51f1-a6f6-1f00f59eb5ac",
      "document_id": "920f61f9-8e4b-4b9d-b956-74be23e208ab",
      "revision_sha256": "3df02786a19348563b8df57f99c27835d2ea7f6fd963e5d340314993dcf78780",
      "source_uri": "repo://src/auth.rs",
      "title": "auth.rs",
      "byte_span": { "start": 0, "end": 152 },
      "line_span": { "start": 1, "end": 4 },
      "content": "/// Validate a bearer token against the session store.",
      "content_sha256": "13773ba003aeaba93cd8ac3e70c57a3dce7f77019f3b6a9251ad94bcb227576e",
      "source_updated_at": "2026-07-26T03:07:09.089070016Z",
      "indexed_at": "2026-07-26T03:39:06.0135Z",
      "head_generation": 1,
      "source_state": "metadata_unchanged",
      "untrusted_content": true,
      "score": null,
      "duplicate_citations": []
    }
  ],
  "next_cursor": null,
  "stop_reason": "unique_exhausted",
  "truncated": false,
  "body_bytes": 54
}</code></pre>

<h3>Fields worth reading</h3>
<div class="tablewrap">
<table>
<thead><tr><th>Field</th><th>Why it matters</th></tr></thead>
<tbody>
<tr><td><code>stop_reason</code></td><td>Why candidate collection stopped: <code>limit_reached</code>, <code>unique_exhausted</code>, <code>work_budget_exhausted</code>, or <code>deadline</code>. Pagination completeness is reported separately.</td></tr>
<tr><td><code>next_cursor</code></td><td>Non-null when another page exists. Pass it back unchanged to continue the same query and snapshot.</td></tr>
<tr><td><code>truncated</code></td><td><code>true</code> when this page omits fetched results because of the requested page size or response-size ceiling.</td></tr>
<tr><td><code>body_bytes</code></td><td>Total raw content bytes returned in this page.</td></tr>
<tr><td><code>effective_mode</code></td><td>What actually ran. In alpha.4 <code>auto</code> resolves to <code>lexical</code>.</td></tr>
<tr><td><code>score</code></td><td><code>null</code> unless the request sets <code>explain: true</code>; then it contains fused and per-retriever rank details.</td></tr>
<tr><td><code>source_state</code></td><td>Whether the file changed since indexing.</td></tr>
<tr><td><code>untrusted_content</code></td><td>Always <code>true</code>. Passages are data, never instructions.</td></tr>
</tbody>
</table>
</div>

<h2>evidence_get</h2>
<p>Resolves a citation to exact bytes.</p>
<pre><code>{
  "schema_version": "hsum.api.v1",
  "request_id": "1babdb7a-ec57-4644-9715-e4c5228257ba",
  "requested_citation_uri": "hsum://v1/72d90a91-8ae9-4086-b6d1-fc5d57ec99d6/8f6e262c-8776-51f1-a6f6-1f00f59eb5ac/920f61f9-8e4b-4b9d-b956-74be23e208ab?rev=3df02786a19348563b8df57f99c27835d2ea7f6fd963e5d340314993dcf78780#bytes=0-152",
  "returned_citation_uri": "hsum://v1/72d90a91-8ae9-4086-b6d1-fc5d57ec99d6/8f6e262c-8776-51f1-a6f6-1f00f59eb5ac/920f61f9-8e4b-4b9d-b956-74be23e208ab?rev=3df02786a19348563b8df57f99c27835d2ea7f6fd963e5d340314993dcf78780#bytes=0-152",
  "requested_line_span": { "start": 1, "end": 4 },
  "returned_line_span": { "start": 1, "end": 4 },
  "source_uri": "repo://src/auth.rs",
  "title": "auth.rs",
  "metadata": {},
  "source_updated_at": "2026-07-26T03:07:09.089070016Z",
  "indexed_at": "2026-07-26T03:39:06.0135Z",
  "content": "/// Validate a bearer token against the session store.",
  "body_sha256": "13773ba003aeaba93cd8ac3e70c57a3dce7f77019f3b6a9251ad94bcb227576e",
  "source_state": "content_unchanged",
  "source_hash_verification": "unchanged",
  "untrusted_content": true
}</code></pre>
<p>Compare <code>requested_</code> against <code>returned_</code> citations and line
spans. <code>get</code> may widen the requested passage to whole stored chunks while
staying within <code>max_bytes</code>. Set <code>verify_source_hash: true</code> to report
whether the current file still has the indexed content hash.</p>

<h2>evidence_project</h2>
<p>Call this before interpreting a search miss. It states the filesystem coverage
of the project selected when the MCP server started.</p>
<pre><code>{
  "schema_version": "hsum.api.v1",
  "request_id": "aaf27f18-48ad-4572-993e-b21cb8540962",
  "project_id": "bed633a6-3104-4010-8f1d-1742eed33e37",
  "name": "default",
  "scope_revision": 0,
  "root": "/workspace/example",
  "indexed_extensions": [
    ".md", ".markdown", ".txt", ".rs", ".py", ".ts", ".tsx",
    ".js", ".jsx", ".go", ".java", ".kt", ".kts", ".c", ".h",
    ".cpp", ".hpp", ".cc", ".hh", ".cxx", ".rb", ".cs", ".swift",
    ".php", ".scala", ".sh", ".bash", ".sql"
  ],
  "sources": [
    {
      "source_id": "8f6e262c-8776-51f1-a6f6-1f00f59eb5ac",
      "name": "workspace",
      "adapter_kind": "filesystem",
      "logical_uri": "/workspace/example",
      "last_success_at": "2026-07-26T03:39:06.0135Z"
    }
  ],
  "last_successful_generation": 1
}</code></pre>

<h2>evidence_status</h2>
<p>Use this when a search returns nothing unexpected. It separates an empty or
unhealthy corpus from a genuine absence.</p>
<pre><code>{
  "schema_version": "hsum.api.v1",
  "request_id": "45d17701-0abe-4d7b-b060-df52191889c7",
  "index_id": "72d90a91-8ae9-4086-b6d1-fc5d57ec99d6",
  "project_id": "bed633a6-3104-4010-8f1d-1742eed33e37",
  "active_generation": 1,
  "index_epoch": 1,
  "source_count": 1,
  "document_count": 42,
  "passage_count": 318,
  "model_fingerprint": null,
  "degraded_modes": [],
  "health_issues": [],
  "index_problems": [],
  "read_only": true,
  "query_only": true
}</code></pre>
<p><code>health_issues</code> reports per-source ingest failures.
<code>index_problems</code> reports actionable index or storage problems and includes
a repair command when one exists. Alpha.2 has no model path, so
<code>model_fingerprint</code> is <code>null</code>.</p>

<h2>Errors</h2>
<p>Failures return a stable machine-readable envelope, not prose:</p>
<pre><code>{
  "code": "NOT_FOUND",
  "subcode": "INDEX_NOT_FOUND",
  "message": "the selected hSUM index is unavailable",
  "retryable": false,
  "next_action": "run hsum context, then initialize or select the intended index",
  "request_id": "e4a44cac-9c23-4f29-a618-cb5895346113"
}</code></pre>
<p>Branch on <code>subcode</code>, not <code>message</code>. Use <code>retryable</code> to
decide whether a retry can help. Every subcode is documented under
<a href="../errors/">error codes</a>, and offline via
<code>hsum help error &lt;SUBCODE&gt;</code>.</p>
""")

# ---------------------------------------------------------------------- cli
write("cli/", "CLI reference", "Every hSUM 0.1.0-alpha.4 command and flag.", """
<h1>CLI reference</h1>
<p class="lede">The complete alpha.4 command surface. Later release-train commands do not
appear as stubs.</p>

<h2>Global options</h2>
<p>Accepted by every command:</p>
<div class="tablewrap">
<table>
<thead><tr><th>Flag</th><th>Effect</th></tr></thead>
<tbody>
<tr><td><code>-v, --verbose...</code></td><td>Increase diagnostic detail; repeat for more</td></tr>
<tr><td><code>-q, --quiet</code></td><td>Suppress progress, preserve errors and results</td></tr>
<tr><td><code>--no-progress</code></td><td>Disable progress, keep warnings and summaries</td></tr>
<tr><td><code>--no-color</code></td><td>Disable colored output</td></tr>
<tr><td><code>--config &lt;PATH&gt;</code></td><td>Use an explicit configuration file</td></tr>
<tr><td><code>--data-dir &lt;PATH&gt;</code></td><td>Override the managed data directory</td></tr>
<tr><td><code>--cache-dir &lt;PATH&gt;</code></td><td>Override the managed cache directory</td></tr>
</tbody>
</table>
</div>

<h2>init</h2>
<p>Create one local filesystem-backed index and project.</p>
<pre><code>hsum init [OPTIONS] [PATH]</code></pre>
<div class="tablewrap">
<table>
<thead><tr><th>Flag</th><th>Effect</th></tr></thead>
<tbody>
<tr><td><code>--index &lt;NAME&gt;</code></td><td>Collision-safe logical index name</td></tr>
<tr><td><code>--project &lt;NAME&gt;</code></td><td>Collision-safe logical project name</td></tr>
<tr><td><code>--rebuild</code></td><td>Replace the trusted index for this root and re-ingest from scratch</td></tr>
<tr><td><code>--no-ingest</code></td><td>Create config and trust state without the first ingest</td></tr>
<tr><td><code>--dry-run</code></td><td>Inspect selection and estimates without writing</td></tr>
<tr><td><code>--write-pointer</code></td><td>Write the optional repository pointer</td></tr>
<tr><td><code>--force-pointer</code></td><td>Replace a conflicting repository pointer</td></tr>
<tr><td><code>--allow-broad-root</code></td><td>Confirm a normally refused broad root</td></tr>
<tr><td><code>--allow-large-source</code></td><td>Confirm a source above default limits</td></tr>
<tr><td><code>--index-quota-bytes &lt;BYTES&gt;</code></td><td>Max managed index bytes, including recovery reserve</td></tr>
</tbody>
</table>
</div>

<h2>trust</h2>
<p>Authorize a canonical repository root for direct and MCP use.</p>
<pre><code>hsum trust &lt;PATH&gt; --confirm</code></pre>
<p><code>--confirm</code> is mandatory. Optional: <code>--index &lt;NAME&gt;</code>,
<code>--project &lt;NAME&gt;</code>.</p>

<h2>ingest</h2>
<p>Refresh the filesystem source into one atomic generation.</p>
<pre><code>hsum ingest [OPTIONS]</code></pre>
<div class="tablewrap">
<table>
<thead><tr><th>Flag</th><th>Effect</th></tr></thead>
<tbody>
<tr><td><code>--dry-run</code></td><td>Discover, validate, estimate — commit nothing</td></tr>
<tr><td><code>--lock-timeout-ms &lt;MS&gt;</code></td><td>Max wait for the single-writer lock (default <code>5000</code>)</td></tr>
<tr><td><code>--allow-empty-snapshot</code></td><td>Confirm replacing a nonempty source with an empty one</td></tr>
<tr><td><code>--allow-mass-delete</code></td><td>Confirm a deletion above the mass-delete budget</td></tr>
</tbody>
</table>
</div>

<h2>search</h2>
<p>Search exact identifiers, conservative quotes, and active lexical text.</p>
<pre><code>hsum search &lt;QUERY&gt; [OPTIONS]</code></pre>
<div class="tablewrap">
<table>
<thead><tr><th>Flag</th><th>Effect</th></tr></thead>
<tbody>
<tr><td><code>--mode &lt;MODE&gt;</code></td><td><code>auto</code> or <code>lexical</code> (equivalent in alpha.4)</td></tr>
<tr><td><code>--limit &lt;N&gt;</code></td><td>Max passages (default <code>10</code>)</td></tr>
<tr><td><code>--cursor &lt;VALUE&gt;</code></td><td>Continue a stable, scope-bound result page</td></tr>
<tr><td><code>--timeout-ms &lt;MS&gt;</code></td><td>Retrieval deadline (default <code>3000</code>)</td></tr>
<tr><td><code>--json</code></td><td>Emit exactly one JSON document</td></tr>
<tr><td><code>--explain</code></td><td>Include retriever scoring and stop information</td></tr>
</tbody>
</table>
</div>

<h2>get</h2>
<p>Resolve immutable bytes from an <code>hsum://v1</code> citation.</p>
<pre><code>hsum get &lt;CITATION_URI&gt; [OPTIONS]</code></pre>
<div class="tablewrap">
<table>
<thead><tr><th>Flag</th><th>Effect</th></tr></thead>
<tbody>
<tr><td><code>--max-bytes &lt;N&gt;</code></td><td>Max returned UTF-8 bytes (default <code>16384</code>)</td></tr>
<tr><td><code>--verify-source-hash</code></td><td>Probe the current source hash against the pinned revision</td></tr>
<tr><td><code>--json</code></td><td>Emit exactly one JSON document</td></tr>
</tbody>
</table>
</div>
<p>Quote the citation — it contains <code>?</code> and <code>#</code>.</p>

<h2>status, doctor, context</h2>
<div class="tablewrap">
<table>
<thead><tr><th>Command</th><th>Purpose</th></tr></thead>
<tbody>
<tr><td><code>hsum status [--problems] [--json]</code></td><td>Index state, generation, counts, disk budget</td></tr>
<tr><td><code>hsum doctor</code></td><td>Read-only diagnosis; no repair switches by design</td></tr>
<tr><td><code>hsum context [--json]</code></td><td>Effective index, project, root, binding, config origins</td></tr>
</tbody>
</table>
</div>

<h2>client</h2>
<pre><code>hsum client config &lt;CLIENT&gt; [--format json|toml]
hsum client doctor &lt;CLIENT&gt;</code></pre>
<p>Clients: <code>codex</code>, <code>claude-code</code>, <code>claude-desktop</code>,
<code>generic</code>. See <a href="../agents/">Connect an agent</a>.</p>

<h2>integration</h2>
<pre><code>hsum integration install codex --activate &lt;PATH&gt; --confirm
hsum integration status codex [--json]
hsum integration repair codex --confirm
hsum integration uninstall codex --confirm
hsum integration authorize-workspace codex --path &lt;PATH&gt; --confirm
hsum integration revoke-workspace codex --path &lt;PATH&gt; --confirm</code></pre>
<p>Manages the single user-wide Codex registration, bounded agent policy, exact
repository activation, and optional lazy enrollment beneath a safe projects
directory. See <a href="../agents/">Connect an agent</a> for the repository-isolation
and consent model.</p>

<h2>mcp</h2>
<pre><code>hsum mcp
hsum mcp --binding &lt;UUID&gt;</code></pre>
<p>The no-argument form resolves the exact repository from the server process's
working directory for managed Codex tasks. <code>--binding</code> pins a manual client
to one trusted project. <code>--project &lt;NAME&gt;</code> selects a project only inside an
already trusted direct-CLI context.</p>

<h2>help, completions, man</h2>
<pre><code>hsum help error &lt;SUBCODE&gt;
hsum completions &lt;SHELL&gt;
hsum man</code></pre>
<p><code>help error</code> works offline and is version-pinned to the binary.</p>
""")

# ---------------------------------------------------------- troubleshooting
write("troubleshooting/", "Troubleshooting", "Common hSUM failures and how to resolve them.", """
<h1>Troubleshooting</h1>
<p class="lede">Start with <code>hsum context</code> and <code>hsum doctor</code>. Between
them they explain most failures.</p>

<h2>Read an error</h2>
<p>hSUM errors name a cause, a fix, and a stable subcode:</p>
<pre><code>problem: the selected hSUM index is unavailable
cause: no authorized managed index matches the selection
fix: run hsum context, then initialize or select the intended index
learn: hsum help error INDEX_NOT_FOUND — code: INDEX_NOT_FOUND — request: d4db1501-...</code></pre>
<p>Every subcode has an offline explanation:</p>
<pre><code>hsum help error INDEX_NOT_FOUND</code></pre>

<h2>INDEX_NOT_FOUND</h2>
<p>The most common first-run failure. hSUM cannot find an index for the current
selection. Causes, in order of likelihood:</p>
<ul>
  <li>You are not inside the indexed root. <code>cd</code> into it, or run <code>hsum context</code> to see what is selected.</li>
  <li>You passed <code>--data-dir</code> or <code>--cache-dir</code> on one command but not the next. These must match across invocations.</li>
  <li><code>HSUM_HOME</code> differs between shells, so config resolves elsewhere.</li>
  <li>No index exists yet — run <code>hsum init .</code>.</li>
</ul>

<h2>PIPELINE_FINGERPRINT after upgrading</h2>
<p>The index was built by different indexing rules and cannot be read safely by this
binary. Replace it explicitly:</p>
<pre><code>hsum init --rebuild --dry-run
hsum init --rebuild</code></pre>
<p>The dry run writes nothing. The rebuild replaces the trusted index and binding.
Evidence and citations recorded before the pipeline change no longer resolve.</p>

<h2>Search returns nothing</h2>
<ul>
  <li>Confirm documents exist: <code>hsum status</code> reports active documents and passages.</li>
  <li>Re-run <code>hsum ingest</code> if files changed. There is no watcher in alpha.4.</li>
  <li>alpha.4 is lexical, not semantic. Search for identifiers and phrases that literally appear in the source; conceptual paraphrases will not match.</li>
  <li>Check <code>stop_reason</code> in <code>--json</code> output to see whether retrieval was truncated.</li>
</ul>

<h2>Agent cannot see the server</h2>
<ol>
  <li>Run <code>hsum client doctor &lt;CLIENT&gt;</code> — it validates the executable, binding, scope, framing, and runs a read-only probe.</li>
  <li>Confirm the config uses an <strong>absolute</strong> path to the binary.</li>
  <li>Confirm the binding UUID matches <code>hsum context</code>.</li>
  <li>Regenerate the snippet with <code>hsum client config &lt;CLIENT&gt;</code> rather than hand-editing.</li>
</ol>

<h2>WRITER_LOCK</h2>
<p>Another ingest holds the single-writer lock. Wait, or raise the ceiling:</p>
<pre><code>hsum ingest --lock-timeout-ms 30000</code></pre>
<p>Readers are never blocked, so search keeps working during an ingest.</p>

<h2>Refused operations</h2>
<p>hSUM refuses destructive or surprising actions until you confirm them explicitly:</p>
<div class="tablewrap">
<table>
<thead><tr><th>Subcode</th><th>Confirm with</th></tr></thead>
<tbody>
<tr><td><code>BROAD_ROOT_CONFIRMATION_REQUIRED</code></td><td><code>hsum init --allow-broad-root</code></td></tr>
<tr><td><code>LARGE_SOURCE_CONFIRMATION_REQUIRED</code></td><td><code>hsum init --allow-large-source</code></td></tr>
<tr><td><code>EMPTY_SNAPSHOT_CONFIRMATION_REQUIRED</code></td><td><code>hsum ingest --allow-empty-snapshot</code></td></tr>
<tr><td><code>MASS_DELETE_CONFIRMATION_REQUIRED</code></td><td><code>hsum ingest --allow-mass-delete</code></td></tr>
<tr><td><code>TRUST_CONFIRMATION_REQUIRED</code></td><td><code>hsum trust &lt;PATH&gt; --confirm</code></td></tr>
</tbody>
</table>
</div>
<p>Read the message before confirming — each guards a real footgun.</p>

<h2>Citation errors in the shell</h2>
<p>Citations contain <code>?</code> and <code>#</code>. Unquoted, your shell will mangle
them into <code>CITATION_MALFORMED</code>. Always quote:</p>
<pre><code>hsum get 'hsum://v1/...?rev=...#bytes=0-152'</code></pre>

<h2>Still stuck</h2>
<ul>
  <li><a href="../errors/">Full error code index</a></li>
  <li><a href="https://github.com/burkan2/hSUM/issues">Open an issue</a> — include the <code>request_id</code> and <code>hsum --version --verbose</code></li>
  <li><a href="https://github.com/burkan2/hSUM/blob/main/SECURITY.md">Report a security issue privately</a></li>
</ul>
""")

build_error_catalog()

print("done")
