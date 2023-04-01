import pathlib

dataset_path = "./drive/MyDrive/tea sickness model5/"
dataset_dir = pathlib.Path(dataset_path)

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
import matplotlib.pyplot as plt
import cv2

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = tf.keras.models.load_model(dataset_path)

CLASS_NAMES = ['Anthracnose','algal leaf','bird eye spot','brown blight','gray light','healthy','red leaf spot','white spot']

@app.get("/ping")
async def ping():
    return "Hello, I am alive"

def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image


def fertlizers_to_disease(argument):
  print("fertlizers_to_disease function called")
  data = {
    "brand_name": "",
    "description":"Please meet knowledgeble person for this desease"
}
  description = "Spray copper fungicides(peranox) once every 7-10 days @220-420g or systemic fungicides once every 10-14 days @85ml, depending on the plucking round, in 170L of water per hectare, using knapsack sprayers or in 30-45 L per hectare using mist-blowers. Spraying should be done on the following plucking, always maintaining Pre Harvest Interval(PHI) of seven days in order to remain within Maximum Residue limits(MRL) set by tea importing/consuming countries."
  if argument == "brown blight":
    print(data)
    data["brand_name"] = "Peranox"
    data["description"]= description
    return data
  elif argument == "gray light":
    data["brand_name"] = "Peranox"
    data["description"]=description
    return data
  elif argument == "healthy":
    data["brand_name"] = "N/A"
    data["description"]="There is no any disease Found"
    return data
  else:
    return data
  

@app.post("/predict")
async def predict(
    file: UploadFile = File(...)
):
    image = read_file_as_image(await file.read())
    img = cv2.resize(image, dsize = (256, 256))
    img_batch = np.expand_dims(img,0)
    

    print("predict function called")
    print(img_batch.shape)
    try:
      predictions = MODEL.predict(img_batch)
      print("Model Called")
    except:
      print("An exception occurred")
      error = {
    "brand_name": "N/A",
    "description":"N/A"
      }
      return {
        'class': "Not a Tea Leave",
        'confidence': float(100),
        'management': error
       }
    
    print(predictions)
    print(np.argmax(predictions[0]))
    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    confidence = np.max(predictions[0])
    disease = fertlizers_to_disease(predicted_class)
    print(confidence)
    print("Function Called Succesfully")
    return {
        'class': predicted_class,
        'confidence': float(confidence),
        "management": disease
    }

import nest_asyncio
from pyngrok import ngrok
import uvicorn

ngrok_tunnel = ngrok.connect(8000)
print('Public URL:', ngrok_tunnel.public_url)
nest_asyncio.apply()
uvicorn.run(app, port=8000)
