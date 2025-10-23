from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserAccount
from django.contrib.auth import logout
from django.http import FileResponse, HttpResponse
import yt_dlp
import os


def index(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password == password2:
            if UserAccount.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
            elif UserAccount.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
            else:
                user = UserAccount.objects.create(username=username, email=email, password=password)
                user.save()
                messages.success(request, "Account created successfully")
                return redirect("user") 
        else:
            messages.error(request, "Passwords do not match")
    
    return render(request, "index.html")

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if UserAccount.objects.filter(username=username, password=password).exists():
            return redirect("user")   # if success go to home
        else:
            messages.error(request, "Invalid username or password")

    return render(request,"login.html")

def profile(request):
    return render(request, "profile.html")

def view_logout(request):
    logout(request)
    return redirect("index")

def user(request):
    return render(request, "user.html", {"user": request.user})

def test(request):
    return render(request, "test.html")



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOAD_PATH = os.path.join(BASE_DIR, "downloads")

if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)


def download_video(request):
    if request.method == 'POST':
        url = request.POST.get('yt-url')
        quality = request.POST.get('qualities')

        if not url:
            return HttpResponse("Please provide a YouTube URL.", status=400)

        final_filepath = None # This will store the actual path to the downloaded/converted file

        try:
            if quality == 'audio':
                options = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(DOWNLOAD_PATH, '%(id)s_temp_audio.%(ext)s'),
                    'ignoreerrors': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'quiet': True,
                    'no_warnings': True,
                }
            else:
                options = {
                    'format': f'bestvideo[height<={quality}]+bestaudio/best', # ensure best audio is included
                    'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
                    'merge_output_format': 'mp4', # This will ensure final file is mp4
                    'ignoreerrors': True,
                    'quiet': True,
                    'no_warnings': True,
                }

            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)

                if quality == 'audio':
                    if 'requested_downloads' in info and info['requested_downloads']:
                        final_filepath = info['requested_downloads'][0]['filepath']
                    else:
                        video_title = info.get('title', 'unknown_audio').replace('/', '_').replace('\\', '_')
                        final_filepath = os.path.join(DOWNLOAD_PATH, f"{video_title}.mp3")
                        if not os.path.exists(final_filepath):
                            raise Exception("Could not determine final audio filename.")
                else:
                    final_filepath = ydl.prepare_filename(info)
                    if not final_filepath.endswith('.mp4'):
                        final_filepath = os.path.splitext(final_filepath)[0] + '.mp4'


            if not final_filepath or not os.path.exists(final_filepath):
                raise Exception("Downloaded file not found or path incorrect.")

            response = FileResponse(open(final_filepath, 'rb'), as_attachment=True)
            if quality == 'audio':
                response['Content-Type'] = 'audio/mpeg' # Explicitly set for audio
            else:
                response['Content-Type'] = 'video/mp4' # Explicitly set for video (or let Django guess)
            response.close = lambda: os.remove(final_filepath)
            filedelete(folder_path=DOWNLOAD_PATH)  # Call file deletion after preparing response
            return response

        except yt_dlp.utils.DownloadError as e:
            return HttpResponse(f"Download Error: {e}", status=400)
        except Exception as e:
            return HttpResponse(f"An unexpected error occurred: {e}", status=500)

    return HttpResponse("Invalid request.", status=400) # Return 400 for GET requests to this POST-only view

# folder_path = r"E:\My Work\python\Python2748.py\Yt_app Django\yt_app\downloads"

def filedelete(folder_path=DOWNLOAD_PATH):
    pass
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]

    max_files = len(files)  # Default to current number of files

    if max_files > 1:
        files_to_delete = files[:len(files)]
        for file in files_to_delete:
            try:
                os.remove(file)
                print(f"Deleted: {os.path.basename(file)}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")
        
    return "File Deletion Check Complete"
