prefix=/usr/local
program_name=insteadman

install:
	cp -R . $(prefix)/share/$(program_name)/
	ln -s "$(prefix)/share/$(program_name)/instead-manager.py" $(prefix)/bin/$(program_name)
	ln -s "$(prefix)/share/$(program_name)/instead-manager-tk.pyw" $(prefix)/bin/$(program_name)-tk
	ln -s "$(prefix)/share/$(program_name)/instead-manager-tk.pyw" $(prefix)/bin/$(program_name)-gui
	if which xdg-desktop-menu; then xdg-desktop-menu install $(prefix)/share/$(program_name)/skeleton/jhekasoft-insteadman.desktop; fi;
	@echo "Completed. Use $(program_name), $(program_name)-gui commands."

uninstall:
	rm -Rf $(prefix)/share/$(program_name)/
	rm $(prefix)/bin/$(program_name)
	rm $(prefix)/bin/$(program_name)-tk
	rm $(prefix)/bin/$(program_name)-gui
	if which xdg-desktop-menu; then xdg-desktop-menu uninstall jhekasoft-insteadman.desktop; fi;
	@echo "Completed"

.PHONY: install, uninstall
