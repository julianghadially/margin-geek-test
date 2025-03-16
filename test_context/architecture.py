from os import environ
from json import load as json_load
location = environ.get('LOCATION','')
if location is None:
    with open("env/bin/secrets.json", 'r') as file:
        secrets = json_load(file)
    location = secrets.get('LOCATION','')

amati_agents_path = "/Users/julianghadially/Documents/0. Amati/2. Product/Amati Agents/" #also update in settings.json to help pylance deal with the extra path

def is_in_docker() -> bool:
    """Determine if the current environment is inside a Docker container."""
    try:
        with open("/.dockerenv", "rt") as f:
            return True #"docker" in f.read() or "kubepods" in f.read()
        #with open("/proc/self/cgroup", "rt") as f:
        #    return "docker" in f.read() or "kubepods" in f.read()
    except FileNotFoundError:
        return False
#===============
# API Host Logic:
#===============


#WARNING: with margin-geek-test, sometimes we want to test dev-api from local terminal. 
#we do not use dev_api_host across the entire testing apparatus. 
if location == 'local':
    if is_in_docker():
        dev_api_host = 'http://host.docker.internal:5000'
    else:
        dev_api_host = 'http://127.0.0.1:5000'
    use_prod_redis_in_dev_for_celerytasks = True
else:
    #dev_redis_url = 'redis://redis-local:6379' # localhost in a docker container may just be that docker container itself. so calling out the other container might help
    dev_api_host = 'https://dev-api.margingeek.com:444'
    use_prod_redis_in_dev_for_celerytasks = True
#
#dev_redis_url = 'rediss://red-cski8s5ds78s739c7dhg:'+redisdev_key+'@oregon-redis.render.com:6379'

