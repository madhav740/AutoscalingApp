from fabric.api import run

def find_memory():
    run('free -m| grep buffers/cache: ')
def find_httpd_requests():
	run('ps aux | grep httpd | wc -l')
