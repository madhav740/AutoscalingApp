import sys,os,time,re
import boto,boto.ec2,boto.utils
import boto.ec2.cloudwatch
from boto.route53.connection import Route53Connection
from boto.route53.record import ResourceRecordSets
import config
import scaling_decision
import amilist
import credentials
import update_and_register_new_instances
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir)) + "/../aws")

import aws_utility
import datetime
import subprocess
import pipes
from boto import elasticache,cloudfront,ec2,boto
if os.path.abspath(os.path.join(__file__, os.pardir) + "/../pubkeys") not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir) + "/../pubkeys"))
import AwsUtil

def create_replica(conn, tagname,latest_tagname, security_group, use_same_image, ami_id, zone):
    print 'Entering create_replica function'
    try:
        print tagname
        res_ami_id = ''
        aws_instance = AwsUtil.get_only_instance_by_name_or_exit(conn,latest_tagname)
        key_name = aws_instance.key_name
        instance_type = aws_instance.instance_type
        if ami_id and use_same_image.lower() == 'true':
            print 'Using same image ' + ami_id
            res_ami_id = ami_id
        else:
            print 'Creating new image'
            curr_date_time = str(datetime.datetime.now())
            curr_date_time = curr_date_time.split(' ')
            curr_date = curr_date_time[0]
            curr_time = repr(time.time())
            ami_name = 'loadtest_' + tagname.lower() + '_' + curr_date + '_' + curr_time
            res_ami_id = conn.create_image(aws_instance.id, ami_name, no_reboot=True)
            ami_id = res_ami_id
            print res_ami_id

            image_status = conn.get_image(res_ami_id)
            print '-----------------------[Begin Image Creation]--------------------------'
            print datetime.datetime.now()

            while image_status.state == 'pending':
                time.sleep(10)
                image_status = conn.get_image(res_ami_id)

            print datetime.datetime.now()
            print '-----------------------[Completed Image Creation]-----------------------'

            if image_status.state == 'failed':
                print 'Bad Image.'
                exit(1)

        reservation = conn.run_instances(res_ami_id, key_name=key_name, instance_type=instance_type, security_groups=[security_group], placement=zone)
        instance = reservation.instances[0]
        print instance.id
        state = instance.update()
        while state == 'pending':
            time.sleep(2)
            state = instance.update()

        if state == 'running':
            instance.add_tag("Name",tagname)

        else:
            print('Instance state: ' + state)
            return None

        time.sleep(200)

        return instance.id
    except Exception as e:
        print e
        return ami_id, 0
    finally:
        print 'Leaving create_replica function'


def stop_instance(conn, tagname):
    aws_instance = AwsUtil.get_only_instance_by_name_or_exit(conn, tagname)
    instance_id = aws_instance.id
    if aws_instance.state == 'running':
        conn.stop_instances(instance_ids=[instance_id])

