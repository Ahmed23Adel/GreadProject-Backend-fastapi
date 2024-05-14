from pydantic import BaseModel


class TodayPics(BaseModel):
    count: int
    percentage_diseased: float
    percentage_diseased_after_mod: float
    mod_rate: int

class TodayPicsModel(BaseModel):
    success: bool
    data: TodayPics


class DatePics(BaseModel):
    count: int
    percentage_diseased: float
    percentage_diseased_after_mod: float
    mod_rate: int
    EB_per: int
    LB_per: int

class DatePicsModel(BaseModel):
    success: bool
    data: DatePics

class DiseaseMonsPercentageResponse(BaseModel):
    mons: list[str]
    EB: list[int]
    LB: list[int]
    
class DiseaseMonsPercentageModel(BaseModel):
    success: bool
    data: DiseaseMonsPercentageResponse


class LocationHistory(BaseModel):
    itemImageSrc: str
    thumbnailImageSrc: str
    alt: str
    title: str
    treatment: str
    

class LocationHistoryList(BaseModel):
    allHistory: list[LocationHistory]

class LocationHistoryModel(BaseModel):
    success: bool
    data: LocationHistoryList


class DatePerDiseasedPlants(BaseModel):
    dates: list[str]
    percentages: list[int]

class DatePerDiseasedPlantsResponse(BaseModel):
    success: bool
    data: DatePerDiseasedPlants



class LocationsResponse(BaseModel):
    locations: list[str]

class DataResponseLocations(BaseModel):
    success: bool
    data: LocationsResponse


class DiseasesResponse(BaseModel):
    diseases: list[str]
    percentages: list[int]

class DataResponseStatistics(BaseModel):
    success: bool
    data: DiseasesResponse