#!/usr/bin/env python
"""dynamodb-create-cloudwatch-alarms

Script used to create above 80% Read/Write Capacity Units
AWS CloudWatch alarms for each DynamoDB table.
If set as a cron job - updates existing alarms if
Read/Write Capacity Units DynamoDB table parameters changed.


Usage:
    dynamodb-create-cloudwatch-alarms [options] <sns_topic_arn> <region>
    dynamodb-create-cloudwatch-alarms [-h | --help]

Options:
    --debug    Don't send data to AWS.
    --version  Show version.

"""
import boto
import boto.ec2
import boto.ec2.cloudwatch
import boto.dynamodb
from docopt import docopt
from boto.ec2.cloudwatch import MetricAlarm

from constants import VERSION

DEBUG = False

DDB_METRICS = frozenset([u'ConsumedReadCapacityUnits',
                         u'ConsumedWriteCapacityUnits'])
ALARM_PERIOD = 300
ALARM_EVALUATION_PERIOD = 12


def get_ddb_tables(region):
    """
    Retrieves all DynamoDB table names

    Args:
        region (str)

    Returns:
        (set) Of valid DynamoDB table names
    """
    assert isinstance(region, str)

    ddb_connection = boto.dynamodb.connect_to_region(region)
    ddb_tables_list = ddb_connection.list_tables()
    ddb_tables = set()
    for ddb_table in ddb_tables_list:

        ddb_table_attributes = ddb_connection.describe_table(ddb_table)
        # creating a variable for each unit to satisfy flake8
        ddb_tablename = ddb_table_attributes[u'Table'][u'TableName']
        ddb_rcu = (ddb_table_attributes
                   [u'Table'][u'ProvisionedThroughput'][u'ReadCapacityUnits'])
        ddb_wcu = (ddb_table_attributes
                   [u'Table'][u'ProvisionedThroughput'][u'WriteCapacityUnits'])
        ddb_tables.add((ddb_tablename, ddb_rcu, ddb_wcu))

    return ddb_tables


def get_existing_alarm_names(aws_cw_connect):
    """
    Retrieves all DynamoDB related CloudWatch alarm names

    Args:
        aws_cw_connect (CloudWatchConnection)

    Returns:
        (dict) Existing CloudWatch DDB alarms (name and threshold)
    """
    assert isinstance(aws_cw_connect,
                      boto.ec2.cloudwatch.CloudWatchConnection)

    page_loop = aws_cw_connect.describe_alarms()
    existing_alarms = set()

    # adding the 1st page of alarms
    for alarm in page_loop:
        existing_alarms.add(alarm)

    while page_loop.next_token:
        page_loop = (aws_cw_connect.
                     describe_alarms(next_token=page_loop.next_token))
        # appending the latter pages
        for alarm in page_loop:
            existing_alarms.add(alarm)

    existing_alarm_names = {}

    for existing_alarm in existing_alarms:
        if existing_alarm.namespace == u'AWS/DynamoDB':
            existing_alarm_names.update({existing_alarm.name:
                                         existing_alarm.threshold})

    return existing_alarm_names


def get_ddb_alarms_to_create(ddb_tables, aws_cw_connect, sns_topic_arn):
    """
    Creates a Read/Write Capacity Units alarm
    for all DynamoDB tables

    Args:
        ddb_tables (set) ist of all DynamoDB tables
        aws_cw_connect (CloudWatchConnection)
        sns_topic_arn (str)

    Returns:
        (set) All new Read/Write Capacity Units alarms that'll be created
        (set) All existing Read/Write Capacity Units alarms that'll be updated
    """
    assert isinstance(ddb_tables, set)
    assert isinstance(aws_cw_connect,
                      boto.ec2.cloudwatch.CloudWatchConnection)
    assert isinstance(sns_topic_arn, str)

    alarms_to_create = set()
    alarms_to_update = set()
    existing_alarms = get_existing_alarm_names(aws_cw_connect)

    for table in ddb_tables:
        # we want two alarms per DynamoDB table
        for metric in DDB_METRICS:
            if metric == u'ConsumedReadCapacityUnits':
                threshold = table[1]
            elif metric == u'ConsumedWriteCapacityUnits':
                threshold = table[2]
            # initiate a MetricAlarm object for each DynamoDb table.
            # for the threshold we calculate the 80 percent
            # from the tables ProvisionedThroughput values
            ddb_table_alarm = MetricAlarm(
                name=u'{}-{}-BasicAlarm'.format(table[0],
                                                (metric.
                                                 replace('Consumed',
                                                         '') + 'Limit')),
                namespace=u'AWS/DynamoDB',
                metric=u'{}'.format(metric), statistic='Sum',
                comparison=u'>=',
                threshold=0.8*threshold*ALARM_PERIOD,
                period=ALARM_PERIOD,
                evaluation_periods=ALARM_EVALUATION_PERIOD,
                # Below insert the actions appropriate.
                alarm_actions=[sns_topic_arn],
                dimensions={u'TableName': table[0]})

            # we create an Alarm metric for each new DDB table
            if ddb_table_alarm.name not in existing_alarms.iterkeys():
                alarms_to_create.add(ddb_table_alarm)
            # checking the existing alarms thresholds
            # update them if there are changes
            for key, value in existing_alarms.iteritems():
                if (key == ddb_table_alarm.name
                        and value != ddb_table_alarm.threshold):
                    alarms_to_update.add(ddb_table_alarm)

    return (alarms_to_create, alarms_to_update)


def main():
    args = docopt(__doc__, version=VERSION)

    global DEBUG

    if args['--debug']:
        DEBUG = True

    region = args['<region>']

    sns_topic_arn = args['<sns_topic_arn>']

    ddb_tables = get_ddb_tables(region)
    aws_cw_connect = boto.ec2.cloudwatch.connect_to_region(region)

    (alarms_to_create,
     alarms_to_update) = get_ddb_alarms_to_create(ddb_tables,
                                                  aws_cw_connect,
                                                  sns_topic_arn)

    # Creating new alarms
    if alarms_to_create:
        if DEBUG:
            for alarm in alarms_to_create:
                print 'DEBUG CREATED:', alarm
        else:
            print 'New DynamoDB table(s) Alarms created:'
            for alarm in alarms_to_create:
                print alarm
                aws_cw_connect.create_alarm(alarm)

    # Updating existing alarms
    if alarms_to_update:
        if DEBUG:
            for alarm in alarms_to_update:
                print 'DEBUG UPDATED:', alarm
        else:
            print 'DynamoDB table(s) Alarms updated:'
            for alarm in alarms_to_update:
                print alarm
                aws_cw_connect.update_alarm(alarm)

if __name__ == '__main__':

    main()
