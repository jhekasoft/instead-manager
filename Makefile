prefix=/usr/local

install:
	cp -R . $(prefix)/share/insteadman/
	ln -s "$(prefix)/share/insteadman/instead-manager.py" /usr/local/bin/insteadman
	ln -s "$(prefix)/share/insteadman/instead-manager-tk.pyw" /usr/local/bin/insteadman-tk
	ln -s "$(prefix)/share/insteadman/instead-manager-tk.pyw" /usr/local/bin/insteadman-gui

.PHONY: install
