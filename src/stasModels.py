from pydantic import BaseModel


class TodayPics(BaseModel):
    count: int
    percentage_diseased: float
    percentage_diseased_after_mod: float
    mod_rate: int


class LatestPics(BaseModel):
    latest_date: str
    count: int
    percentage_diseased: float
    percentage_diseased_after_mod: float
    mod_rate: float


class LatestPicsModel(BaseModel):
    success: bool
    data: LatestPics

class TodayPicsModel(BaseModel):
    success: bool
    data: TodayPics


class DatePics(BaseModel):
    latest_date: str
    count: int
    percentage_diseased: float
    percentage_diseased_after_mod: float
    mod_rate: float
    EB_per: float
    LB_per: float
    

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


class NewImage(BaseModel):
    Image_Path: str
    Location: str
    Date: str
    Time: str
    Classification: list[int]
    Confidence: list[float]
    bbox: list[int]
    Image_Class: int
    Edited: int
    Treated: int
    Resized_Path: str
    Annotated_Path: str