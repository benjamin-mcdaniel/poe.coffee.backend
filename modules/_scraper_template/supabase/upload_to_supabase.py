import os
from supabase import create_client, Client
from PIL import Image
import io

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME', 'test-bucket')

def create_image():
    # Generate a simple image
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def upload_image_to_supabase(image_data, file_name):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.storage.from_(BUCKET_NAME).upload(file_name, image_data)
    return response

def main():
    image_data = create_image()
    response = upload_image_to_supabase(image_data, 'test_image.png')
    print(response)

if __name__ == '__main__':
    main()
