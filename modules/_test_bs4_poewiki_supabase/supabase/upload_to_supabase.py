import os
from supabase import create_client, Client
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME', 'test-bucket')

def generate_image():
    # Generate a simple image using PIL
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def upload_image_to_supabase(image_data, image_name):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Try deleting the existing image first
    try:
        delete_response = supabase.storage.from_(BUCKET_NAME).remove([image_name])
        print(f"Deleted existing image: {delete_response}")
    except Exception as e:
        print(f"No existing image to delete or error deleting: {e}")
    
    # Upload the new image
    response = supabase.storage.from_(BUCKET_NAME).upload(image_name, image_data, {"content-type": "image/png"})
    return response

if __name__ == "__main__":
    image_data = generate_image()
    image_name = 'generated_image.png'
    response = upload_image_to_supabase(image_data, image_name)
    print(response)
