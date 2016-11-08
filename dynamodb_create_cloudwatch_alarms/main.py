#!/usr/bin/env python
"""dynamodb-create-cloudwatch-alarms

Script used to create above 80% Read/Write Capacity Units
AWS CloudWatch alarms for each DynamoDB table.
If set as a cron job - updates existing alarms if
Read/Write Capacity Units DynamoDB table parameters changed.


Usage:
    dynamodb-create-cloudwatch-alarms (-s <sns_topic_arn>) [options]
    dynamodb-create-cloudwatch-alarms [-h | --help]

Options:
     -s <sns_topic_arn>    For sending alarm ( require )
     -r <region>           AWS region
     -p <prefix>           DynamoDB name prefix
     --debug               Don't send data to AWS

"""
import time
import boto
import boto.ec2
import boto.dynamodb2
from docopt import docopt
from boto.ec2.cloudwatch import MetricAlarm

DEBUG = False
AWS_REGION = u'ap-northeast-1'
AWS_SNS_ARN = u''
DYNAMO_PREF = u''

DDB_METRICS = frozenset([u'ConsumedReadCapacityUnits',
                         u'ConsumedWriteCapacityUnits'])
ALARM_PERIOD = 60
ALARM_EVALUATION_PERIOD = 5
RATE = 0.9


def _get_ddb_tables_list(ddb_connection):
    """
    Retrieves all DynamoDB table names

    Returns:
        (set) Of valid DynamoDB table names
    """

    ddb_tables_list_all = []

    ddb_tables_list = ddb_connection.list_tables()
    while u'LastEvaluatedTableName' in ddb_tables_list:
        ddb_tables_list_all.extend(ddb_tables_list[u'TableNames'])
        ddb_tables_list = ddb_connection.list_tables(
                exclusive_start_table_name=ddb_tables_list
                [u'LastEvaluatedTableName'])
    else:
        ddb_tables_list_all.extend(ddb_tables_list[u'TableNames'])

    return ddb_tables_list_all


def get_ddb_tables():
    """
    Retrieves all DynamoDB table describe

    Returns:
        (set) Of valid DynamoDB table describe list
    """

    ddb_connection = boto.dynamodb2.connect_to_region(AWS_REGION)
    ddb_tables_list = _get_ddb_tables_list(ddb_connection)

    ddb_tables = set()
    for ddb_table in ddb_tables_list:

        if DYNAMO_PREF and not ddb_table.startswith(DYNAMO_PREF):
            continue

        ddb_table_attributes = ddb_connection.describe_table(ddb_table)

        # creating a variable for each unit to satisfy flake8
        ddb_tablename = ddb_table_attributes[u'Table'][u'TableName']
        ddb_rcu = (ddb_table_attributes
                   [u'Table'][u'ProvisionedThroughput'][u'ReadCapacityUnits'])
        ddb_wcu = (ddb_table_attributes
                   [u'Table'][u'ProvisionedThroughput'][u'WriteCapacityUnits'])
        ddb_tables.add((ddb_tablename, ddb_rcu, ddb_wcu))

        # check GlobalSecondaryIndexes
        if u'GlobalSecondaryIndexes' not in ddb_table_attributes[u'Table']:
            continue

        gsi_list = ddb_table_attributes[u'Table'][u'GlobalSecondaryIndexes']
        for gsi in gsi_list:
            ddb_indexname = gsi[u'IndexName']
            ddb_rcu = (gsi[u'ProvisionedThroughput'][u'ReadCapacityUnits'])
            ddb_wcu = (gsi[u'ProvisionedThroughput'][u'WriteCapacityUnits'])
            ddb_tables.add((ddb_tablename, ddb_rcu, ddb_wcu, ddb_indexname))

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
            existing_alarm_names.update({existing_alarm.name: {
                     u'threshold': existing_alarm.threshold,
                     u'alarm_actions': existing_alarm.alarm_actions}})

    return existing_alarm_names


def get_ddb_alarms_to_create(ddb_tables, aws_cw_connect):
    """
    Creates a Read/Write Capacity Units alarm
    for all DynamoDB tables

    Args:
        ddb_tables (set) ist of all DynamoDB tables
        aws_cw_connect (CloudWatchConnection)

    Returns:
        (set) All new Read/Write Capacity Units alarms that'll be created
        (set) All existing Read/Write Capacity Units alarms that'll be updated
    """
    assert isinstance(ddb_tables, set)
    assert isinstance(aws_cw_connect,
                      boto.ec2.cloudwatch.CloudWatchConnection)

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
            if len(table) > 3:
                alarm_name = u'{0}-{1}-BasicAlarm'.format(
                        table[0] + u'-' + table[3],
                        metric.replace('Consumed', '') + 'Limit')
                alarm_dimensions = {
                        u'TableName': table[0],
                        u'GlobalSecondaryIndexName': table[3]}
            else:
                alarm_name = u'{0}-{1}-BasicAlarm'.format(
                        table[0],
                        metric.replace('Consumed', '') + 'Limit')
                alarm_dimensions = {u'TableName': table[0]}

            ddb_table_alarm = MetricAlarm(
                name=alarm_name,
                namespace=u'AWS/DynamoDB',
                metric=u'{0}'.format(metric), statistic='Sum',
                comparison=u'>=',
                threshold=RATE*threshold*ALARM_PERIOD,
                period=ALARM_PERIOD,
                evaluation_periods=ALARM_EVALUATION_PERIOD,
                # Below insert the actions appropriate.
                alarm_actions=[AWS_SNS_ARN],
                dimensions=alarm_dimensions)

            # we create an Alarm metric for each new DDB table
            if ddb_table_alarm.name not in existing_alarms.iterkeys():
                alarms_to_create.add(ddb_table_alarm)
            # checking the existing alarms thresholds
            # update them if there are changes
            for key, value in existing_alarms.iteritems():
                if key != ddb_table_alarm.name:
                    continue

                if str(value[u'threshold']) != str(ddb_table_alarm.threshold):
                    alarms_to_update.add(ddb_table_alarm)
                elif value[u'alarm_actions'] != ddb_table_alarm.alarm_actions:
                    alarms_to_update.add(ddb_table_alarm)

    return (alarms_to_create, alarms_to_update)


def main():
    args = docopt(__doc__)

    global DEBUG
    global AWS_REGION
    global AWS_SNS_ARN
    global DYNAMO_PREF

    AWS_SNS_ARN = args['-s']

    if args['--debug']:
        DEBUG = True

    if args['-r']:
        AWS_REGION = args['-r']

    if args['-p']:
        DYNAMO_PREF = args['-p']

    ddb_tables = get_ddb_tables()
    aws_cw_connect = boto.ec2.cloudwatch.connect_to_region(AWS_REGION)

    (alarms_to_create,
     alarms_to_update) = get_ddb_alarms_to_create(ddb_tables,
                                                  aws_cw_connect)

    def __counter(x):
        i = [x]
        def __count():
            i[0] += 1
            if i[0] > 10:
                time.sleep(5)
                i[0] = 1
            return i[0]
        return __count

    c = __counter(0)
    # Creating new alarms
    if alarms_to_create:
        if DEBUG:
            for alarm in alarms_to_create:
                print 'DEBUG CREATED:', alarm
        else:
            print 'New DynamoDB table(s) Alarms created:'
            for alarm in alarms_to_create:
                c()
                aws_cw_connect.create_alarm(alarm)
                print alarm

    # Updating existing alarms
    if alarms_to_update:
        if DEBUG:
            for alarm in alarms_to_update:
                print 'DEBUG UPDATED:', alarm
        else:
            print 'DynamoDB table(s) Alarms updated:'
            for alarm in alarms_to_update:
                c()
                aws_cw_connect.update_alarm(alarm)
                print alarm

if __name__ == '__main__':

    main()
