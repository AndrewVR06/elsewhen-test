# elsewhen-test

This is my solution to the Elsewhen technical test

## Running the code
To run the code please install the requirements with 
```commandline
pip install -r requirements.txt
```

The main script can be run with 
```commandline
python main.py --file=slcsp.csv
```

This will print out valid zipcodes and the SLCSP values to stdout. However, if you'd like to also see zipcodes that failed
you can run the script with
```commandline
python main.py --file=slcsp.csv --show_stderr=True
```

## Testing

To run the full suite of unit tests please issue the following:
```commandline
pytest --cov-report term --cov persistence_layer/ --cov main tests/
```

This will also provide a full coverage report. The only branch not missing has to do
with the actual running of the main file. Usually click handles this for us, so we cannot
test it in our test suite. So besides this, our code has full coverage. 

## Requirements
I have used the following additional libraries

- click
- pytest-cov
- pydantic

Click was used to provide a easy and simple to use CLI.

pytest-cov is used to run the full test suite and provide coverage statistics.

pydantic is used to validate and parse rows of csv data which helps in ensuring 
variable types elsewhere in the code.

## Persistence Layer

I have built this technical test around a persistence layer. This layer is meant to
mimic a database in order to try get as close to a production system as possible. The 
idea is that the persistence layer provides a way to save data as well as access it later in a 
uniform and predictable manner.

In this test for example, to work out SLCSP we use the persistance layer to find all
rates for a metal type. Once we have that, only then do we impose SLCSP logic onto it.
The hope is that we're able to extend this technical test and add additional functionality much
more easily later on. 


