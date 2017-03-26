# AWS OpenVPN Server
This repository contains the code to allow the deployment of your own VPN Access Server in AWS. This code uses Sceptre to deploy AWS CloudFormation templates so this means you will need an AWS account and Sceptre installed on your machine.

## Setup
### AWS
- [Create AWS account](aws.amazon.com/free)
- [Create IAM user with programmatic access & save the access keys](http://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console)
- [Create EC2 Key Pair]( http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair)
- Change permissons of the private key
  ```
  chmod 400 my-key-pair.pem
  ```
- [Install AWS CLI to your machine](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)
- [Configure AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-quick-configuration)
- Share EC2 key pair with other regions by running `region_share_key` script
  ```
  bash region_share_key.sh path/to/pem_key.pem
  ```

### Sceptre
- Install python & pip if you don't have it installed already
- Install virtualenv
  ```
  pip install virtualenv
  ```
- Install virtualenvwrapper
  ```
  pip install virtualenvwrapper
  export WORKON_HOME=~/Envs
  source /usr/local/bin/virtualenvwrapper.sh
  ```
- Create the sceptre virtualenv
  ```
  mkvirtualenv sceptre
  ```
- Select the sceptre virtualenv to work on
  ```
  workon sceptre
  ```
  Note: You will need to `workon sceptre` every time you want to use Sceptre

- Install Sceptre
  ```
  pip install sceptre
  ```

## Usage
- Set the `owner_name` and `owner_email` values in `config/vpn/network.yaml` which will be used to tag the resources
- Set the `vpn_admin_user` and `vpn_admin_pw` values in `config/vpn/openvpn.yaml` which you will use to log in to the VPN
- Set the `key_pair` value in `config/vpn/openvpn.yaml` to the name of the key pair you created earlier
- Edit the `region` value in `config/vpn/config.yaml` and `config/vpn/openvpn.yaml` to the [region](http://docs.aws.amazon.com/general/latest/gr/rande.html#cfn_region) you want to launch in
- Launch the environment using Sceptre
  ```
  sceptre launch-env vpn
  ```
- Connect to the VPN
  - Navigate to the [EC2 console](console.aws.amazon.com/ec2) of the region you just launched the OpenVPN Access Server in.
  - Select the OpenVPN instance and copy its public IP address.
  - [Follow these instructions to learn how to connect to the VPN](http://envyandroid.com/connecting-android-openvpn/)
