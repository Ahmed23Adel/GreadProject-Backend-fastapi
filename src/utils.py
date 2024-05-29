from datetime import datetime, timedelta
from fastapi import Query
from datetime import date, datetime
from fastapi import status, HTTPException, Depends
import re

def parse_date_from(from_date: str = Query(...)) -> date:
    try:
        parsed_date = datetime.strptime(from_date, "%d-%m-%Y").date()
    except ValueError:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Please provide the date in d-m-Y format."
        )
    return parsed_date

def parse_date_to(to_date: str = Query(...)) -> date:
    try:
        parsed_date = datetime.strptime(to_date, "%d-%m-%Y").date()
    except ValueError:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Please provide the date in d-m-Y format."
        )
    return parsed_date


def transform(url):
    regex = r'\/d\/(.*?)\/view'
    match = re.search(regex, url)

    if match:
        image_id = match.group(1)
        url = f'https://drive.google.com/uc?id={image_id}&export=download'

    url = url.replace("&export=download", "")
    url = url.replace("google", "lienuc")

    return url