.PHONY: validate test

validate:
	python3 scripts/validate.py

test: validate
	python3 -m json.tool ecosystem.json >/dev/null
	python3 -m json.tool sources.lock.json >/dev/null
	@for file in tests/*.json; do python3 -m json.tool "$$file" >/dev/null; done
	@echo "All JSON fixtures parsed successfully."
