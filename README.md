# dynamodb-create-cloudwatch-alarms

[![Circle CI](https://circleci.com/gh/percolate/dynamodb-create-cloudwatch-alarms.svg?style=svg)](https://circleci.com/gh/percolate/dynamodb-create-cloudwatch-alarms)

Automate the creation of DynamoDB Read/Write ThrottleEvents Alarms.
We want to know the first occurrence of a ThrottleEvent, so the threshold is
set to 0.

# Quick Start
```bash
Script that creates AWS CloudWatch alarms Read/Write ThrottleEvents
for each DynamoDB table. Can be set as a cron job.

Usage:
    dynamodb-create-cloudwatch-alarms [options] <sns_topic_arn> <region>
    dynamodb-create-cloudwatch-alarms [-h | --help]

Options:
    --debug    Don't send data to AWS.
    --version  Show version.

Examples:
    dynamodb_create_cloudwatch_alarms some_sns_topic some_region
    dynamodb_create_cloudwatch_alarms some_sns_topic some_region --debug
    dynamodb_create_cloudwatch_alarms --version
```

# Install
```bash
$ pip install dynamodb_create_cloudwatch_alarms
```
