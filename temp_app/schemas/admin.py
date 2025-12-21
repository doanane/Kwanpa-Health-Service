from pydantic import BaseModel, Field

class CreateDoctorRequest(BaseModel):
    doctor_id: str = Field(..., min_length=8, max_length=8, description="8-digit doctor ID")
    full_name: str = Field(..., description="Full name of the doctor")
    specialization: str = Field(..., description="Medical specialization")
    hospital: str = Field(..., description="Hospital name")
    initial_password: str = Field(..., min_length=6, description="Initial password for the doctor")

class CreateDoctorResponse(BaseModel):
    message: str
    doctor_id: str
    full_name: str
    specialization: str

class SuperUserAuth(BaseModel):
    superuser_password: str = Field(..., description="Superuser password")