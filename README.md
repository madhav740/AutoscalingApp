# AutoscalingApp
python scripts to scale a set of haproxy load balanced ec2 machines

In amilist.py you create a config of server groups
where you mention the ami-id and security group and ha proxy load balancer
group and other aws ec2 instance properties.

This script first figures out all the instances in that server group then
get the metrics like cpu,memory,any custom metric using fab scripts

You can configure based on which property/metric and what threshold value
it should start autoscaling i.e scale up and scale down

