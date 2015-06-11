prefix=/usr/local
program_name=insteadman

install:
	cp -R . $(prefix)/share/$(program_name)/
	ln -s "$(prefix)/share/$(program_name)/instead-manager.py" $(prefix)/bin/$(program_name)
	ln -s "$(prefix)/share/$(program_name)/instead-manager-tk.pyw" $(prefix)/bin/$(program_name)-tk
	ln -s "$(prefix)/share/$(program_name)/instead-manager-tk.pyw" $(prefix)/bin/$(program_name)-gui
	@echo "Completed. Use $(program_name), $(program_name)-gui commands."

uninstall:
	rm -Rf $(prefix)/share/$(program_name)/
	rm $(prefix)/bin/$(program_name)
	rm $(prefix)/bin/$(program_name)-tk
	rm $(prefix)/bin/$(program_name)-gui
	@echo "Completed"

.PHONY: install, uninstall
