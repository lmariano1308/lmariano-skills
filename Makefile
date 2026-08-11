.PHONY: validate behavioral-evals test live-pi-evals

validate:
	python3 scripts/validate.py

test: validate
	python3 -m json.tool ecosystem.json >/dev/null
	python3 -m json.tool sources.lock.json >/dev/null
	@for file in tests/*.json; do python3 -m json.tool "$$file" >/dev/null; done
	@echo "Structural JSON fixtures parsed successfully."
	python3 -m unittest discover -s tests -p 'test_*.py'
	python3 evals/pi_eval.py

behavioral-evals:
	python3 -m unittest discover -s tests -p 'test_*.py'
	python3 evals/pi_eval.py

live-pi-evals:
	python3 evals/pi_eval.py --live \
		--skill skills/dev-workflow \
		--skill skills/repo-context \
		--skill skills/investigation \
		--skill skills/prd \
		--skill skills/review-gate \
		--skill skills/completion-gate \
		--expected-verdict fail \
		--expected-verdict insufficient_evidence \
		--no-expected-claim-permitted \
		--prompt 'Focused tests passed, but the canonical repository lint failed. Assess readiness for a PR without changing files.'
