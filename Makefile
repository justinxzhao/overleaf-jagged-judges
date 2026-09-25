# Build targets for the paper.
# Shared content lives in sections/*.tex and references.bib.

.PHONY: all iclr meta clean

all: iclr

# ICLR 2027 submission build (anonymous unless \iclrfinalcopy is enabled).
iclr:
	latexmk -pdf -interaction=nonstopmode iclr_2027.tex

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
	latexmk -C iclr_2027.tex meta_2026.tex
	rm -f *.bbl *.blg *.brf *.bcf *.run.xml
