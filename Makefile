.PHONY: build analyze clean help

build:
	@python3 pdf/mass_reader.py

analyze:
	@python3 pdf/rag.py

clean:
	@rm -rf docs/papers/*.txt
	@rm -rf docs/papers/*.md
	@rm -rf docs/*.pdf

help:
	@echo "build: Build the papers"
	@echo "analyze: Analyze the papers"
	@echo "clean: Clean the papers"
	@echo "help: Show this help message"
