.PHONY: bootstrap inventory scan worklists audit test verify clean bundle

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

verify:
	bash scripts/verify_upstream.sh
	python3 scripts/validate_jsonl.py results/pattern-matches.jsonl --kind pattern-match

test:
	python3 -m unittest discover -s tests -v

clean:
	rm -rf results/*
	touch results/.gitkeep

bundle:
	git bundle create ../claude-legal-audit-lab.bundle --all
