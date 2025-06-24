import os
from supabase import create_client, Client
from dotenv import load_dotenv
import mimetypes

# Загрузка переменных окружения из .env
load_dotenv()

SUPABASE_URL = "https://cvpvqxxbthdwyyxjbcqd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN2cHZxeHhidGhkd3l5eGpiY3FkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ5NTMyMTEsImV4cCI6MjA2MDUyOTIxMX0.yJoGeK7WdoDvUdCx6TSq6upu5dhAOq5aP8bfVmyXAco"

print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_KEY type:", type(SUPABASE_KEY))
print("SUPABASE_KEY length:", len(SUPABASE_KEY))

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase client created successfully")
except Exception as e:
    print("Error creating Supabase client:", str(e))
    exit(1)

BUCKET = "article-images"
LOCAL_DIR = "images"

def upload_to_supabase(filename):
    try:
        path = os.path.join(LOCAL_DIR, filename)
        print(f"Uploading {filename} from {path}")
        
        # Определяем MIME-тип файла
        mime_type, _ = mimetypes.guess_type(path)
        if not mime_type:
            mime_type = 'image/jpeg'  # По умолчанию для .jpg файлов
            
        # Читаем файл
        with open(path, "rb") as f:
            file_content = f.read()
            
        # Загружаем файл с правильными заголовками
        res = supabase.storage.from_(BUCKET).upload(
            filename,
            file_content,
            {
                "content-type": mime_type,
                "upsert": "true",
                "x-upsert": "true"
            }
        )
        
        # Проверяем успешность загрузки
        if res:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"
            print(f"{filename}: {public_url}")
            return public_url
        else:
            print(f"Ошибка загрузки {filename}")
            return None
    except Exception as e:
        print(f"Error uploading {filename}: {str(e)}")
        return None

if __name__ == "__main__":
    print("Starting upload process...")
    print("Local directory:", os.path.abspath(LOCAL_DIR))
    print("Files in directory:", os.listdir(LOCAL_DIR))
    
    uploaded_urls = {}
    for fname in os.listdir(LOCAL_DIR):
        if fname.lower().endswith(".jpg"):
            url = upload_to_supabase(fname)
            if url:
                uploaded_urls[fname] = url
    
    print("\nUploaded files and their URLs:")
    for filename, url in uploaded_urls.items():
        print(f"{filename}: {url}") 