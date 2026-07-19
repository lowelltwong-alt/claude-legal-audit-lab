.PHONY: bootstrap inventory scan worklists audit lineage validate-navigation validate-radar validate-arguments validate-roadmap validate-release validate-claims chunks pr-linkage graph thesis paper mini-papers candidate test verify clean bundle

bootstrap:
	bash scripts/bootstrap_upstream.sh

inventory:
	python3 scripts/inventory.py upstream/claude-for-legal --out results

scan:
	python3 scripts/pattern_scan.py upstream/claude-for-legal --patterns patterns/seed-patterns.json --out results/pattern-matches.jsonl

worklists:
	python3 scripts/build_worklists.py results/inventory.json --workers 6 --out results/worklists

audit: inventory scan worklists
	@echo "Static audit artifacts written under results/."

lineage:
	python3 scripts/build_lineage.py

validate-navigation:
	python3 scripts/build_lineage.py --check
	python3 scripts/validate_navigation.py

validate-radar:
	python3 scripts/validate_research_radar.py

validate-arguments:
	python3 scripts/validate_argument_mesh.py

validate-roadmap:
	python3 scripts/validate_roadmap.py

validate-release:
	python3 scripts/validate_release_readiness.py

validate-claims:
	python3 scripts/upgrade_claim_registry_v2.py --check

chunks:
	python3 scripts/build_chunk_registry.py --check --verify-reconstruction

pr-linkage:
	python3 scripts/build_pr_linkage.py --check

graph:
	python3 scripts/build_evidence_graph.py --check

thesis:
	python3 scripts/build_thesis_map.py --check

paper:
	python3 scripts/build_white_paper_candidate.py --check

mini-papers:
	python3 scripts/build_mini_papers.py --check

candidate: validate-claims chunks pr-linkage graph thesis paper mini-papers lineage
	@echo "Blocked unpublished candidate is deterministic; this target does not authorize release."

verify:
	bash scripts/verify_upstream.sh
	python3 scripts/validate_jsonl.py results/pattern-matches.jsonl --kind pattern-match

test:
	python3 scripts/upgrade_claim_registry_v2.py --check
	python3 scripts/build_chunk_registry.py --check --verify-reconstruction
	python3 scripts/build_pr_linkage.py --check
	python3 scripts/build_evidence_graph.py --check
	python3 scripts/build_thesis_map.py --check
	python3 scripts/build_white_paper_candidate.py --check
	python3 scripts/build_mini_papers.py --check
	python3 scripts/build_lineage.py --check
	python3 scripts/validate_research_radar.py
	python3 scripts/validate_argument_mesh.py
	python3 scripts/validate_roadmap.py
	python3 scripts/validate_release_readiness.py
	python3 scripts/validate_navigation.py
	python3 -m unittest discover -s tests -v

clean:
	rm -rf results/*
	touch results/.gitkeep

bundle:
	git bundle create ../claude-legal-audit-lab.bundle --all
