GBDK ?= /opt/gbdk
PYTHON ?= python3
LCC := $(GBDK)/bin/lcc
SOURCES := src/main.c src/game.c src/ui.c src/save.c src/levels.c $(wildcard src/campaign_*.c) src/music.c src/art_data.c src/title_art.c $(wildcard src/world_*.c)
HEADERS := $(wildcard src/*.h)
.PHONY: all assets check clean
all: dist/moonwake.gbc
assets:
	"$(PYTHON)" tools/build_art.py

dist/moonwake.gbc: $(SOURCES) $(HEADERS)
	mkdir -p build dist
	"$(LCC)" -I./src -Wl-m -Wl-j -Wm-yC -Wm-yt0x1B -Wm-ya1 -Wm-yo32 -Wm-ynMOONWAKE -Wm-yS -o build/moonwake.gb $(SOURCES)
	cp build/moonwake.gb $@
	cp build/moonwake.sym dist/moonwake.sym
	"$(PYTHON)" tools/check_rom.py $@
check: all
	"$(PYTHON)" tools/build_campaign.py --check
	"$(PYTHON)" tools/check_campaign.py
	"$(PYTHON)" tools/playtest.py
clean:
	rm -f build/moonwake.* dist/moonwake.gbc dist/moonwake.sym
