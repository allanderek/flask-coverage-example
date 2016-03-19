This is a simple example Flask application demonstrating how to combine a
Flask application with some testing including coverage analysis.
To see this in action do the following:

    $ git clone https://github.com/allanderek/flask-coverage-example.git
    $ cd flask-coverage-example
    $ . setup.fish # or source setup.sh
    $ python manage.py test

You should then be able to look in the `htmlcov` directory to see the source
marked-up with all the lines ran. Specially open the file
`htmlcov/app_main_py.html`.

To see an example of a missing line, locate the lines:

    try:
        check_fraction(50, 100, '50 of 100 is 50%')
        check_fraction(20, 30, '20 of 30 is 66%')
        check_fraction(50, 10, 'Invalid: Fraction greater than Total')
        check_fraction(0, 0, '0 of 0 is 0%')

Comment out some of them, say the bottom two, re-run `python manage.py test`
and reload `htmlcov/app_main_py.html` in your browser.
