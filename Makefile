run:
	#export FLASK_APP=sensor.py
	#flask run
	python3 -m sensor

clean:
	rm *.pyc

stop:
	kill $(pidof python3)

test:
	python3 test-script.py
