# dynamodb-create-cloudwatch-alarms

[![Circle CI](https://circleci.com/gh/percolate/dynamodb-create-cloudwatch-alarms.svg?style=svg)](https://circleci.com/gh/percolate/dynamodb-create-cloudwatch-alarms)

Automate the creation of DynamoDB ProvisionedThroughput Read/Write Alarms.
The `ProvisionedThroughput` upper-bound limit in the script is 80%, but this can be altered.

# Quick Start
```bash
$ dynamodb_create_cloudwatch_alarms --help

Script used to create above 80% Read/Write Capacity Units
AWS CloudWatch alarms for each DynamoDB table.
If set as a cron job - updates existing alarms if
Read/Write Capacity Units DynamoDB table parameters changed.

Usage:
    dynamodb-create-cloudwatch-alarms (-s <sns_topic_arn>) [-r <region>] [-p <prefix>] [--debug] 
    dynamodb-create-cloudwatch-alarms [-h | --help]

Options:
     -s <sns_topic_arn>    For sending alarm ( require )
     -r <region>           AWS region
     -p <prefix>           DynamoDB name prefix
     --debug               Don't send data to AWS

```

# Install and Usage
```bash
$ git clone git@github.com:kentokento/dynamodb-create-cloudwatch-alarms.git
$ cd ./dynamodb-create-cloudwatch-alarms
$ make develop
$ dynamodb-create-cloudwatch-alarms -s arn:aws:sns:ap-northeast-1:xxxxxxxxxx:hoge
```
