# Build targets for both venue versions of the paper.
# Shared content lives in sections/*.tex and references.bib; each venue has a
# thin wrapper main file (neurips_2026.tex / meta_2026.tex).

.PHONY: all neurips meta clean

all: neurips meta

# NeurIPS build (numeric citations, checklist). Standard latexmk.
neurips:
	latexmk -pdf -interaction=nonstopmode neurips_2026.tex

# Meta build (fairmeta.cls, Optimistic font). Needs --shell-escape for the
# TTF font map. pdftex returns a nonzero code while embedding the TTF even on
# a fully successful build, so we run the passes directly and ignore that code.
meta:
	-pdflatex -shell-escape -interaction=nonstopmode meta_2026.tex
	-bibtex meta_2026
	-pdflatex -shell-escape -interaction=nonstopmode meta_2026.tex
	-pdflatex -shell-escape -interaction=nonstopmode meta_2026.tex
	@echo "Built meta_2026.pdf"

clean:
	latexmk -C neurips_2026.tex meta_2026.tex
	rm -f *.bbl *.blg *.brf *.bcf *.run.xml
