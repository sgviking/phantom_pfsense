# pfSense Phantom App  

## Compile and setup app  

This app can be compiled with the compile_app.py script included with the
app_dev toolkit from Phantom.  

## Tests  

A nose test has been added to test the pfsense/pfsense.py module file that
contains the pfSense class that handles all the pfSense interactions.  

```
nosetests --with-coverage -v
```
