SRCS = $(wildcard neon/src/*.html)

all: build

build: $(SRCS) neon/src/styles.css neon/src/*.js
	python3 utils/preprocess.py
	cp neon/src/*.js neon/dist/

clean:
	rm neon/dist/*

serve:
	python3 -m http.server 8080 --directory neon/dist

.PHONY: clean all build serve

