regions=(
  'us-east-1'
  'us-east-2'
  'us-west-1'
  'us-west-2'
  'eu-west-1'
  'eu-west-2'
  'eu-central-1'
  'ap-southeast-1'
  'ap-southeast-2'
  'ap-south-1'
  'ap-northeast-1'
  'ap-northeast-2'
  'sa-east-1'
  'ca-central-1'
)

# Generate OpenSSH public key from private key
pubkey="$(openssl rsa -in $1 -pubout)"

# Remove prefix, suffix and whitespace so we are only left with public key
prefix="-----BEGIN PUBLIC KEY-----"
suffix="-----END PUBLIC KEY-----"
pubkey=${pubkey#$prefix}
pubkey=${pubkey%$suffix}
pubkey="$(echo -e "${pubkey}" | tr -d '[:space:]')"

# Import key to all regions
for i in "${regions[@]}"
do
  aws ec2 import-key-pair --region $i --key-name connorwilliams --public-key-material $pubkey
done
