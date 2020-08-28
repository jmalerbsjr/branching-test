#!/bin/sh -l

#SSH_PRIVATE_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDx7EBzPYXi99ay3Lli/vrEfK+WK2gxnTRGeqlJd4VHA1gDz+ncdGR9xBXBPvIe6OdkxLbh4xZ99slnazvU5BKtMzc8yNlMOeycU9ICnlnh5RA0OnxuVogsk0gLPpF0eEh58e+SsLaeODRzUei3LRdalgUkIrFtvqWsEtqjVX/3gp+DXX8p81vMEtvtXYi/mBVH3XSc/tcVyT0u5hJBCUVSHzqkgMPR4+MA6BAuSHzXjrWXFNc3wE+6BIS781i+eHYf2tfdOXdj5uaBYixHSjpo+5xndJkT9HLl1/doT5qRpF6A88SG2OVgwm0qrCm0hzMm5bFG/hQjgLhQzUHxl75LybJzBtadiFgkfVZgNGeQrVed1qq2zENB+cwkDFvKiQr9p9LT4d3hVNNiydBqvTmgGXcaD9l0YxlDbtjn1kRyirinf2YAHwzbqoSnlq8rLFD3DMiccAtwJJ2eFQ87YuF5JmC0YLRKwFf5HSLtLRawBMrojvQDc9d8CqpsMhh+IzErVlc0hmOZCQ9CbpsbSK5bPMIVZFyTyFHYS7Asb2cOtV0EmlkmM2qwXn8ZZn1ZeJ5aK6JtmLhhbb+FVLpnjCJx2BhcCF4PolIXjReAPdB9ZJejn3TBobAxVqGhE1A6z1CnIqdWHirspIy0xS6KLDJ+rwFwB9nE/Jmz9fRqbLIZzQ== joseph.malerba.jr@gmail.com"

#echo "$SSH_PRIVATE_KEY" > ~/.ssh/known_hosts
#ssh-keyscan github.com >> $HOME/.ssh/known_hosts

output=$(ls)
echo $output
cd $GITHUB_WORKSPACE
echo $(ls /github/workspace)

##git clone git@github.com:jmalerbsjr/branching-test.git
#
#echo "Hello $1"
#time=$(date)
#echo "::set-output name=time::$time"
#echo $GITHUB_WORKSPACE
#echo $GITHUB_REF
#tags=$(git fetch --tags)
#echo $tags