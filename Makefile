clean:
	rm *.pyc

stop:
	kill $(pidof python3)

test:
	python3 test-script.py

#Run the development server. Useful for testing before deployment on Apache
run-dev:
	./venvpy3/bin/flask run
