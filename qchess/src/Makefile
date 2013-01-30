# Makefile that builds qchess.py from the component files

TARGET = qchess.py
COMPONENTS = piece.py board.py player.py agent_bishop.py timeout_player.py network.py thread_util.py log.py game.py images.py graphics.py main.py
#COMPONENTS=$(shell ls *.py | tr '\t' '\n' | grep -v $(TARGET))

$(TARGET) : $(COMPONENTS)
	echo "#!/usr/bin/python -u" > $(TARGET)
	for f in $(COMPONENTS); do echo "# +++ $$f +++ #" >> ../$(TARGET); cat $$f >> $(TARGET); echo "# --- $$f --- #" >> $(TARGET); done
	echo "# EOF - created from make on $$(date)" >> $(TARGET)
	chmod u+x $(TARGET)

clean :
	rm -f *~
	rm -f *.pyc
	rm -f $(TARGET)
