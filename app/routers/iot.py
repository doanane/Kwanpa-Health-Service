from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging
import json

from app.database import get_db
from app.models.iot_device import IoTDevice, VitalReading
from app.config import settings
from app.handler.emergency_handler import emergency_handler


try:
    from azure.iot.device import IoTHubDeviceClient, Message

    AZURE_IOT_AVAILABLE = True
except ImportError:
    IoTHubDeviceClient = None
    Message = None
    AZURE_IOT_AVAILABLE = False

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/iot", tags=["IoT"])


class VitalReadingData(BaseModel):
    heart_rate: Optional[int] = None
    blood_oxygen: Optional[float] = None
    is_emergency: Optional[bool] = False


class IoTDataPayload(BaseModel):
    device_id: str
    user_id: int
    vital_data: VitalReadingData
    timestamp: Optional[str] = None


class HeartRateData(BaseModel):
    heart_rate: int
    device_id: Optional[str] = "mobile_device_001"
    timestamp: Optional[str] = None


class AzureFunctionData(BaseModel):
    device_id: str
    heart_rate: int
    timestamp: str
    data_type: str


@router.post("/forward_to_hub")
async def forward_to_hub(data: HeartRateData):
    """
    Endpoint to receive heart rate data from
    React Native and forward to IoT Hub
    """
    try:
        logger.info(f"Received heart rate data: {data.heart_rate}")

        # before forwarding handle all emergencies
        if data.heart_rate > 120:
            emergency_handler(data.heart_rate)

        if not AZURE_IOT_AVAILABLE or IoTHubDeviceClient is None:
            return {
                "status": "success",
                "message": "Data received (Azure IoT not configured)",
                "heart_rate": data.heart_rate,
            }

        message_payload = {
            "device_id": "hf93j3",
            "heart_rate": data.heart_rate,
            "timestamp": data.timestamp or datetime.now().isoformat(),
            "data_type": "heart_rate",
        }

        device_client = IoTHubDeviceClient.create_from_connection_string(
            settings.IOT_HUB_CONNECTION_STRING
        )

        try:
            device_client.connect()

            if Message is None:
                raise Exception("Azure IoT Message class not available")
            message = Message(json.dumps(message_payload))
            message.content_encoding = "utf-8"
            message.content_type = "application/json"

            device_client.send_message(message)
            logger.info("Successfully sent message to IoT Hub")

        finally:

            device_client.disconnect()
        return {
            "status": "success",
            "message": "Heart rate data forwarded to IoT Hub",
            "heart_rate": data.heart_rate,
            "device_id": "xx-pius-test",
        }

    except Exception as e:
        logger.error(f"Error forwarding data to IoT Hub: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to forward to IoT Hub: {str(e)}",
            "heart_rate": data.heart_rate,
        }


@router.post("/webhook")
async def receive_azure_function_data(
    data: AzureFunctionData, db: Session = Depends(get_db)
):
    """
    Receive data from Azure Function (IoT Hub webhook)
    """
    try:
        logger.info(f"Received data from Azure Function: {data.device_id}")

        # fix this later, get user by device_id or email that
        #  the person provides from the frontend
        default_user_id = 1

        device = (
            db.query(IoTDevice)
            .filter(IoTDevice.device_id == data.device_id)
            .first()  # noqa
        )

        if not device:
            device = IoTDevice(
                user_id=default_user_id,
                device_id=data.device_id,
                device_type="smartwatch",
                device_name=f"Device {data.device_id}",
                manufacturer="Unknown",
                model="Unknown",
                connection_status="connected",
                last_sync=datetime.now(),
            )
            db.add(device)
            db.flush()

        vital_reading = VitalReading(
            device_id=device.id,
            user_id=default_user_id,
            heart_rate=data.heart_rate,
            blood_oxygen=None,
            is_emergency=False,
            timestamp=datetime.fromisoformat(
                data.timestamp.replace("Z", "+00:00")
            ),  # noqa
        )

        db.add(vital_reading)

        # Update device status
        db.query(IoTDevice).filter(IoTDevice.id == device.id).update(
            {
                IoTDevice.last_sync: datetime.now(),
                IoTDevice.connection_status: "connected",
            }
        )

        db.commit()
        db.refresh(vital_reading)

        return {
            "status": "success",
            "message": "Data received from Azure Function and stored",
            "reading_id": vital_reading.id,
            "device_id": data.device_id,
            "heart_rate": data.heart_rate,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error processing Azure Function data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process data: {str(e)}"
        )  # noqa


@router.get("/devices/{user_id}")
async def get_user_devices(user_id: int, db: Session = Depends(get_db)):
    """
    Get all IoT devices for a user
    """
    devices = db.query(IoTDevice).filter(IoTDevice.user_id == user_id).all()
    return {"devices": devices}


@router.get("/status")
async def iot_status():
    """
    Check IoT service status
    """
    return {"status": "IoT service is running"}
