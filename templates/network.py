# !/usr/bin/env python

from troposphere import Output, Parameter, Ref, Template, Join
from troposphere import GetAZs, Select, Join, GetAtt
from troposphere.ec2 import Tag, VPC, InternetGateway, VPCGatewayAttachment
from troposphere.ec2 import Subnet, RouteTable, Route
from troposphere.ec2 import SubnetRouteTableAssociation


class Vpc(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.template.add_description("VPN Server")
        self.sceptre_user_data = sceptre_user_data

        self.default_tags = [
            Tag('Owner', self.sceptre_user_data['owner_name']),
            Tag('Contact', self.sceptre_user_data['owner_email'])
        ]

        self.subnet_ids = {}
        self.route_table_ids = {}

        self.add_vpc()
        self.add_igw()
        self.add_subnets()
        self.add_route_table_ids()
        self.add_routes()
        self.associate_route_table_ids()

        self.add_outputs()

    def add_vpc(self):
        t = self.template

        self.vpc = t.add_resource(VPC(
            'vpc',
            CidrBlock=self.sceptre_user_data['vpc_cidr'],
            EnableDnsSupport='true',
            EnableDnsHostnames='true',
            Tags=self.default_tags + [Tag('Name', self.sceptre_user_data['application']+'-VPC')]
        ))
        return 0

    def add_igw(self):
        t = self.template

        self.igw = t.add_resource(InternetGateway(
            'internet-gateway',
            Tags=self.default_tags + [Tag('Name', self.sceptre_user_data['application']+'-IGW')]
        ))

        self.igw_attachment = t.add_resource(VPCGatewayAttachment(
            'internet-gateway-attachment',
            VpcId=Ref(self.vpc),
            InternetGatewayId=Ref(self.igw)
        ))
        return 0

    def add_subnets(self):
        t = self.template

        for subnet_dict in self.sceptre_user_data['subnets']:
            for i in range(0, self.sceptre_user_data['num_az']):
                az = Select(i, GetAZs())
                az_num = str(i+1)
                subnet_name = self.sceptre_user_data['application']+'-'+subnet_dict['tier']+'-az'+az_num
                cidr = subnet_dict['az'+az_num]+subnet_dict['suffix']
                subnet = self.build_subnet(t, subnet_name, az, cidr)
                subnet_ids[subnet_dict['tier']+'-az'+az_num] = Ref(subnet)
        return 0

    def build_subnet(self, t, name, az, cidr):
        subnet = t.add_resource(Subnet(
            name,
            VpcId=Ref(self.vpc),
            AvailabilityZone=az,
            CidrBlock=cidr,
            Tags=self.default_tags + [Tag('Name', name]
        ))
        return subnet

    def add_route_tables(self):
        t = self.template

        for subnet_dict in self.sceptre_user_data['subnets']:
            table_name = self.sceptre_user_data['application']+'-'+subnet_dict['tier']+'-route-table'
            route_table = t.add_resource(RouteTable(
                table_name,
                VpcId=Ref(self.vpc),
                Tags=self.default_tags + [Tag('Name', table_name]
            )
            self.route_table_ids[subnet_dict['tier']]=Ref(route_table)
        return 0

    def add_routes(self):
        t=self.template
        for subnet_dict in self.sceptre_user_data['subnets']:
            # Add route to Internet Gateway
            if subnet_dict['use_igw']:
                igw_route=t.add_resource(Route(
                    '{}-rt-igw-route'.format(subnet_dict['tier']),
                    RouteTableId=Ref(self.route_table_ids[subnet_dict['tier']]),
                    DestinationCidrBlock='0.0.0.0/0',
                    GatewayId=Ref(self.igw)
                ))
        return 0

    def associate_route_table_ids(self):
        t=self.template

        for subnet_dict in self.sceptre_user_data['subnets']:
            for i in range(0, self.sceptre_user_data['num_az']):
                az_num=str(i+1)
                subnet_id=subnet_dict[subnet_dict['tier']+'-az'+az_num]
                route_table_id=self.route_table_ids[subnet_dict['tier']])
                self.route_subnet_association(t, subnet_dict['tier'], subnet_id, route_table_id)
        return 0

    def route_table_subnet_association(self, t, tier, subnet_id, route_table_id):
        association=t.add_resource(SubnetRouteTableAssociation(
            tier+'-route-table-association',
            SubnetId=subnet_id,
            RouteTableId=route_table_id
        ))
        return 0

    def add_outputs(self):
        t=self.template

        self.vpc_output=t.add_output(Output(
            'VPC',
            Value=Ref(self.vpc),
            Description='VPC ID'
        ))

        # Adds subnet IDs to output
        for subnet_dict in self.sceptre_user_data['subnets']:
            for i in range(0, self.sceptre_user_data['num_az']):
                az_num=str(i+1)
                output_name = subnet_dict['tier']+'-az'+az_num+'-subnet-id'
                output=t.add_output(Output(
                    output_name,
                    Value=self.subnet_ids[subnet_dict['tier']+'-az'+az_num],
                    Description=output_name
                ))

        # Adds route table IDs to output
        for route_table in self.routeTables:
            output=t.add_output(Output(
                routeTable.replace('-', ''),
                Value=self.routeTables[routeTable],
                Description='{} Route table ID'.format(routeTable)
            ))


def sceptre_handler(sceptre_user_data):
    vpc=Vpc(sceptre_user_data)
    return vpc.template.to_json()

if __name__ == '__main__':
    # for debugging
    import sys
    print('python version: ', sys.version, '\n')
    vpc=Vpc()
    print(vpc.template.to_json())
