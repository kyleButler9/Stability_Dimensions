# Stability_Dimensions

## Initialization

After installing the Requirements.txt file via

    pip install -r Requirements.txt

Navigate to this repo's parent directory, and initialize the database schema of
the database specified in the .ini file stored in the panels/psql subdirectory
and run

    python Stability_Dimensions/panels/psql/Initialize_Database.py

## Running

To view the app directly from a Bokeh server, from the parent directory and
execute the command:

    bokeh serve --show Stability_Dimensions
