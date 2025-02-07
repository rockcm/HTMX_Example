from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import csv


app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Define the data model for a Skin
class Skin(BaseModel):
    Id: int
    Name: str
    Description: str
    WeaponName: str
    RarityName: str
    PictureUrl: str

class SkinUpdate(BaseModel):
    Id : Optional[int]
    Name: Optional[str]
    Description: Optional[str]
    WeaponName: Optional[str]
    RarityName: Optional[str]
    PictureUrl: Optional[str]

# Read the data from the CSV file into a list of Skin objects
def read_csv(file_path):
    skin_list = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            skin = Skin(**row)
            skin_list.append(skin)
    return skin_list

# Get all skins
@app.get("/skins/", response_model=List[Skin])
async def get_all_skins():
    return read_csv("CSGOSkins2.csv")

# Get a specific skin by ID
@app.get("/skins/{skin_id}", response_model=Skin)
async def get_skin_by_id(skin_id: int):
    skins = read_csv("CSGOSkins2.csv")
    for skin in skins:
        if skin.id == skin_id:
            return skin
    raise HTTPException(status_code=404, detail="Skin not found")

# Create a new skin
@app.post("/skins/", response_model=Skin)
async def create_skin(skin: Skin):
    skins = read_csv("CSGOSkins2.csv")
    

    # Append the new skin to the list
    skins.append(skin)

    # Write the updated list back to the CSV file
    with open("CSGOSkins2.csv", mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Id", "Name", "Description", "WeaponName", "RarityName", "PictureUrl"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(skin.dict() for skin in skins)

    return skin

def write_csv(file_path, skins):
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Id", "Name", "Description", "WeaponName", "RarityName", "PictureUrl"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(skin.dict() for skin in skins)

        
@app.delete("/skins/{skin_id}", response_model=Skin)
async def delete_skin(skin_id: int):
    skins = read_csv("CSGOSkins2.csv")
    
    # Find and remove the skin with the specified ID
    deleted_skin = None
    for skin in skins:
        if skin.Id == skin_id:
            deleted_skin = skin
            skins.remove(skin)
            break

    # Write the updated list back to the CSV file
    write_csv("CSGOSkins2.csv", skins)

    if deleted_skin:
        return deleted_skin
    else:
        raise HTTPException(status_code=404, detail="Skin not found")
    

# Update a skin by ID
@app.put("/skins/{skin_id}", response_model=Skin)
async def update_skin(skin_id: int, updated_skin: Skin):
    skins = read_csv("CSGOSkins2.csv")

    # Find the skin to update
    for i, skin in enumerate(skins):
        if skin.Id == skin_id:
            skins[i] = updated_skin
            break

    # Write the updated list back to the CSV file
    write_csv("CSGOSkins2.csv", skins)

    return updated_skin


# User Skins code 
@app.get("/user-skins/", response_model=List[Skin])
async def get_user_skins():
    user_skins = read_csv("UserSkins.csv")
    return user_skins


@app.post("/user-skins/", response_model=Skin)
async def add_user_skin(skin: Skin):
    print(skin)  # Add this line to print the received payload
    try:
        # Read existing user skins
        user_skins = read_csv("UserSkins.csv")

        # Generate a new unique ID for the user skin
        new_id = max([s.Id for s in user_skins], default=0) + 1
        skin.Id = new_id

        # Append the new skin to the list
        user_skins.append(skin)

        # Write the updated list back to the CSV file
        write_csv("UserSkins.csv", user_skins)

        return skin
    except Exception as e:
        # Handle exceptions and return an appropriate HTTP response
        raise HTTPException(status_code=500, detail=str(e))
    

# Endpoint to delete a user-added skin
@app.delete("/skins/{skin_id}", response_model=Skin)
async def delete_skin(skin_id: int):
    skins = read_csv("CSGOSkins2.csv")
    
    # Find and remove the skin with the specified ID
    deleted_skin = None
    for skin in skins:
        if skin.Id == skin_id:
            deleted_skin = skin
            skins.remove(skin)
            break

    # Write the updated list back to the CSV file
    write_csv("CSGOSkins2.csv", skins)

    if deleted_skin:
        return deleted_skin
    else:
        raise HTTPException(status_code=404, detail="Skin not found")
    

# Endpoint to update a user-added skin
@app.put("/user-skins/{skin_id}", response_model=Skin)
async def update_user_skin(skin_id: int, updated_skin: SkinUpdate):
    user_skins = read_csv("UserSkins.csv")
    updated_skin_dict = updated_skin.dict()
    for skin in user_skins:
        if skin.Id == skin_id:
            for key, value in updated_skin_dict.items():
                setattr(skin, key, value)
            break
    write_csv("UserSkins.csv", user_skins)
    return updated_skin

# Update the get_skin_by_id endpoint for UserSkins.csv
@app.get("/user-skins/{skin_id}", response_model=Skin)
async def get_user_skin_by_id(skin_id: int):
    user_skins = read_csv("UserSkins.csv")
    for user_skin in user_skins:
        if user_skin.Id == skin_id:  
            return user_skin
    raise HTTPException(status_code=404, detail="User Skin not found")

@app.delete("/user-skins/{skin_id}", response_model=Skin)
async def delete_user_skin(skin_id: int):
    user_skins = read_csv("UserSkins.csv")

    # Find and remove the user-added skin with the specified ID
    deleted_user_skin = None
    for user_skin in user_skins:
        if user_skin.Id == skin_id:
            deleted_user_skin = user_skin
            user_skins.remove(user_skin)
            break

    # Write the updated list back to the CSV file
    write_csv("UserSkins.csv", user_skins)

    if deleted_user_skin:
        return deleted_user_skin
    else:
        raise HTTPException(status_code=404, detail="User-added Skin not found")
    
class UserProfile(BaseModel):
    UserId: int
    Username: str
    Email: str

# Read the data from the CSV file into a list of UserProfile objects
def read_user_profiles(file_path):
    user_profiles = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert keys to strings
            row = {str(key): value for key, value in row.items()}
            user_profile = UserProfile(**row)
            user_profiles.append(user_profile)
    return user_profiles

# Get all user profiles
@app.get("/user-profiles/", response_model=List[UserProfile])
async def get_user_profiles():
    return read_user_profiles("UserProfiles.csv")

@app.get("/user-profiles/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: int):
    user_profiles = read_user_profiles("UserProfiles.csv")
    for user_profile in user_profiles:
        if user_profile.UserId == user_id:
            return user_profile
    raise HTTPException(status_code=404, detail="User profile not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=80)

