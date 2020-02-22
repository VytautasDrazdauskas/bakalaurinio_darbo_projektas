import service.device_types.default_device as default_device
import service.device_types.heater as heater
import service.helpers.enums as enums
import service.logger as logger
import service.models as models
from service.mqtt_service import MQTTService as mqtt
from service.lib.json2obj import JsonParse

def get_device_config(session, device, job): 
    if (device.device_type == enums.DeviceType.Heater.value):
        return session.query(heater.HeaterConfig).filter_by(uuid=job.config_uuid).first()
    elif (device.device_type == enums.DeviceType.Default.value):
        return session.query(default_device.DefaultDeviceConfig).filter_by(uuid=job.config_uuid).first()

def execute_job(user, device, config, stop_job=False):
    payload_list = []
    if (device.device_type == enums.DeviceType.Heater.value):
        payload_list = heater.form_config_mqtt_payload(config, stop_job)
        
    elif (device.device_type == enums.DeviceType.Default.value):
        payload_list = default_device.form_config_mqtt_payload(config, stop_job)

    systemName = "system"
    topic = user.uuid + "/" + systemName + "/" + device.mac + "/control"
    response_topic = topic + "/response"

    result = None
    for payload in payload_list:
        response = JsonParse(mqtt.publish_with_response(topic=topic, response_topic=response_topic, message=payload, timeout=5))

        if(response.success):
            result = True
        else:
            logger.log_scheduler('Klaidos: ' + response.reason)
            result = False

    return result

def save_device_history(session,device,text):
    device_history = models.UserDeviceHistory(
        device_id=device.id,
        text=text
    )
    session.add(device_history)

