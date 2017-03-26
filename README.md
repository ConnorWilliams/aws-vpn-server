# AWS OpenVPN Server
This repository contains the code to allow the deployment of your own VPN server in AWS.

The code uses Sceptre to deploy CloudFormation templates.

Prerequisites
- [Create AWS account](aws.amazon.com/free)
- [Create IAM user with programmatic access & save the access keys](http://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console)
- [Create EC2 Key Pair]( http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair)
- Change permissons of the private key
  ```
  chmod 400 my-key-pair.pem
  ```
- [Install AWS CLI to your machine](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)
- [Configure AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-quick-configuration)
- Install Sceptre
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
- Share EC2 key pair with other regions by running `region_share_key` script
  ```
  bash region_share_key.sh path/to/pem_key.pem
  ```
- Select the AWS region you want to launch the OpenVPN Access Server in
  - Edit the `region` value in `config/dev/config.yaml` and `config/dev/openvpn.yaml` to the region you want to launch in
  - [List of regions](http://docs.aws.amazon.com/general/latest/gr/rande.html#cfn_region)
- Launch the environment using Sceptre
  ```
  sceptre launch-env dev
  ```
- Connect to the VPN
  - Navigate to the [EC2 console](console.aws.amazon.com/ec2) in the correct region you selected before.
  - Select the OpenVPN Instance and copy its public IP address.
  - [Follow these instructions to learn how to connect to the VPN](http://envyandroid.com/connecting-android-openvpn/)
