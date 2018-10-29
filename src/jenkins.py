# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
import json
from datetime import datetime
from urllib.parse import urljoin 
import os
import time

from lib.rest import on_events 
from lib.rest import on_start 
from lib.rest import on_catalog
from lib.rest import on_execute
from lib.rest import get_package_cache_path

class Jenkins(kp.Plugin):
 
    TITLE='Jenkins'
    DESCRIPTION="Search jobs"
    TYPE="job"
    PREFIX="j"

    DAYS_KEEP_CACHE = 10
    LIMIT=20
    ITEMCAT = kp.ItemCategory.USER_BASE + 1

    def get_cache_path(self,prefix):
        cache_path = self.get_package_cache_path(True)
        return os.path.join(cache_path, prefix + self.TITLE.lower() +  '.json')


    def get_url_channel(self,url):
        return urljoin(url ,'api/json?tree=jobs[name,url]')

    def get_jobs(self,urlChannels):
        try:
            opener = kpnet.build_urllib_opener()
            self.dbg(urlChannels)
            with opener.open(urlChannels) as request:
                response = request.read()
                data = json.loads(response) 
                with open(self.get_cache_path(str(int(round(time.time()))) +self.PREFIX), "w") as index_file:
                    json.dump(data, index_file, indent=2)    
                for j in data['jobs']:
                    if  "folder" in j['_class'] :
                        ch= self.get_url_channel (j['url'])  
                        self.get_jobs(ch)  

        except Exception as exc:
            self.err("Could not reach the entries to generate the cache: ", exc)   

    def generate_cache(self):
        self.dbg("generate_cache user",self.DOMAIN) 
        cache_path_c = self.get_cache_path(self.PREFIX)
        should_generate = False
        cache_path = self.get_package_cache_path(True)
        self.dbg(cache_path) 

        for i in os.listdir(cache_path):
            self.dbg('Find',i) 
            if os.path.isfile(os.path.join(cache_path,i)) and (self.PREFIX + self.TITLE.lower())  in i:
                file = os.path.join(cache_path,i)
                self.dbg('file',file)
                break
        
        try:
            last_modified = datetime.fromtimestamp(os.path.getmtime(file)).date()
            if ((last_modified - datetime.today().date()).days > self.DAYS_KEEP_CACHE):
                should_generate = True
        except Exception as exc:
            should_generate = True

        if not should_generate:
            return True
        ch=self.get_url_channel(self.DOMAIN) 
        self.get_jobs(ch)
        return True
  
    def get_entries(self):
        self.dbg('Get entries')
        if not self.entries:
            cache_path = self.get_package_cache_path(True)
            for i in os.listdir(cache_path):
                self.dbg(i)
                if os.path.isfile(os.path.join(cache_path,i)) and (self.PREFIX + self.TITLE.lower()) in i:
                    with open(os.path.join(cache_path,i), "r") as users_file:
                        data = json.loads(users_file.read())
                        for item in data['jobs']:
                            self.dbg('jobs:' ,item['name']) 
                            #self.dbg("-------------------------") 
                            typeJ=self.TYPE
                            if "folder" in item['_class']:
                                typeJ="folder"

                            suggestion = self.create_item(
                                category=self.ITEMCAT,
                                label=item['name'],
                                short_desc=typeJ,
                                target=item['url'],
                                args_hint=kp.ItemArgsHint.FORBIDDEN,
                                hit_hint=kp.ItemHitHint.IGNORE
                            )
                            self.entries.append(suggestion)    

        self.dbg('Length:' , len(self.entries) )
        return self.entries

    # read ini config
    def read_config(self):
        self.dbg("Reading config")
        settings = self.load_settings()

        self.DOMAIN = str(settings.get("DOMAIN", "main"))

        if not self.DOMAIN  :
            self.dbg("Not configured",self.DOMAIN)
            return False   
        return True
