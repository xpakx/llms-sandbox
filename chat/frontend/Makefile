SRCS = $(wildcard neon/src/*.html)

all: build

build: $(SRCS)
	python3 utils/preprocess.py

clean:
	rm neon/dist/*

serve:
	python3 -m http.server 8080 --directory neon/dist

.PHONY: clean all build serve

