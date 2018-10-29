# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
from urllib.parse import urljoin 
import os

def on_events(self, flags):
    """
    Reloads the package config when its changed
    """
    if flags & kp.Events.PACKCONFIG:
        self.read_config()

def on_start(self):
    self.dbg("On Start")
    if self.read_config():
        if self.generate_cache():
            self.cache_is_active()
            self.get_entries()
    pass

def on_catalog(self):
    self.dbg("On catalog")
    self.set_catalog([
        self.create_item(
            category=kp.ItemCategory.KEYWORD,
            label=self.TITLE,
            short_desc=self.DESCRIPTION,
            target=self.TITLE.lower(),
            args_hint=kp.ItemArgsHint.REQUIRED,
            hit_hint=kp.ItemHitHint.KEEPALL
        )
    ])

def on_suggest(self, user_input, items_chain):
    if not items_chain or items_chain[0].category() != kp.ItemCategory.KEYWORD:
        return

    suggestions = self.filter(user_input)
    self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.LABEL_ASC)

def filter(self, user_input):
    return list(filter(lambda item: self.has_name(item, user_input), self.entries))

def has_name(self, item, user_input):
    self.dbg(user_input.upper(),item.label().upper())
    if user_input.upper() in item.label().upper():
        return item
    return False

def on_execute(self, item, action):
    if item.category() != self.ITEMCAT:
        return
    url=item.target()
    self.dbg(item.target())
    kpu.web_browser_command(private_mode=None,url=url,execute=True)

  
def get_cache_path(self,prefix):
    cache_path = self.get_package_cache_path(True)
    return os.path.join(cache_path, prefix + self.TITLE.lower() +  '.json')

def cache_is_active(self):
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

    if should_generate:
        self.cache_remove()    

    return should_generate

def cache_remove(self):
    cache_path_c = self.get_cache_path(self.PREFIX)
    cache_path = self.get_package_cache_path(True)
    self.dbg(cache_path) 

    for i in os.listdir(cache_path):
        self.dbg('Find',i) 
        if os.path.isfile(os.path.join(cache_path,i)) and (self.PREFIX + self.TITLE.lower())  in i:
            file = os.path.join(cache_path,i)
            os.remove(file)

