import os
import json
from youtubesearchpython import VideosSearch
import yt_dlp
from tqdm import tqdm

CONFIG_FILE = "config.json"

DEFAULT_SETTINGS = {
    "audio_format": "mp3",
    "audio_quality": "192",  # 192kbps as a medium quality for audio
    "video_format": "mp4",
    "video_quality": "best",  # 'best' for the highest quality available
    "default_download_path": os.getcwd(),  # Default to the current working directory
}

AUDIO_FORMAT_OPTIONS = ['mp3', 'wav', 'aac', 'flac']
AUDIO_QUALITY_OPTIONS = ['128', '192', '256', '320']
VIDEO_FORMAT_OPTIONS = ['mp4', 'mkv', 'avi', 'mov']
VIDEO_QUALITY_OPTIONS = ['lowest', 'low', 'medium', 'high', 'best']

def load_settings():
    """Load settings from a config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            settings = json.load(file)
            # Merge the loaded settings with DEFAULT_SETTINGS to ensure all keys are present
            merged_settings = {**DEFAULT_SETTINGS, **settings}
            return merged_settings
    return DEFAULT_SETTINGS

def save_settings(settings):
    """Save settings to a config file."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(settings, file, indent=4)

def update_settings(settings):
    """Update settings interactively with predefined options."""
    print("\nCurrent Settings:")
    for key, value in settings.items():
        print(f"{key}: {value}")
    
    print("\nUpdate Settings:")

    print("Select audio format:")
    for idx, option in enumerate(AUDIO_FORMAT_OPTIONS):
        print(f"{idx + 1}. {option}")
    audio_format_choice = input(f"Enter your choice (1-{len(AUDIO_FORMAT_OPTIONS)}) or press Enter to keep '{settings['audio_format']}': ").strip()
    if audio_format_choice.isdigit() and 1 <= int(audio_format_choice) <= len(AUDIO_FORMAT_OPTIONS):
        settings["audio_format"] = AUDIO_FORMAT_OPTIONS[int(audio_format_choice) - 1]
    
    print("Select audio quality:")
    for idx, option in enumerate(AUDIO_QUALITY_OPTIONS):
        print(f"{idx + 1}. {option}kbps")
    audio_quality_choice = input(f"Enter your choice (1-{len(AUDIO_QUALITY_OPTIONS)}) or press Enter to keep '{settings['audio_quality']}': ").strip()
    if audio_quality_choice.isdigit() and 1 <= int(audio_quality_choice) <= len(AUDIO_QUALITY_OPTIONS):
        settings["audio_quality"] = AUDIO_QUALITY_OPTIONS[int(audio_quality_choice) - 1]
    
    print("Select video format:")
    for idx, option in enumerate(VIDEO_FORMAT_OPTIONS):
        print(f"{idx + 1}. {option}")
    video_format_choice = input(f"Enter your choice (1-{len(VIDEO_FORMAT_OPTIONS)}) or press Enter to keep '{settings['video_format']}': ").strip()
    if video_format_choice.isdigit() and 1 <= int(video_format_choice) <= len(VIDEO_FORMAT_OPTIONS):
        settings["video_format"] = VIDEO_FORMAT_OPTIONS[int(video_format_choice) - 1]
    
    print("Select video quality:")
    for idx, option in enumerate(VIDEO_QUALITY_OPTIONS):
        print(f"{idx + 1}. {option}")
    video_quality_choice = input(f"Enter your choice (1-{len(VIDEO_QUALITY_OPTIONS)}) or press Enter to keep '{settings['video_quality']}': ").strip()
    if video_quality_choice.isdigit() and 1 <= int(video_quality_choice) <= len(VIDEO_QUALITY_OPTIONS):
        settings["video_quality"] = VIDEO_QUALITY_OPTIONS[int(video_quality_choice) - 1]
    
    default_download_path = input(f"Enter default download path (default: {settings['default_download_path']}): ").strip()
    if default_download_path:
        settings["default_download_path"] = default_download_path
    
    save_settings(settings)
    print("\nSettings updated successfully.")

def search_youtube(query, max_results=5):
    """Search for videos on YouTube."""
    search = VideosSearch(query, limit=max_results)
    results = search.result()['result']
    videos = [(video['title'], video['link']) for video in results]
    return videos

def download_video(url, output_path, settings, format='bestaudio', quality=None):
    """Download video or audio from YouTube."""
    ydl_opts = {
        'format': format,
        'outtmpl': f'{output_path}.%(ext)s',
        'postprocessors': []
    }

    if format == 'bestaudio':
        ydl_opts['format'] = f'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best'
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': settings['audio_format'],
            'preferredquality': quality,
        })
    elif format == 'mp4':
        ydl_opts['format'] = 'bestvideo+bestaudio/best'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def display_progress_bar(iterable, desc="Processing"):
    """Display a progress bar using tqdm."""
    return tqdm(iterable, desc=desc)

def main():
    settings = load_settings()

    while True:
        print("\nWelcome to the YouTube Downloader CLI")
        print("1. Search and Download Audio (mp3)")
        print("2. Search and Download Video (mp4)")
        print("3. Settings")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()

        if choice in ['1', '2']:
            query = input("Enter the search term (song or artist name): ").strip()
            videos = search_youtube(query)
            if videos:
                print("\nSearch Results:")
                for idx, (title, url) in enumerate(videos, 1):
                    print(f"{idx}. {title} - {url}")
                video_choice = input("\nEnter the number of the video to download (or 'c' to cancel): ").strip()
                if video_choice.isdigit() and 1 <= int(video_choice) <= len(videos):
                    _, url = videos[int(video_choice) - 1]
                else:
                    continue
            else:
                print("No results found.")
                continue

            output_name = input("Enter the output file name (without extension): ").strip()
            output_path = os.path.join(settings['default_download_path'], output_name)

            if choice == '1':  # Download Audio (mp3)
                download_video(url, output_path, settings, format='bestaudio', quality=settings['audio_quality'])
                print(f"Audio download complete! File saved at {output_path}.{settings['audio_format']}")
            
            elif choice == '2':  # Download Video (mp4)
                download_video(url, output_path, settings, format='mp4', quality=settings['video_quality'])
                print(f"Video download complete! File saved at {output_path}.mp4")

        elif choice == '3':
            update_settings(settings)
        
        elif choice == '4':
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
