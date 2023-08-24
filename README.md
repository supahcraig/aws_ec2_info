# aws_ec2_info
Uses boto3 to call the AWS pricing API to return the on demand, 1yr, and 3yr reserved instance prices.

It's a little bit brute-forcey, but running this will return a comma separated list to stdout that can by copy/pasted into the AWS_Reference tab on my TCO google sheet (as of v3, anyway).

https://docs.google.com/spreadsheets/d/1A5dAQOt7MPQfQ6wLBRI_bDL0Q0yTGIZB3EIGYRWoONc/edit#gid=2020792389

In a perfect world we could automate the injection of this data into that sheet, but the sheet exists in my company's org, and it requires a service acct to have API access to the sheet...unfortunatetly the service acct lives outside of my company's org and is denied.

