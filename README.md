# dynamodb-create-cloudwatch-alarms

[![Circle CI](https://circleci.com/gh/percolate/dynamodb-create-cloudwatch-alarms.svg?style=svg)](https://circleci.com/gh/percolate/dynamodb-create-cloudwatch-alarms)

Automate the creation of DynamoDB ProvisionedThroughput Read/Write Alarms.
The ProvisionedThroughput upper-bound limit in the script is 80%, but this can be altered.

# Quick Start
```bash
$ dynamodb_create_cloudwatch_alarms --help

Script used to create above 80% Read/Write Capacity Units alarms in AWS CloudWatch for each DynamoDB table.
Also updates existing alarms if the parameters changed.

Usage:
    dynamodb_create_cloudwatch_alarms [options]
    dynamodb_create_cloudwatch_alarms [-h | --help]

Options:
    --debug   Don't send data to AWS

Examples:
    dynamodb_create_cloudwatch_alarms
    dynamodb_create_cloudwatch_alarms --debug
```

# Install
```bash
$ pip install dynamodb_create_cloudwatch_alarms
```
