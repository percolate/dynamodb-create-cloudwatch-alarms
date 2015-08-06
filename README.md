# dynamodb-create-cloudwatch-alarms

[![Circle CI](https://circleci.com/gh/percolate/dynamodb-create-cloudwatch-alarms.svg?style=svg)](https://circleci.com/gh/percolate/dynamodb-create-cloudwatch-alarms)

Automate the creation of DynamoDB ProvisionedThroughput Read/Write Alarms.
The ProvisionedThroughput upper-bound limit in the script is 80%, but this can be altered.

# Quick Start
```bash
$ create_dynamodb_alarms --help

Script used to create above 80% Read/Write Capacity Units alarms
in AWS CloudWatch for each DynamoDB table.
Also updates existing alarms if the parameters changed.

Usage:
    create_dynamodb_alarms [options]
    create_dynamodb_alarms [-h | --help]

Options:
     --debug   Don't send data to AWS

Examples:
    create_dynamodb_alarms
    create_dynamodb_alarms --debug
```

# Install
```bash
$ pip install dynamodb-create-cloudwatch-alarms
```
