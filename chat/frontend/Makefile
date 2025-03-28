SRCS = $(wildcard neon/src/*.html)

all: build

build: $(SRCS) neon/src/styles.css neon/src/script.js
	python3 utils/preprocess.py
	cp neon/src/styles.css neon/dist/styles.css
	cp neon/src/script.js neon/dist/script.js

clean:
	rm neon/dist/*

serve:
	python3 -m http.server 8080 --directory neon/dist

.PHONY: clean all build serve

