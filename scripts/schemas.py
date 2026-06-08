from pydantic import BaseModel, Field

class TripPayload(BaseModel):
    # Hard operational constraints written directly into the data model layer
    driver_id: int = Field(
        ..., 
        gt=0, 
        description="Must be a valid positive non-zero system Driver Identifier"
    )
    
    distance_km: float = Field(
        ..., 
        gt=0.0, 
        le=5000.0, 
        description="Trip boundaries must scale between 0.1 and 5000.0 Kilometers"
    )
    
    traffic_density: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Traffic density factor metrics must scale strictly between 0.0 and 1.0"
    )

    class Config:
        schema_extra = {
            "example": {
                "driver_id": 1,
                "distance_km": 45.2,
                "traffic_density": 0.6
            }
        }