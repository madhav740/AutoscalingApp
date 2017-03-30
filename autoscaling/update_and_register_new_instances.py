import sys,os,time,re
import boto,boto.ec2,boto.utils
import boto.ec2.cloudwatch
from boto.route53.connection import Route53Connection
from boto.route53.record import ResourceRecordSets
import config
import scaling_decision
import amilist
import credentials
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir)) + "/../aws")
import aws_utility
import datetime
import subprocess
import pipes
import boto.ec2.elb

def register_with_load_balancer(lb_name,instance_id):
    conn = boto.ec2.elb.connect_to_region("ap-southeast-1", aws_access_key_id=None,
        aws_secret_access_key=None)
    lb = conn.get_all_load_balancers(load_balancer_names=[lb_name])
    print lb
    instance_ids = [instance_id]
    print instance_ids
    conn.register_instances(lb_name,instance_ids)

def update_code_and_attach_loadbalancer(lbname,tagname,instance_id):
    print "...UPDATING CODEBASE ....\n ....UPDATING HA PROXY...."
    try :
        process = subprocess.Popen("cd "+os.path.abspath(os.path.join(__file__,os.pardir))+"/../server_scripts/release/scripts/ ;"+"fab rsync_config_ini:autoscaling=true,include_instance_tag="+tagname+" ; fab push_to_app_servers:autoscaling=true,include_instance_tag="+tagname+" ; fab rsync_haproxy_cfg:autoscaling=true,include_instance_tag="+tagname,shell=True,stdout=subprocess.PIPE)
        result = process.communicate()[0]
        print result
        print "...UPDATED SUCCESSFULLY...."
        print "REGISTERING WITH LOAD BALANCER...."
        try:
            register_with_load_balancer(lbname,instance_id)
            print "SUCCESFULLY REGISTERED"
        except Exception,ab:
            print "----FAILED TO ATTACH TO LOAD BALANCER----"
            
    except Exception,e:
        print "---FAILED TO UPDATE---"


