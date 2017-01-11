define HELPBODY
Available commands:

	make help       - this thing.
	make clean      - clear *.pyc files

	make run        - start client and websocket server
	make stop       - stop current client and server runtime

endef

export HELPBODY
help:
	@echo "$$HELPBODY"

clean:
	find . -name "*.pyc" -exec rm -rf {} \;

.PHONY: run
run:
	sh run.sh

stop:
	sh stop.sh