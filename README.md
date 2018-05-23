# dynamodb-create-cloudwatch-alarms

[![Circle CI](https://circleci.com/gh/percolate/dynamodb-create-cloudwatch-alarms.svg?style=svg)](https://circleci.com/gh/percolate/dynamodb-create-cloudwatch-alarms)

Automate the creation of DynamoDB Read/Write ThrottleEvents Alarms.

## Quick Start

```bash
Script that creates AWS CloudWatch alarms Read/Write ThrottleEvents
for each DynamoDB table. Can be set as a cron job.

Usage:
    dynamodb-create-cloudwatch-alarms [options] <threshold> <period>
        <eval_period> <sns_topic_arn> <region>
    dynamodb-create-cloudwatch-alarms [-h | --help]

Options:
    --debug    Do not send data to AWS.
    --version  Show version.

Examples:
    dynamodb-create-cloudwatch-alarms 1 300 12 \
      arn:aws:sns:us-west-2:123456789012:dynamodb us-west-2
    dynamodb-create-cloudwatch-alarms 1 300 12 \
      arn:aws:sns:us-west-2:123456789012:dynamodb us-west-2 --debug
    dynamodb-create-cloudwatch-alarms --version
```

## Install

```bash
pip install dynamodb-create-cloudwatch-alarms
```
