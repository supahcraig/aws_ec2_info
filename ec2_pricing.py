import boto3
import json
from pkg_resources import resource_filename

regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'ca-central-1',
           'eu-central-1', 'eu-central-2' 'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-north-1', 'eu-south-1',
           'eu-south-2',
           'af-south-1',
           'ap-east-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3',
           'ap-south-1', 'ap-south-2', 'ap-southeast-1', 'ap-southeast-2', 'ap-southeast-3', 'ap-southeast-4',
           'il-central-1', 'me-south-1', 'me-central-1', 'sa-east-1',
           # 'us-gov-east-1', 'us-gov-west-1'
           ]

instance_types = ['i3en.large', 'i3en.xlarge', 'i3en.2xlarge', 'i3en.3xlarge', 'i3en.6xlarge', 'i3en.12xlarge',
                  'i3en.24xlarge', 'i3en.metal',
                  'im4gn.large', 'im4gn.xlarge', 'im4gn.2xlarge', 'im4gn.4xlarge', 'im4gn.8xlarge', 'im4gn.16xlarge',
                  'is4gen.medium', 'is4gen.large', 'is4gen.xlarge', 'is4gen.2xlarge', 'is4gen.4xlarge',
                  'is4gen.8xlarge',
                  ]

# The basis for this was found on SO:
# https://stackoverflow.com/questions/51673667/use-boto3-to-get-current-price-for-given-ec2-instance-type

# Search product filter. This will reduce the amount of data returned by the
# get_products function of the Pricing API
FLT = '[{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},' \
      '{{"Field": "operatingSystem", "Value": "{o}", "Type": "TERM_MATCH"}},' \
      '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},' \
      '{{"Field": "instanceType", "Value": "{t}", "Type": "TERM_MATCH"}},' \
      '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},' \
      '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}]'


def find_on_demand_rate(raw_pricing_dict):
    id1 = list(raw_pricing_dict)[0]
    id2 = list(raw_pricing_dict[id1]['priceDimensions'])[0]

    return float(raw_pricing_dict[id1]['priceDimensions'][id2]['pricePerUnit']['USD'])


def find_RI_rate(raw_pricing_dict, term):
    for k in raw_pricing_dict:

        if (raw_pricing_dict[k]['termAttributes']['LeaseContractLength'] == term and
                raw_pricing_dict[k]['termAttributes']['OfferingClass'] == 'standard' and
                raw_pricing_dict[k]['termAttributes']['PurchaseOption'] == 'No Upfront'):

            pd = raw_pricing_dict[k]['priceDimensions']

            for dim in pd:
                hourly_rate = float(pd[dim]['pricePerUnit']['USD'])
                return hourly_rate


# Get current AWS price for an on-demand instance
def get_price(region, instance, os):
    f = FLT.format(r=region, t=instance, o=os)
    data = client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))

    price_list = json.loads(data['PriceList'][0])

    on_demand = find_on_demand_rate(price_list['terms']['OnDemand'])
    ri_1yr = find_RI_rate(price_list['terms']['Reserved'], '1yr')
    ri_3yr = find_RI_rate(price_list['terms']['Reserved'], '3yr')

    return {'On Demand': on_demand, '1yr Reserved Instance': ri_1yr, '3yr Reserved Instance': ri_3yr}



# Translate region code to region name. Even though the API data contains
# regionCode field, it will not return accurate data. However using the location
# field will, but then we need to translate the region code into a region name.
# You could skip this by using the region names in your code directly, but most
# other APIs are using the region code.
def get_region_name(region_code):
    default_region = 'US East (N. Virginia)'
    endpoint_file = resource_filename('botocore', 'data/endpoints.json')
    try:
        with open(endpoint_file, 'r') as f:
            data = json.load(f)
        # Botocore is using Europe while Pricing API using EU...sigh...
        return data['partitions'][0]['regions'][region_code]['description'].replace('Europe', 'EU')
    except IOError:
        return default_region


# Use AWS Pricing API through Boto3
# API only has us-east-1 and ap-south-1 as valid endpoints.
# It doesn't have any impact on your selected region for your instance.
client = boto3.client('pricing', region_name='us-east-1')


for r in regions:
    for i in instance_types:
        try:
            price = (get_price(region=get_region_name(r), instance=i, os='Linux'))

            print(
                f"{r}, {i}, , ,{price['On Demand']}, {price['1yr Reserved Instance']}, {price['3yr Reserved Instance']}")
        except:
            print(r, ',', i)
