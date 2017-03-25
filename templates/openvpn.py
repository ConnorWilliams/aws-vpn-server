# !/usr/bin/env python
from troposphere import Output, Ref, Template, GetAtt, Join, Base64
# from troposphere import GetAZs, Select
from troposphere.ec2 import Instance, Tag, NetworkInterfaceProperty

class Stack(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.template.add_description(self.sceptre_user_data['application']+': Instance')

        self.DEFAULT_TAGS = [
            Tag('Application', self.sceptre_user_data['application']),
            Tag('Owner Name', self.sceptre_user_data['owner_name']),
            Tag('Owner Email', self.sceptre_user_data['owner_email'])
        ]

        self.add_instance()

        self.add_outputs()

    def add_instance(self):
        t = self.template

        self.openvpn_instance = t.add_resource(Instance(
            'OpenVpnInstance',
            ImageId=self.sceptre_user_data['ami_map'][self.sceptre_user_data['region']],
            InstanceType=self.sceptre_user_data['instance_type'],
            KeyName=self.sceptre_user_data['key_pair'],
            NetworkInterfaces=[
                NetworkInterfaceProperty(
                    AssociatePublicIpAddress=True,
                    DeviceIndex=0,
                    GroupSet=[self.sceptre_user_data['openvpn_sg']],
                    SubnetId=self.sceptre_user_data['subnets']['public_1']
                )
            ],
            UserData=Base64(Join("",
                [
                    "admin_user=",self.sceptre_user_data['vpn_admin_user'],"\n",
                    "admin_pw=",self.sceptre_user_data['vpn_admin_pw'],"\n",
                    "reroute_gw=1\n",
                    "reroute_dns=1\n"
                ]
            )),
            Tags=self.DEFAULT_TAGS + [Tag('Name', self.sceptre_user_data['application']+'-Instance')]
        ))
        return 0

    def add_outputs(self):
        t=self.template

        self.vpn_public_ip=t.add_output(Output(
            'vpnPublicIp',
            Value=GetAtt(self.openvpn_instance, 'PublicIp'),
            Description='Link to Open VPN server.'
        ))

        return 0


def sceptre_handler(sceptre_user_data):
    stack=Stack(sceptre_user_data)
    return stack.template.to_json()

if __name__ == '__main__':
    # for debugging
    import sys
    print('python version: ', sys.version, '\n')
    stack=Stack()
    print(stack.template.to_json())
