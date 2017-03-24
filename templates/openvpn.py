# !/usr/bin/env python
# This template generates an openvpn instance following the config from the
# openvpn.yaml file.
# Template is modified for Sceptre (http://sceptre.ce-tools.cloudreach.com).

from troposphere import Output, Parameter, Ref, Template, Join
from troposphere import GetAZs, Select, Join, GetAtt
from troposphere.ec2 import Tag, VPC, InternetGateway, VPCGatewayAttachment
from troposphere.ec2 import Subnet, RouteTable, Route
from troposphere.ec2 import SubnetRouteTableAssociation


class Vpc(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.template.add_description("VPN Server")
        self.sceptreUserData = sceptre_user_data
        self.numAz = self.sceptreUserData['numAz']

        self.add_parameters()

        self.defaultTags = [
            Tag('Owner', Ref(self.ownerEmailParam))
        ]
        self.namePrefix = Join("", [
            self.sceptreUserData['environment']
        ])

        self.subnets = self.sceptreUserData['subnets']
        self.routeTables = {}

        self.add_vpc()
        self.add_igw()
        self.add_subnets()
        self.add_route_tables()
        self.add_routes()
        self.associate_route_tables()

        self.add_outputs()

    def add_parameters(self):
        t = self.template

        self.vpcCidrParam = t.add_parameter(Parameter(
            'vpcCidr',  # This matches the attribute name in vpc.yaml
            Description='VPC CIDR',
            Type='String',
            MinLength='1',
            MaxLength='19'
        ))

        self.ownerNameParam = t.add_parameter(Parameter(
            'ownerName',
            Type='String'
        ))

        self.ownerEmailParam = t.add_parameter(Parameter(
            'ownerEmail',
            Type='String'
        ))

    def add_vpc(self):
        t = self.template

        self.vpc = t.add_resource(VPC(
            'Vpc',
            CidrBlock=Ref(self.vpcCidrParam),
            EnableDnsSupport='true',
            EnableDnsHostnames='true',
            Tags=self.defaultTags + [
                Tag('Name', Join("", [
                    self.namePrefix,
                    'Vpc'
                ]))
            ]
        ))

    def add_igw(self):
        t = self.template

        self.igw = t.add_resource(InternetGateway(
            'InternetGateway',
            Tags=self.defaultTags + [
                Tag('Name', Join("", [
                    self.namePrefix,
                    'InternetGateway'
                ]))
            ]
        ))

        self.igwAttachment = t.add_resource(VPCGatewayAttachment(
            'InternetGatewayAttachment',
            VpcId=Ref(self.vpc),
            InternetGatewayId=Ref(self.igw)
        ))

    def add_subnets(self):
        t = self.template

        for subnetDict in self.subnets:
            for i in range(0, self.numAz):
                az = Select(i, GetAZs())
                azNum = str(i+1)
                subnetName = subnetDict['tier']+'Az'+azNum+'Subnet'
                baseCidr = subnetDict['az'+azNum]
                cidr = baseCidr + subnetDict['suffix']
                subnet = self.build_subnet(t, subnetName, az, cidr)
                subnetDict['ID'+azNum] = Ref(subnet)

    def build_subnet(self, t, subnetName, az, cidr):
        subnet = t.add_resource(Subnet(
            subnetName,
            VpcId=Ref(self.vpc),
            AvailabilityZone=az,
            CidrBlock=cidr,
            Tags=self.defaultTags + [
                Tag('Name', Join("", [
                    self.namePrefix,
                    subnetName
                ]))
            ]
        ))
        return subnet

    def add_route_tables(self):
        t = self.template

        for subnetDict in self.subnets:
            tableName = subnetDict['tier']+'RouteTable'
            routeTable = t.add_resource(RouteTable(
                tableName,
                VpcId=Ref(self.vpc),
                Tags=self.defaultTags + [
                    Tag('Name', Join("", [
                        self.namePrefix,
                        tableName
                    ]))
                ]
            )
            self.routeTables[tableName]=Ref(routeTable)

    def add_routes(self):
        t=self.template
        for subnetDict in self.subnets:
            # Add route to Internet Gateway
            if subnetDict['useIgw']:
                igwRoute=t.add_resource(Route(
                    'IGWRouteFor{}RouteTable'.format(subnetDict['tier']),
                    RouteTableId=Ref(subnetDict['tier']+'RouteTable'),
                    DestinationCidrBlock='0.0.0.0/0',
                    GatewayId=Ref(self.igw)
                ))
            # Add route to NAT Gateway
            if subnetDict['useNat']:
                natGwRoute=t.add_resource(Route(
                    'NatGwRouteFor{}RouteTable'.format(subnetDict['tier']),
                    RouteTableId=Ref(subnetDict['tier']+'RouteTable'),
                    DestinationCidrBlock='0.0.0.0/0',
                    NatGatewayId=Ref(self.natGw)
                ))

    def associate_route_tables(self):
        t=self.template

        for subnetDict in self.subnets:
            for i in range(0, self.numAz):
                azNum=str(i+1)
                subnetName=subnetDict['tier']+'Az'+azNum+'Subnet'
                subnetId=subnetDict['ID'+azNum]
                routeTableId=Ref(subnetDict['tier']+'RouteTable')
                self.route_subnet_association(t, subnetName, subnetId,
                                                routeTableId)

    def route_subnet_association(self, t, subnetName, subnetId, routeTableId):
        association=t.add_resource(SubnetRouteTableAssociation(
            'AssociateRt'+subnetName,
            SubnetId=subnetId,
            RouteTableId=routeTableId,
        ))

    def add_outputs(self):
        t=self.template

        self.vpcIdOutput=t.add_output(Output(
            'vpcId',
            Value=Ref(self.vpc),
            Description='VPC Id'
        ))

        self.vpcCidrOutput=t.add_output(Output(
            'vpcCidr',
            Value=Ref(self.vpcCidrParam),
            Description='VPC CIDR range'
        ))

        self.ownerNameOutput=t.add_output(Output(
            'ownerName',
            Value=Ref(self.ownerNameParam),
            Description='Name of owner of resources'
        ))

        self.ownerEmailOutput=t.add_output(Output(
            'ownerEmail',
            Value=Ref(self.ownerEmailParam),
            Description='Email of owner of resources'
        ))

        # Adds subnet IDs to output
        for subnetDict in self.subnets:
            for i in range(0, self.numAz):
                azNum=str(i+1)
                subnetName=subnetDict['tier']+'AZ'+azNum
                output=t.add_output(Output(
                    subnetName+'Id',
                    Value=subnetDict['ID'+azNum],
                    Description=subnetName
                ))

        # Adds route table IDs to output
        for routeTable in self.routeTables:
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
