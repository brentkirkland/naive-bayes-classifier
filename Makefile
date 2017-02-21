ifndef VERBOSE
.SILENT:
endif

all:
	chmod +x start.py
	cp start.py NaiveBayesClassifier
