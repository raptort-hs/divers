# Convenience commands for Symbiose MVP.

.PHONY: install demo demo-run test serve validate-skills clean

install:
	cd backend && pip install -e '.[dev]'

demo:
	cd backend && symbiose demo

demo-run:
	cd backend && symbiose demo --execute

test:
	cd backend && python -m pytest tests/ -v

serve:
	cd backend && symbiose serve

validate-skills:
	cd backend && symbiose skills validate

clean:
	find . -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/.workspace
