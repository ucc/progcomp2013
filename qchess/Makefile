# Makefile that builds qchess for UCC::Progcomp2013

SCRIPT=qchess.py
DLL_PATH=win32_dll

python_native : 
	make -C src
	mv src/$(SCRIPT) ./


all : python_native frozen

frozen : win32_frozen linux64_frozen
	cd build; for d in $$(ls); do if [ -d $$d ]; then zip -r $$d.zip $$d; rm -r $$d; fi; done


images :
	cd tools; python image_builder.py 

win32_frozen : $(SCRIPT) images
	sed -i 's:create_images(grid_sz):load_images():g' $(SCRIPT)
	wine "C:\\Python27\\python.exe" build.py build
	for d in $$(ls $(DLL_PATH)); do cp $(DLL_PATH)/$$d build/exe.win32-2.7/; done
	for b in $$(ls build); do if [ -d build/$$b ]; then cp -r data build/$$b; fi; done
	sed -i 's:load_images():create_images(grid_sz):g' $(SCRIPT)

linux64_frozen : $(SCRIPT) images
	sed -i 's:create_images(grid_sz):load_images():g' $(SCRIPT)
	python build.py build
	for b in $$(ls build); do if [ -d build/$$b ]; then cp -r data build/$$b; fi; done
	sed -i 's:load_images():create_images(grid_sz):g' $(SCRIPT)	
	
	

clean :
	make -C src clean
	rm -f $(SCRIPT)
	rm -f *~
	rm -rf build
	rm -rf data/images
	rm -f tools/*~
	rm -f tools/*.pyc
