#!/usr/bin/env python

import pandas as pd
from sodapy import Socrata


# client = Socrata('data.ny.gov','APP-TOKEN',
#                 username='EMAIL-USERNAME',
#                 password='PASSWORD')
# client = Socrata("sandbox.demo.socrata.com", "FakeAppToken", 
# username="fakeuser@somedomain.com", password="mypassword")

# results = client.get('xe9x-a24f', limit=2000)

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:

# client = Socrata('data.ny.gov','APP-TOKEN',
#                 username='EMAIL-USERNAME',
#                 password='PASSWORD')



# https://openpaymentsdata.cms.gov/resource/axsx-c8us.json

client = Socrata("openpaymentsdata.cms.gov", None)

# results = client.get("xrap-xhey", select="distinct teaching_hospital_ccn",)
results = client.get("axsx-c8us", select='applicable_manufacturer_or_applicable_gpo_making_payment_id')[-1]
print(results)
exit()
hospital_list=[]
for result in results:  
    if 'teaching_hospital_ccn' in result:
        id= result['teaching_hospital_ccn']
        payments = client.get("xrap-xhey", teaching_hospital_ccn=id, select='sum(total_amount_of_payment_usdollars)')
        info=client.get("xrap-xhey", teaching_hospital_ccn=id, select='teaching_hospital_name,recipient_primary_business_street_address_line1,recipient_primary_business_street_address_line2,recipient_state,recipient_city,recipient_zip_code')
        # info = pd.DataFrame(info)
        info_dict=info[0]
        # print(info[0])
        payment= payments[0]['sum_total_amount_of_payment_usdollars']
        info_dict['payment']=payment
        # print(info_dict)
        # list.append(hospital_list)
        hospital_list.append(info_dict)
        print(info_dict['teaching_hospital_name'])

hos_df=pd.DataFrame(hospital_list)
# print(hos_df.head())
hos_df.to_csv('hospital_payments.csv')

exit()

