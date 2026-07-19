//! Deterministic Rust parity projection of `scripts/build_chunk_registry.py`.
//! Python remains the schema and policy authority; output bytes must match it.

use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::env;
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

const FORMAT_VERSION: &str = "2.0.0";
const GENERATOR_VERSION: &str = "2.0.0";
const REPOSITORY_ID: &str = "anthropics/claude-for-legal";
const CHUNK_PREFIX: &str = "chk:sha256:";
const PARENT_PREFIX: &str = "parent:sha256:";
const EDGE_PREFIX: &str = "edge:sha256:";
const FORBIDDEN_PUBLIC_SUBSTRINGS: &[&str] = &[
    ".private/",
    "private/",
    "raw-research",
    "raw_capture",
    "raw-capture",
    "BEGIN PRIVATE KEY",
    "AWS_SECRET",
    "api_key=",
    "authorization: bearer",
    "c:\\users\\",
];

#[derive(Clone)]
struct TreeBlob {
    path: String,
    object_id: String,
    data: Vec<u8>,
}

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

fn hash(bytes: &[u8]) -> String {
    hex(&Sha256::digest(bytes))
}

fn is_repo_root(path: &Path) -> bool {
    path.join("UPSTREAM.lock.json").is_file()
        && path.join("registry").join("chunk-policy.json").is_file()
        && path.join("upstream").join("claude-for-legal").is_dir()
}

fn find_repo_root(start: &Path) -> Option<PathBuf> {
    start.ancestors().find(|dir| is_repo_root(dir)).map(Path::to_path_buf)
}

fn resolve_repo_root(explicit: Option<PathBuf>) -> Result<PathBuf, String> {
    if let Some(path) = explicit {
        let path = if path.is_absolute() {
            path
        } else {
            env::current_dir().map_err(|e| e.to_string())?.join(path)
        };
        return is_repo_root(&path)
            .then_some(path.clone())
            .ok_or_else(|| format!("ERROR: --repo-root is not a chunk-engine repository root: {}", path.display()));
    }
    let cwd = env::current_dir().map_err(|e| e.to_string())?;
    if let Some(found) = find_repo_root(&cwd) {
        return Ok(found);
    }
    if let Ok(exe) = env::current_exe() {
        if let Some(parent) = exe.parent() {
            if let Some(found) = find_repo_root(parent) {
                return Ok(found);
            }
        }
    }
    find_repo_root(Path::new(env!("CARGO_MANIFEST_DIR"))).ok_or_else(|| {
        "ERROR: could not locate repository root (expected UPSTREAM.lock.json and registry/chunk-policy.json)".into()
    })
}

fn line_for(data: &[u8], offset: usize) -> usize {
    data[..offset].iter().filter(|byte| **byte == b'\n').count() + 1
}

fn is_utf8_boundary(data: &[u8], offset: usize) -> bool {
    offset <= data.len()
        && (offset == 0 || offset == data.len() || (data[offset] & 0xC0) != 0x80)
}

fn partition_static_file(data: &[u8], lines_per_chunk: usize) -> Result<Vec<(usize, usize)>, String> {
    std::str::from_utf8(data).map_err(|_| "input is not valid UTF-8".to_string())?;
    let mut starts = vec![0usize];
    for (index, byte) in data.iter().enumerate() {
        if *byte == b'\n' {
            starts.push(index + 1);
        }
    }
    if data.is_empty() {
        starts = vec![0];
    }
    let mut spans = Vec::new();
    let mut index = 0usize;
    while index < starts.len() {
        let start = starts[index];
        let end = if index + lines_per_chunk < starts.len() {
            starts[index + lines_per_chunk]
        } else {
            data.len()
        };
        if !is_utf8_boundary(data, start) || !is_utf8_boundary(data, end) {
            return Err(format!("UTF-8 code point would be split at [{start},{end})"));
        }
        spans.push((start, end));
        index += lines_per_chunk;
    }
    Ok(spans)
}

fn sort_keys(value: Value) -> Value {
    match value {
        Value::Object(map) => {
            let mut keys: Vec<String> = map.keys().cloned().collect();
            keys.sort();
            let mut out = Map::new();
            for key in keys {
                out.insert(key.clone(), sort_keys(map.get(&key).expect("known key").clone()));
            }
            Value::Object(out)
        }
        Value::Array(items) => Value::Array(items.into_iter().map(sort_keys).collect()),
        other => other,
    }
}

fn canon(value: &Value) -> Result<Vec<u8>, String> {
    let body = serde_json::to_string_pretty(&sort_keys(value.clone())).map_err(|e| e.to_string())?;
    Ok(format!("{body}\n").into_bytes())
}

fn compact_canon(value: &Value) -> Result<Vec<u8>, String> {
    serde_json::to_vec(&sort_keys(value.clone())).map_err(|e| e.to_string())
}

fn digest_id(prefix: &str, material: &Value) -> Result<String, String> {
    Ok(format!("{prefix}{}", hash(&compact_canon(material)?)))
}

fn chunk_id(identity: &Value) -> Result<String, String> {
    digest_id(CHUNK_PREFIX, identity)
}

fn stable_parent_id(material: &Value) -> Result<String, String> {
    digest_id(PARENT_PREFIX, material)
}

fn stable_edge_id(edge_type: &str, source: &str, target: &str) -> Result<String, String> {
    digest_id(
        EDGE_PREFIX,
        &json!({
            "edge_type": edge_type,
            "policy_revision": FORMAT_VERSION,
            "source_chunk_id": source,
            "target_chunk_id": target,
        }),
    )
}

fn inverse_type(edge_type: &str) -> Result<&'static str, String> {
    match edge_type {
        "NEXT_IN_PARENT" => Ok("PREVIOUS_IN_PARENT"),
        "PREVIOUS_IN_PARENT" => Ok("NEXT_IN_PARENT"),
        "MODIFIES_PATH" => Ok("MODIFIED_BY"),
        "MODIFIED_BY" => Ok("MODIFIES_PATH"),
        "DERIVED_FROM" => Ok("HAS_DERIVATIVE"),
        "HAS_DERIVATIVE" => Ok("DERIVED_FROM"),
        other => Err(format!("unknown edge type: {other}")),
    }
}

fn make_edge(edge_type: &str, source: &str, target: &str) -> Result<Value, String> {
    let inverse = inverse_type(edge_type)?;
    Ok(json!({
        "authority_class": "candidate_evidence",
        "creation_method": "deterministic_partition",
        "edge_id": stable_edge_id(edge_type, source, target)?,
        "edge_type": edge_type,
        "inverse_edge_id": stable_edge_id(inverse, target, source)?,
        "limitation": "A deterministic adjacency edge preserves source order; it does not establish semantic or causal relation.",
        "policy_revision": FORMAT_VERSION,
        "review_status": "candidate",
        "source_chunk_id": source,
        "target_chunk_id": target,
    }))
}

fn git_command(repo: &Path, args: &[&str], input: Option<&[u8]>) -> Result<Vec<u8>, String> {
    let mut command = Command::new("git");
    command.arg("-C").arg(repo).args(args).stdout(Stdio::piped()).stderr(Stdio::piped());
    if input.is_some() {
        command.stdin(Stdio::piped());
    }
    let mut child = command.spawn().map_err(|e| format!("failed to start git: {e}"))?;
    if let Some(bytes) = input {
        child
            .stdin
            .as_mut()
            .ok_or_else(|| "git stdin unavailable".to_string())?
            .write_all(bytes)
            .map_err(|e| format!("failed to write git stdin: {e}"))?;
    }
    let output = child.wait_with_output().map_err(|e| format!("failed to wait for git: {e}"))?;
    if !output.status.success() {
        return Err(format!(
            "git {} failed: {}",
            args.join(" "),
            String::from_utf8_lossy(&output.stderr).trim()
        ));
    }
    Ok(output.stdout)
}

fn load_tree(repo: &Path, commit: &str) -> Result<Vec<TreeBlob>, String> {
    let raw = git_command(repo, &["ls-tree", "-r", "-z", "--full-tree", commit], None)?;
    let mut metadata_rows: Vec<(String, String)> = Vec::new();
    for record in raw.split(|byte| *byte == 0).filter(|record| !record.is_empty()) {
        let tab = record.iter().position(|byte| *byte == b'\t').ok_or("invalid git ls-tree row")?;
        let metadata = std::str::from_utf8(&record[..tab]).map_err(|_| "non-ASCII git metadata")?;
        let parts: Vec<&str> = metadata.split_whitespace().collect();
        if parts.len() != 3 {
            return Err(format!("invalid git ls-tree metadata: {metadata:?}"));
        }
        if parts[1] != "blob" {
            continue;
        }
        let path = String::from_utf8(record[tab + 1..].to_vec()).map_err(|_| "non-UTF-8 Git path")?;
        metadata_rows.push((path, parts[2].to_string()));
    }
    metadata_rows.sort_by(|left, right| left.0.as_bytes().cmp(right.0.as_bytes()));
    let mut request = Vec::new();
    for (_, object_id) in &metadata_rows {
        request.extend_from_slice(object_id.as_bytes());
        request.push(b'\n');
    }
    let batch = git_command(repo, &["cat-file", "--batch"], Some(&request))?;
    let mut position = 0usize;
    let mut blobs = Vec::new();
    for (path, expected_oid) in metadata_rows {
        let relative_end = batch[position..]
            .iter()
            .position(|byte| *byte == b'\n')
            .ok_or("truncated git cat-file header")?;
        let header_end = position + relative_end;
        let header = std::str::from_utf8(&batch[position..header_end]).map_err(|_| "non-ASCII cat-file header")?;
        position = header_end + 1;
        let parts: Vec<&str> = header.split_whitespace().collect();
        if parts.len() != 3 || parts[0] != expected_oid || parts[1] != "blob" {
            return Err(format!("unexpected git cat-file header: {header:?}"));
        }
        let size: usize = parts[2].parse().map_err(|_| "invalid git blob size")?;
        if position + size >= batch.len() || batch[position + size] != b'\n' {
            return Err("truncated git cat-file blob".into());
        }
        let data = batch[position..position + size].to_vec();
        position += size + 1;
        if std::str::from_utf8(&data).is_ok() {
            blobs.push(TreeBlob { path, object_id: expected_oid, data });
        }
    }
    if position != batch.len() {
        return Err("git cat-file returned trailing bytes".into());
    }
    Ok(blobs)
}

fn activated_kinds(policy: &Value) -> Result<Vec<String>, String> {
    let kinds = policy
        .get("activated_chunk_kinds")
        .and_then(Value::as_array)
        .ok_or("ERROR: malformed chunk policy: activated_chunk_kinds must be an array")?;
    let mut out = Vec::new();
    for value in kinds {
        out.push(
            value
                .as_str()
                .ok_or("ERROR: malformed chunk policy: activated kinds must be strings")?
                .to_string(),
        );
    }
    if !out.iter().any(|kind| kind == "static_file_span") {
        return Err("ERROR: malformed chunk policy: static_file_span must be activated".into());
    }
    for gated in ["pr_file_record", "web_capture_span"] {
        if out.iter().any(|kind| kind == gated) {
            return Err(format!("ERROR: {gated} is designed but not implemented"));
        }
    }
    Ok(out)
}

fn reject_forbidden_public_bytes(bytes: &[u8]) -> Result<(), String> {
    let lowered = String::from_utf8_lossy(bytes).to_lowercase();
    for needle in FORBIDDEN_PUBLIC_SUBSTRINGS {
        if lowered.contains(&needle.to_lowercase()) {
            return Err(format!("ERROR: public chunk registry must not contain {needle:?}"));
        }
    }
    Ok(())
}

fn build_registry(root: &Path) -> Result<(Value, Vec<u8>), String> {
    let upstream = root.join("upstream").join("claude-for-legal");
    let policy_path = root.join("registry").join("chunk-policy.json");
    let lock_path = root.join("UPSTREAM.lock.json");
    let source_registry_path = root.join("registry").join("source-registry.json");
    let policy_bytes = fs::read(&policy_path).map_err(|e| format!("ERROR: cannot read policy: {e}"))?;
    let policy: Value = serde_json::from_slice(&policy_bytes).map_err(|e| format!("ERROR: malformed policy: {e}"))?;
    if policy.get("schema") != Some(&json!("claude-legal-audit.chunk-policy.v2"))
        || policy.get("format_version") != Some(&json!(FORMAT_VERSION))
        || policy.get("output") != Some(&json!("registry/chunk-registry.json"))
    {
        return Err("ERROR: unsupported chunk policy contract".into());
    }
    let active = activated_kinds(&policy)?;
    let lines_per_chunk = policy["static_inputs"]["lines_per_chunk"]
        .as_u64()
        .ok_or("ERROR: invalid lines_per_chunk")? as usize;
    let source_id = policy["static_inputs"]["source_id"]
        .as_str()
        .ok_or("ERROR: invalid static source ID")?;
    let source_registry: Value = serde_json::from_slice(
        &fs::read(source_registry_path).map_err(|e| format!("ERROR: cannot read source registry: {e}"))?,
    )
    .map_err(|e| format!("ERROR: malformed source registry: {e}"))?;
    let source_known = source_registry["sources"]
        .as_array()
        .map(|sources| sources.iter().any(|source| source["source_id"] == source_id))
        .unwrap_or(false);
    if !source_known {
        return Err(format!("ERROR: unknown static source ID {source_id}"));
    }
    let lock: Value = serde_json::from_slice(
        &fs::read(lock_path).map_err(|e| format!("ERROR: cannot read UPSTREAM.lock.json: {e}"))?,
    )
    .map_err(|e| format!("ERROR: malformed UPSTREAM.lock.json: {e}"))?;
    let commit = lock["commit"].as_str().ok_or("ERROR: missing pinned commit")?;
    if commit.len() != 40 || !commit.bytes().all(|byte| byte.is_ascii_hexdigit() && !byte.is_ascii_uppercase()) {
        return Err("ERROR: pinned commit must be lowercase 40-hex".into());
    }

    let mut chunks = Vec::new();
    let mut file_ids: Vec<Vec<String>> = Vec::new();
    for blob in load_tree(&upstream, commit)? {
        let parent_hash = hash(&blob.data);
        let parent_material = json!({
            "content_sha256": parent_hash,
            "git_blob_oid": blob.object_id,
            "kind": "git_blob",
            "path": blob.path,
            "repository": REPOSITORY_ID,
            "source_id": source_id,
            "source_revision": commit,
        });
        let parent_id = stable_parent_id(&parent_material)?;
        let parent_record = json!({
            "byte_count": blob.data.len(),
            "commit": commit,
            "git_blob_oid": blob.object_id,
            "parent_id": parent_id,
            "path": blob.path,
            "repository": REPOSITORY_ID,
            "sha256": parent_hash,
        });
        let mut ids = Vec::new();
        for (start, end) in partition_static_file(&blob.data, lines_per_chunk)? {
            let content_hash = hash(&blob.data[start..end]);
            let locator = json!({
                "byte_end_exclusive": end,
                "byte_start": start,
                "kind": "git_blob_span",
                "line_end": line_for(&blob.data, start.max(end.saturating_sub(1))),
                "line_start": line_for(&blob.data, start),
            });
            let identity = json!({
                "chunk_kind": "static_file_span",
                "content_sha256": content_hash,
                "locator": locator,
                "parent_id": parent_id,
                "policy_revision": FORMAT_VERSION,
                "source_id": source_id,
                "source_revision": commit,
            });
            let id = chunk_id(&identity)?;
            chunks.push(json!({
                "authority_class": "candidate_evidence",
                "chunk_id": id,
                "chunk_kind": "static_file_span",
                "content_sha256": content_hash,
                "exact_locator": locator,
                "identity": identity,
                "limitation": "A byte-exact pinned Git-blob span is candidate evidence, not runtime behavior, intent, or source truth.",
                "parent": parent_record,
                "review_status": "candidate",
                "source_ids": [source_id],
            }));
            ids.push(id);
        }
        file_ids.push(ids);
    }

    let mut edges = Vec::new();
    for ids in file_ids {
        for pair in ids.windows(2) {
            edges.push(make_edge("NEXT_IN_PARENT", &pair[0], &pair[1])?);
            edges.push(make_edge("PREVIOUS_IN_PARENT", &pair[1], &pair[0])?);
        }
    }
    edges.sort_by(|left, right| {
        let left_key = (
            left["source_chunk_id"].as_str().unwrap_or(""),
            left["edge_type"].as_str().unwrap_or(""),
            left["target_chunk_id"].as_str().unwrap_or(""),
        );
        let right_key = (
            right["source_chunk_id"].as_str().unwrap_or(""),
            right["edge_type"].as_str().unwrap_or(""),
            right["target_chunk_id"].as_str().unwrap_or(""),
        );
        left_key.cmp(&right_key)
    });
    let value = json!({
        "build": {
            "activated_chunk_kinds": active,
            "canonical_json": "sorted_keys_pretty_utf8_lf",
            "generator": "scripts/build_chunk_registry.py",
            "generator_version": GENERATOR_VERSION,
        },
        "chunks": chunks,
        "edges": edges,
        "format_version": FORMAT_VERSION,
        "limitation": "Generated candidate evidence only; no private raw bytes, semantic inference, or claim promotion.",
        "pinned_commit": commit,
        "pinned_repository": REPOSITORY_ID,
        "policy_sha256": hash(&policy_bytes),
        "schema": "claude-legal-audit.chunk-registry.v2",
        "source_ids": [source_id],
    });
    let bytes = canon(&value)?;
    reject_forbidden_public_bytes(&bytes)?;
    Ok((value, bytes))
}

fn print_usage() {
    eprintln!(
        "usage: claude-legal-chunk-engine [--repo-root PATH] [--output PATH] [--check]\n\
         Defaults: repo root via cwd/ancestor search; output registry/chunk-registry.json"
    );
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut repo_root: Option<PathBuf> = None;
    let mut output: Option<PathBuf> = None;
    let mut check = false;
    let mut args = env::args().skip(1);
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--check" => check = true,
            "--repo-root" => repo_root = Some(PathBuf::from(args.next().ok_or("ERROR: --repo-root requires a path")?)),
            "--output" => output = Some(PathBuf::from(args.next().ok_or("ERROR: --output requires a path")?)),
            "--help" | "-h" => {
                print_usage();
                return Ok(());
            }
            other => {
                print_usage();
                return Err(format!("ERROR: unknown argument: {other}").into());
            }
        }
    }
    if check && output.is_some() {
        return Err("ERROR: --check compares the authoritative registry; do not pass --output".into());
    }
    let root = resolve_repo_root(repo_root)?;
    let out_path = output.unwrap_or_else(|| root.join("registry").join("chunk-registry.json"));
    let (value, bytes) = build_registry(&root)?;
    if check {
        let existing = fs::read(root.join("registry").join("chunk-registry.json"))?;
        if existing != bytes {
            return Err("ERROR: Rust projection differs from authoritative Python registry".into());
        }
        println!(
            "Rust chunk engine parity: {} chunks, {} edges",
            value["chunks"].as_array().map(Vec::len).unwrap_or(0),
            value["edges"].as_array().map(Vec::len).unwrap_or(0)
        );
        return Ok(());
    }
    if let Some(parent) = out_path.parent() {
        fs::create_dir_all(parent)?;
    }
    fs::write(&out_path, &bytes)?;
    println!(
        "wrote {}: {} chunks, {} edges",
        out_path.display(),
        value["chunks"].as_array().map(Vec::len).unwrap_or(0),
        value["edges"].as_array().map(Vec::len).unwrap_or(0)
    );
    Ok(())
}
