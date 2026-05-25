from pydantic import BaseModel, Field

# Pydantic data validation layer isolated from core routing logic
class TripPayload(BaseModel):
    driver_id: int = Field(..., description="Unique database identifier for the operator")
    distance_km: float = Field(..., gt=0, description="Total trip distance must be greater than zero")
    traffic_density: float = Field(..., ge=0, le=1, description="Traffic density coefficient bounded between 0 and 1")