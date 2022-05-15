from datetime import datetime
from enum import Enum
import io
import base64
from .models import User, PointLog

# returns current time as a string for logging
def current_time() -> str:
    return datetime.now().strftime("%m/%d/%y @ %H:%M:%S")

# simple case that returns probation status based on points
def get_status(points):
    if(points > 60):
        return {"style":"text-success","text":"GOOD"}
    elif(points > 40):
        return {"style":"text-warning","text":"NEAR PROBATION"}
    else:
        return {"style":"text-danger","text":"ON PROBATION"}

# just gets the points for a given User object
def get_points(user: User):
    return PointLog.objects(user=user).sum('points')

# given a uid, returns base64 encoding of image
def get_b64_img(uid):
    user = User.objects(uid=uid).first()
    if not user.profile_pic:
        # case: no picture saved
        return None
    bytes_im = io.BytesIO(user.profile_pic.read())
    # print(f'bytes_im {bytes_im}')
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image
