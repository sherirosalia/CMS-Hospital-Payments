## CMS Payments to Teaching Hospitals 2018

### About
Interactive map plot of The Centers for Medicare and Medicaid Services (CMS)  payments to teaching hospitals in 2018 using data from the US Government Open Payments API.

### Deployed on Github Pages
Click on this <a href='https://sherirosalia.github.io/cms_hospital_payments/'><strong>link </strong></a>to view the interactive projection created in Plotly. Hospital location and total money received in display on hover.

### Frameworks
Google Map API, Plotly and Python. 

### File Structure
- The app.py script contains the api call for openpaymentsdata.cms.gov.
- Index file is Plotly generated html.
- The geocoding script is in geocode.py.
- The hospitals_map.py creates the Plotly map.
- Data at various stages are in the CSV files.
- Screenshots in the img folder.


### US Map
![](img/usa_hospitals.png)

### Port Jefferson, NY
![](img/st_charles_ny.png)

### Stony Brook, NY
![](img/stony_brook_ny.png)

### Manhattan, NY
![](img/manhattan_ny.png)

### San Diego, CA
![](img/san_diego_ca.png)

### Ponce, Puerto Rico
![](img/puerto_rico.png)
