from sys import platform
from traceback import format_exc
from pydantic.class_validators import validator
import pywebio.input as IN
import pywebio.output as OUT
import time
import threading

from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class WebActionEntityConfiguration(Configuration):

    id: str

    expose_state: str

    payload_on: Optional[str] = "on"

    payload_off: Optional[str] = "off"


@configuration
class WebPlatformConfiguration(PlatformConfiguration):
    '''Configuration setting for the pywebio Dashboard.'''

    @validator('platform')
    def check_platform(cls, v):
        if "plugins.web" not in v:
            raise ValueError("wrong platform: plugins.web, is: " + v)
        return v

    port: int
    '''NYI'''

    exports: list[WebActionEntityConfiguration]
    '''Scripts to display in the pywebio Dashboard.'''        


class WebActionEntity(Stackable, Disposeable, Logging):

    def __init__(self, parent: Stackable, config: WebActionEntityConfiguration) -> None:
        from plugins.web.Platform import Platform
        super().__init__(parent)
        
        self.platform: Platform 
        if type(parent) is Platform:
            self.platform = parent 

        self.configuration = config
        self.app = parent.get_app()

        self.wrapped_id = self.app.get_id(self.configuration.id)

    def on_updated(self):
        pass

    def get_state(self):
        '''Returns the internal state of the exposed entity.'''

        exp_state = str(self.configuration.expose_state) #type: ignore
        path = exp_state.split('.') #type: ignore
        act = self.wrapped_id
        for path_element in path:
            act = getattr(act, path_element)
        return act        
    
    def start(self, call_stack: CallStack):
        class update(Automation):
            def invoke(_, call_stack: CallStack): #type: ignore
                act_state = self.get_state()
                self.platform.has_been_updated = True
                self.on_updated()

        self.wrapped_id.on_state_changed_automations.append(update(self, AutomationConfiguration())) #type: ignore    

    def toggle(self):
        if isinstance(self.wrapped_id, BaseAction):
            call_stack = CallStack()
            
            act_state = self.get_state()

            if (act_state == True):
                act_state = self.configuration.payload_on
            elif (act_state == False):
                act_state = self.configuration.payload_off

            if act_state == self.configuration.payload_on:
                call_stack = call_stack.with_key("payload", self.configuration.payload_off)
            elif act_state == self.configuration.payload_off:
                call_stack = call_stack.with_key("payload", self.configuration.payload_on)

            self.wrapped_id.invoke(call_stack)

class Platform(BasePlatform):
    '''Web Dashboard based on pywebio.'''

    def __init__(self, parent: Stackable, config: WebPlatformConfiguration) -> None:
        super().__init__(parent, config)
        
        self.configuration = config
        self.logs = [["Logs"]]
        self.table = [["Topic", "Payload"]]
        self.entities = [["Platform", "Id", {}]]
        self.entities[0][2] = "Payload"

        self.has_been_updated = True
        self.has_started = False

        self.exports: list[WebActionEntity] = []
    


    def update(self, topic, payload):
        while not self.has_started:
            time.sleep(1)

        for line in self.table:
            if line[0] == topic:
                line[1] = payload
                self.has_been_updated = True
                return           

        self.has_been_updated = True

    def add_log(self, text):
        while not self.has_started:
            time.sleep(1)

        self.logs.append([text])
        self.has_been_updated = True


    def start(self, call_stack: CallStack):
        for entity_configuration in self.configuration.exports:
            web_action_entity = WebActionEntity(self, entity_configuration)
            web_action_entity.start(call_stack)
            id = entity_configuration.id
            state = web_action_entity.get_state()

            def get_color():
                if state == True:
                    return "success"
                elif state == False:
                    return "warning"
                else:
                    return "brown"

            self.entities.append(["___", id, OUT.put_button(str(state), onclick=lambda: web_action_entity.toggle(), color=get_color(), outline=True)])      

            def update():
                for entity in self.entities:
                    if entity[1] == entity_configuration.id:
                        id = web_action_entity.configuration.id
                        state = web_action_entity.get_state()
                        #entity[1] = id
                        entity[2] = OUT.put_button(str(state), onclick=lambda: web_action_entity.toggle(), color=get_color(), outline=True)

            web_action_entity.on_updated = update
            self.exports.append(web_action_entity)    
       

        def loop():
            OUT.set_scope('result')
            while True:
                if self.has_been_updated:
                    self.has_been_updated = False
                    with OUT.use_scope('result', clear=True):
                        OUT.put_markdown(" ## Table")
                        OUT.put_table(self.table)
                        OUT.put_markdown(" ## Logs")
                        OUT.put_table(self.logs)
                        OUT.put_markdown(" ## Entities")
                        OUT.put_table(self.entities)

                time.sleep(0.2)
                
        
        loop_thread = threading.Thread(target=loop)
        loop_thread.start()
        super().start(call_stack)
        self.has_started = True

