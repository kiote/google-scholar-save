build:
	@python3 pdf/mass_reader.py

analyze:
	@python3 pdf/rag.py

clean:
	@rm -rf docs/papers/*.txt
	@rm -rf docs/*.pdf

.PHONY: build analyze clean
