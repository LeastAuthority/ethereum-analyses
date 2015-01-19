MD_SOURCES = README.md GasEcon.md PoW.md Appendix.md
#RST_SOURCES = ethereum_incentive_analysis.rst

HTML_OUTPUTS = $(HTML_FROM_MD_OUTPUTS) $(HTML_FROM_RST_OUTPUTS)
HTML_FROM_MD_OUTPUTS = $(subst .md,.html,$(MD_SOURCES))
HTML_FROM_RST_OUTPUTS = $(subst .rst,.html,$(RST_SOURCES))

PDF_OUTPUTS = $(PDF_FROM_MD_OUTPUTS) $(PDF_FROM_RST_OUTPUTS)
PDF_FROM_MD_OUTPUTS = $(subst .md,.pdf,$(MD_SOURCES))
PDF_FROM_RST_OUTPUTS = $(subst .rst,.pdf,$(RST_SOURCES))

VERSIONED_MDS = $(subst .md,.versioned.md,$(MD_SOURCES))
VERSIONED_RSTS = $(subst .rst,.versioned.rst,$(RST_SOURCES))

all: $(HTML_OUTPUTS) $(PDF_OUTPUTS)

clean:
	rm -f $(HTML_OUTPUTS) $(PDF_OUTPUTS) $(VERSIONED_MDS) $(VERSIONED_RSTS)

VERSION = $(shell git describe --long --always --abbrev=40 --dirty)

# "static pattern rule" is probably a GNU-Make extension. It is slightly
# safer to constrain it by an explicit list of targets.
$(VERSIONED_MDS) : %.versioned.md: %.md
	@echo "creating $@ by inserting git revision hash"
	@cat $< | sed 's@This file generated from https://github.com/LeastAuthority/ethereum-analyses .@This file generated from https://github.com/LeastAuthority/ethereum-analyses , revision $(VERSION).@' > $@

$(VERSIONED_RSTS) : %.versioned.rst: %.rst
	@echo "creating $@ by inserting git revision hash"
	@cat $< | sed 's@This file generated from https://github.com/LeastAuthority/ethereum-analyses .@This file generated from https://github.com/LeastAuthority/ethereum-analyses , revision $(VERSION).@' > $@

$(HTML_FROM_MD_OUTPUTS) : %.html: %.versioned.md
	@echo 'Generating: $@'
	@pandoc $< -o $@

$(PDF_FROM_MD_OUTPUTS) : %.pdf: %.versioned.md
	@echo 'Generating: $@'
	@pandoc $< -o $@

$(HTML_FROM_RST_OUTPUTS) : %.html: %.versioned.rst
	@echo 'Generating: $@'
	@rst2html --strict $< $@

$(PDF_FROM_RST_OUTPUTS) : %.pdf: %.versioned.rst
	@echo 'Generating: $@'
	@rst2pdf $< $@

# Bug: This isn't included by the 'all' target.
# Bug: We may need a path invariant way of generating this.
# Bug: This should exclude the blogpost, right?
LA-Ethereum-Report.pdf: $(PDF_OUTPUTS)
	python /usr/share/doc/python-pypdf2/examples/pdfcat -o $@ $^

.PHONY: all clean
