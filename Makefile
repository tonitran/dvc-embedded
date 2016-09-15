run:
	export FLASK_APP=sensor.py
	flask run --host=0.0.0.0

clean:
	rm *.pyc

stop:
	kill $(pidof python3)

test:
	python3 test-script.py
