import sys,os,time,re
import boto,boto.ec2,boto.utils
import boto.ec2.cloudwatch
from boto.route53.connection import Route53Connection
from boto.route53.record import ResourceRecordSets
sys.path.append(os.path.abspath(os.path.join(__file__, os.pardir)) + "/../aws")
import datetime
import subprocess
import pipes
import config
import credentials
import requests,json
from datetime import date, timedelta, datetime,time
import time

tag_name_to_instance_id_dict=dict()
tag_name_to_instance_dns_dict=dict()

def get_aws_ro_conn (region='ap-southeast-1'):
    aws_ro_conn = boto.ec2.connect_to_region(region, aws_access_key_id=None,aws_secret_access_key=None)
    return aws_ro_conn


def get_all_instances(server):
    print "GETTING ALL INSTANCES LIST FOR THE "+server
    if server=='app_server':    
        reg_ex=re.compile("CF_PROD_APP_\d\d")
    elif server=='image_server':
        reg_ex=re.compile("CF_PROD_IMG_\d\d")
    elif server=='demo_server':
        reg_ex=re.compile("AUTOSCALING_APP_\d\d")
    print "--CREATING EC2 CONNECTION--"    
    conn=get_aws_ro_conn()
    if conn!=None:
        print "EC2 CONNECTION SUCCESSFUL "
        reservations = conn.get_all_instances()
        for res in reservations:
            for inst in res.instances:
                if 'Name' in inst.tags and reg_ex.match(inst.tags['Name']) and inst.state=='running':
                    tag_name_to_instance_id_dict[inst.tags['Name']]=inst.id
                    tag_name_to_instance_dns_dict[inst.tags['Name']]=inst.public_dns_name
                    print "%s (%s) [%s] " % (inst.tags['Name'],inst.state,inst.public_dns_name)
    else:
        print "FAILED TO CONNECT "
                        
                

def get_ec2_cloudwatch_connection(region='ap-southeast-1',):
    conn=boto.ec2.cloudwatch.connect_to_region(region,aws_access_key_id=None,aws_secret_access_key=None)
    return conn

def calculate_cpu_utilization_metric(instance_id,period,interval_in_sec,statistics):
    conn=get_ec2_cloudwatch_connection()
    dimensions={"InstanceId": instance_id}
    try:
        cpu=conn.get_metric_statistics(period,datetime.utcnow() - timedelta(seconds=interval_in_sec),datetime.utcnow(),'CPUUtilization','AWS/EC2',statistics,dimensions)[0]['Average']
        return float(cpu)
    except Exception,e:
        print e
        return None
        

def calculate_memory_utilization(host):
    print host
    process = subprocess.Popen("fab -H "+host+" find_memory",shell=True,stdout=subprocess.PIPE)
    result = process.communicate()[0].split('\n')
    for items in result:
        if "-/+ buffers/cache:" in items:
            mem=items.split(':')[2].strip()
            mem=" ".join(mem.split()).split(' ')
            used=float (mem[0])
            free=float (mem[1])
            percent_used=(used*100)/(used +free)
    return percent_used    

def calculate_httpd_request(host):
    process = subprocess.Popen("fab -H "+host+" find_httpd_requests",shell=True,stdout=subprocess.PIPE)
    result = process.communicate()[0].split('\n')[2].split(':')[1]
    if result !=None:
        return int(result)


def decide_scaleup_or_scaledown(server,period,interval,statistics):
    tag_name_to_instance_id_dict.clear()
    tag_name_to_instance_dns_dict.clear()
    memory_usage=0.0
    cpu_usage=0.0
    httpd_request=0
    no_of_instances=0
    avg_memory_usage=0.0
    avg_cpu_usage=0.0
    avg_httpd_request=0
    get_all_instances(server)
    print "------"+server+" machines details-----"
    print "--MACHINE NAME--      --CPU USAGE--      --MEMORY USAGE--        --HTTPD REQUESTS--"
    for instances in tag_name_to_instance_id_dict:
        cpu_usage=calculate_cpu_utilization_metric(tag_name_to_instance_id_dict[instances],period,interval,statistics)
        memory_usage=calculate_memory_utilization(tag_name_to_instance_dns_dict[instances])
        httpd_request=calculate_httpd_request(tag_name_to_instance_dns_dict[instances])
        print str(instances) +"  "+str(cpu_usage)+"  "+str(memory_usage)+"  "+str(httpd_request)
        avg_cpu_usage=avg_cpu_usage+cpu_usage
        avg_memory_usage=avg_memory_usage+memory_usage
        avg_httpd_request=avg_httpd_request+httpd_request
        no_of_instances=no_of_instances+1
    print "\n\n TOTAL NO OF INSTANCES IN "+str(server)+" -->"+str(no_of_instances)    
    avg_memory_usage=memory_usage/no_of_instances
    avg_cpu_usage=cpu_usage/no_of_instances
    avg_httpd_request=httpd_request/no_of_instances
    print "AVERAGE MEMORY USAGE ON "+str(server)+" -->"+str(avg_memory_usage)
    print "AVERAGE CPU USAGE ON "+server+" -->"+str(avg_cpu_usage)
    print "AVERAGE HHTPD REQUEST ON "+server+" -->"+str(avg_httpd_request)+" per machine"
    print "\n\n CHECKING AGAINST THRASHOLD VALUES "
    if server=='demo_server':
        if avg_cpu_usage > config.demo_server['cpu_max_utilization'] or avg_memory_usage > config.demo_server['max_memory_utilization'] or avg_httpd_request >config.demo_server['custom_check_max_limit']:
            return 1
        elif avg_cpu_usage < config.demo_server['cpu_min_utilization'] or avg_memory_usage < config.demo_server['min_memory_utilization']:
            return -1
        else:
            return 0

    elif server=='app_server':
        if avg_cpu_usage > config.app_server['cpu_max_utilization'] or avg_memory_usage > config.app_server['max_memory_utilization'] or avg_httpd_request >config.app_server['custom_check_max_limit']:
            return 1
        elif avg_cpu_usage < config.app_server['cpu_min_utilization'] or avg_memory_usage < config.app_server['min_memory_utilization']:
            return -1
        else:
            return 0        

   
     