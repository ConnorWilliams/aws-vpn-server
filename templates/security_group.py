#!/usr/bin/env python
# This Python template generates
import os

from troposphere import Output, Parameter, Ref, Template, Join, Base64
from troposphere import GetAZs, Select, Join, GetAtt
from troposphere.ec2 import Tag, SecurityGroup, SecurityGroupRule
from troposphere.elasticloadbalancing import LoadBalancer, Listener, HealthCheck
from troposphere.rds import DBSubnetGroup, DBInstance
from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration
from troposphere.policies import UpdatePolicy, AutoScalingRollingUpdate
from troposphere.autoscaling import Tag as ASTag
from troposphere import cloudformation as cfn

class SG(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data

        self.template.add_description(self.sceptre_user_data['application'] + ' ' + self.sceptre_user_data['sg_name']+" Security Group Stack")

        self.DEFAULT_TAGS = [
            Tag('Application', self.sceptre_user_data['application']),
            Tag('Environment', self.sceptre_user_data['environment']),
            Tag('Owner', self.sceptre_user_data['owner'])
        ]

        self.add_security_group()

        self.add_outputs()

    def add_security_group(self):
        t = self.template

        self.security_group = t.add_resource(SecurityGroup(
            self.sceptre_user_data['sg_name']+'SecurityGroup',
            VpcId=self.sceptre_user_data['vpc_id'],
            GroupDescription='Security Group.',
            SecurityGroupIngress=self.create_rules(self.sceptre_user_data['rules']),
            Tags=self.DEFAULT_TAGS + [Tag('Name', self.sceptre_user_data['application']+self.sceptre_user_data['sg_name']+'SG')]
        ))
        return 0

    def create_rules(self, rules):
        ingress_rules = []

        for rule in rules:
            ingress_rule = 0
            if 'source_security_group_id' in rule:
                ingress_rule = SecurityGroupRule(
                    ToPort=rule['to_port'],
                    FromPort=rule['from_port'],
                    IpProtocol=rule['ip_protocol'],
                    SourceSecurityGroupId=rule['source_security_group_id']
                )
            elif 'cidr_ip' in rule:
                ingress_rule = SecurityGroupRule(
                    ToPort=rule['to_port'],
                    FromPort=rule['from_port'],
                    IpProtocol=rule['ip_protocol'],
                    CidrIp=rule['cidr_ip']
                )
            ingress_rules.append(ingress_rule)
        return ingress_rules

    def add_outputs(self):
        t = self.template

        self.security_group_output = t.add_output(Output(
            'SecurityGroup',
            Value=Ref(self.security_group)
        ))
        return 0


def sceptre_handler(sceptre_user_data):
    security_group = SG(sceptre_user_data)
    return security_group.template.to_json()


if __name__ == '__main__':
    # for debugging
    import sys
    print('python version: ', sys.version, '\n')
    security_group = SG()
    print(security_group.template.to_json())
