import sys,os,time,re
import boto,boto.ec2,boto.utils
import boto.ec2.cloudwatch
from boto.route53.connection import Route53Connection
from boto.route53.record import ResourceRecordSets
import config
import scaling_decision
import amilist
import credentials
import automated_aws_handling
import update_and_register_new_instances
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir)) + "/../aws")
import aws_utility
import datetime
import subprocess
import pipes



#in ordr to change the app_server or image_server do change aws_utility.create_replica() method

print amilist.demo_server['security-group']
server_list=['demo_server']
period=3600
interval=3600
statistics='Average'
connection=boto.ec2.connect_to_region('ap-southeast-1', aws_access_key_id=None,aws_secret_access_key=None)

for servers in server_list:
    print "------STARTING MONITORING ON "+servers+" --------"
    decision=scaling_decision.decide_scaleup_or_scaledown(servers,period,interval,statistics)
    latest_tag_name=max(scaling_decision.tag_name_to_instance_id_dict.keys())
    print "-----TAKING DECISIONS--------"
    if decision==1:
        print "....SEEMS LIKE WE HAVE AN OVERLOADED SERVER..."
        print " ADDING A MACHINE TO SERVER \n\n GETTING MACHINE DETAILS...."

        tag_name_suffix=int (latest_tag_name[-2:])
        if tag_name_suffix < 9:
            add_suffix="0"+str(tag_name_suffix+1)
        else:
            add_suffix=str(tag_name_suffix+1)
        tagname=latest_tag_name.rstrip(latest_tag_name[-2:])+add_suffix
        print " MACHINE WITH TAGNAME "+tagname+" IS CREATED....\n\n HOLD ON FOR A MOMENT......"
        if servers=='demo_server':
            #instance_id=automated_aws_handling.create_replica(connection,tagname,latest_tag_name,amilist.demo_server['security-group'],'True', amilist.demo_server['ami-id'],'ap-southeast-1a')
            print "...MACHINE SUCCESSFULLY CREATED AND ADDED...."
            #update_and_register_new_instances.update_code_and_attach_loadbalancer(amilist.demo_server['load-balancer'],tagname,instance_id)
        elif servers=='app_server':
            #instance_id=automated_aws_handling.create_replica(connection,tagname,latest_tag_name,amilist.app_server['security-group'],'True', amilist.app_server['ami-id'],'ap-southeast-1a')
            print "...MACHINE SUCCESSFULLY CREATED AND ADDED...."
            #update_and_register_new_instances.update_code_and_attach_loadbalancer(amilist.demo_server['load-balancer'],tagname,instance_id)
            

            
    elif decision==-1:
        print "SERVER HAS UNDER UTILIZED RESOURCES...SNATCHING THEM...."
        #automated_aws_handling.stop_instance(connection,latest_tag_name)
    else:
        print server+" is scalable and running fine"
            
             



        

        

