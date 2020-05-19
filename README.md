## CMS Payments to Teaching Hospitals 2018

### About
Interactive map plot of CMS payments to teaching hospitals in 2018 using data from the US Government Open Payments API. (openpaymentsdata.cms.gov)

### Deployed on Github Pages
Click on the link above which leads to an interactive map created in Plotly. Hospital location and total money received in display on hover.

### Frameworks
Python, Google map API, Plotly Python and Pandas. 

### File Structure
The script in app.py (root folder) runs a server with Python Flask.
Index file is Plotly generated html.
API call script in app.py.
Geocoding script in geocode.py.
Plotly mapping script in hospitals_map.py
Data at various stages in CSV file.
Screenshots in img folder.


### US Map
![](img/usa_hospitals.png)

### Bubble Plot
![](img/puerto_rico.png)
