BUILD_DIR=build

prefix = /usr/local

all: $(BUILD_DIR)/hdstress

$(BUILD_DIR)/hdstress: 
	-mkdir $(BUILD_DIR) | true
	python3 -m zipapp -o $(BUILD_DIR)/hdstress hdstress -p "/usr/bin/env python3"
	chmod +x $@

install: $(BUILD_DIR)/hdstress
	install $(BUILD_DIR)/hdstress $(DESTDIR)$(prefix)/bin/hdstress
	install -m 644 doc/man/hdstress.1 $(DESTDIR)$(prefix)/man/man1
	
uninstall:
	-rm -f $(DESTDIR)$(prefix)/bin/hdstress
	-rm -f $(DESTDIR)$(prefix)/man/man1/hdstress.1


clean:
	-rm -f $(BUILD_DIR)/*

distclean: clean

debian: $(BUILD_DIR)/hdstress
	dpkg-buildpackage -b

.PHONY: clean debian
