install: ;

clean:
	rm *.pyc

run-local:
	python3 sensor.py nopi

kill:
	kill $(pidof python)

test:
	python3 test-script.py
