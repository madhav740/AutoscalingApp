app_server={
'max_memory_utilization':'90',
'min_memory_utilization':'5',
'cpu_max_utilization':'50',
'cpu_min_utilization':'10',
'min_instances':'10',
'max_instances':'100',
'max_no_proceses':'70',
'params_to_check':'cpu,memory,custom',
'custom_command':'ps aux | grep httpd | wc -l',
'custom_check_max_limit':70,
'custom_check_min_limit':10,
}

demo_server={
'max_memory_utilization':'90',
'min_memory_utilization':'5',
'cpu_max_utilization':'50',
'cpu_min_utilization':'2',
'min_instances':'10',
'max_instances':'100',
'max_no_proceses':'70',
'params_to_check':'cpu,memory,custom',
'custom_command':'ps aux | grep httpd | wc -l',
'custom_check_max_limit':70,
'custom_check_min_limit':10,
}

