import os
from youtubesearchpython import VideosSearch
import yt_dlp
from rich.console import Console
from rich.text import Text
from rich.table import Table
import time
import re

# Initialize console for rich text
console = Console()

def display_banner():
    """Display an ASCII art banner."""
    banner = """
██╗   ██╗ █████╗ ██╗   ██╗████████╗██╗   ██╗██████╗ ███████╗
╚██╗ ██╔╝██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║   ██║██╔══██╗██╔════╝
 ╚████╔╝ ███████║ ╚████╔╝    ██║   ██║   ██║██████╔╝█████╗  
  ╚██╔╝  ██╔══██║  ╚██╔╝     ██║   ██║   ██║██╔══██╗██╔══╝  
   ██║   ██║  ██║   ██║      ██║   ╚██████╔╝██████╔╝███████╗
   ╚═╝   ╚═╝  ╚═╝   ╚═╝      ╚═╝    ╚═════╝ ╚═════╝ ╚══════╝                                                       
    """
    console.print(Text.from_markup(banner, style="bold beige"))

def search_youtube(query, max_results=5):
    """Search for videos on YouTube."""
    search = VideosSearch(query, limit=max_results)
    results = search.result()['result']
    videos = [(video['title'], video['link'], video['publishedTime'], video['duration']) for video in results]
    return videos

def download_video(url, output_path, format='bestaudio', quality=None):
    """Download video or audio from YouTube."""
    ydl_opts = {
        'format': format,
        'outtmpl': output_path,
        'postprocessors': []
    }

    if format == 'bestaudio' and quality:
        ydl_opts['format'] = f'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best'
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def format_search_results(videos):
    """Format search results into a table."""
    table = Table(title="Search Results", header_style="bold blue")
    table.add_column("No.", style="bold cyan")
    table.add_column("Title", style="bold magenta")
    table.add_column("URL", style="dim")
    table.add_column("Published Time", style="italic")
    table.add_column("Duration", style="italic")
    
    for idx, (title, url, published_time, duration) in enumerate(videos, 1):
        table.add_row(str(idx), title, url, published_time, duration)

    return table

def clear_screen():
    """Clear the terminal screen."""
    time.sleep(2)
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    
    while True:
        clear_screen()  # Clear screen while keeping the banner
        display_banner()
        console.print("\n[bold green]Welcome to the YaYtube CLI[/bold green]")
        console.print("[cyan]1. Search for a song by name[/cyan]")
        console.print("[cyan]2. Search for songs by artist[/cyan]")
        console.print("[cyan]3. Paste a YouTube URL to download[/cyan]")
        console.print("[cyan]4. Exit[/cyan]")
        
        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            query = input("Enter the song name: ").strip()
            start_time = time.time()
            videos = search_youtube(query)
            runtime = time.time() - start_time
            if videos:
                console.print(format_search_results(videos))
                console.print(f"\n[bold green]Search completed in {runtime:.2f} seconds.[/bold green]")
                video_choice = input("\nEnter the number of the video to download (or 'c' to cancel): ").strip()
                if video_choice.isdigit() and 1 <= int(video_choice) <= len(videos):
                    title, url, _, _ = videos[int(video_choice) - 1]
                else:
                    continue
            else:
                console.print("[red]No results found.[/red]")
                continue

        elif choice == '2':
            artist_name = input("Enter the artist name: ").strip()
            start_time = time.time()
            videos = search_youtube(artist_name)
            runtime = time.time() - start_time
            if videos:
                console.print(format_search_results(videos))
                console.print(f"\n[bold green]Search completed in {runtime:.2f} seconds.[/bold green]")
                video_choice = input("\nEnter the number of the video to download (or 'c' to cancel): ").strip()
                if video_choice.isdigit() and 1 <= int(video_choice) <= len(videos):
                    title, url, _, _ = videos[int(video_choice) - 1]
                else:
                    continue
            else:
                console.print("[red]No results found.[/red]")
                continue

        elif choice == '3':
            url = input("Paste the YouTube URL: ").strip()
            # Get the video title from the URL
            video_info = search_youtube(url.split('/')[-1], max_results=1)  # Search for the video title
            if video_info:
                title = video_info[0][0]  # Get the title of the first result
            else:
                console.print("[red]Could not retrieve video title. Please try again.[/red]")
                continue
        elif choice == '4':
            console.print("[bold yellow]Goodbye![/bold yellow]")
            break
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")
            continue

        output_format = input("Choose output format (mp3/mp4): ").strip().lower()
        # Use the title of the video as the default output file name
        sanitized_title = re.sub(r'[\/:*?"<>|]', "", title)  # Remove invalid characters for filenames
        output_path = os.path.join(os.getcwd(), sanitized_title)  # Save in the current directory

        if output_format == 'mp3':
            quality = input("Choose audio quality (e.g., 128, 192, 320): ").strip()
            download_video(url, f"{output_path}.mp3", format='bestaudio', quality=quality)
        elif output_format == 'mp4':
            download_video(url, f"{output_path}.mp4", format='bestvideo+bestaudio')

        clear_screen()  # Clear screen after download but keep the banner
        console.print(f"[bold green]Download complete! File saved at {output_path}.{output_format}[/bold green]")

if __name__ == "__main__":
    main()
