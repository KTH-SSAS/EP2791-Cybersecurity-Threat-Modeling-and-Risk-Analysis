# Unit tests

**WARNING: Risk of flashing lights as GUI windows are rapidly created and destroyed**

Run the tests by running:

```
python3 test.py
```

The unit tests validate basic functionality of the tool, where it would be preferred to add more tests in the future to encompass a larger portion of the program's functionality.

The distribution and attack-plan aggregation tests are headless and can be run separately from the tool directory:

```
python3 -m unittest testing/test_distribution_calculations.py -v
```
