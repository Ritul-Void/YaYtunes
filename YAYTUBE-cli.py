import os
from youtubesearchpython import VideosSearch
import yt_dlp
from rich.console import Console
from rich.text import Text
from rich.table import Table
import time
import re
import vlc  # For audio playback

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

def list_downloaded_songs():
    """List downloaded songs in a tabular form."""
    songs = [f for f in os.listdir() if f.endswith('.mp3') or f.endswith('.mp4')]
    table = Table(title="Downloaded Songs", header_style="bold blue")
    table.add_column("No.", style="bold cyan")
    table.add_column("Title", style="bold magenta")
    
    for idx, song in enumerate(songs, 1):
        table.add_row(str(idx), song)

    return table

def play_song(file_path):
    """Play a song using VLC."""
    player = vlc.MediaPlayer(file_path)
    player.play()
    return player
def clear_screen():
    """Clear the terminal screen."""
    time.sleep(2)
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    player = None

    while True:
        clear_screen()  # Clear screen while keeping the banner
        display_banner()
        console.print("\n[bold green]Welcome to the YaYtube CLI[/bold green]")
        console.print("[cyan]1. Search for a song by name[/cyan]")
        console.print("[cyan]2. Search for songs by artist[/cyan]")
        console.print("[cyan]3. Paste a YouTube URL to download[/cyan]")
        console.print("[cyan]4. List downloaded songs[/cyan]")
        console.print("[cyan]5. Exit[/cyan]")
        
        choice = input("Enter your choice (1-5): ").strip()

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
            video_info = search_youtube(url.split('/')[-1], max_results=1)
            if video_info:
                title = video_info[0][0]
            else:
                console.print("[red]Could not retrieve video title. Please try again.[/red]")
                continue
        elif choice == '4':
            clear_screen()
            display_banner()
            console.print("[bold green]List of Downloaded Songs:[/bold green]")
            console.print(list_downloaded_songs())
            song_choice = input("Enter the number of the song to play (or 'c' to cancel): ").strip()
            if song_choice.isdigit() and 1 <= int(song_choice):
                songs = [f for f in os.listdir() if f.endswith('.mp3') or f.endswith('.mp4')]
                song_file = songs[int(song_choice) - 1]
                if player:
                    player.stop()
                player = play_song(song_file)
                console.print("[bold yellow]Playing... Press 'p' to pause, 'r' to resume, 'n' to move to the next song, or 'q' to quit.[/bold yellow]")
                while True:
                    control = input("Enter your choice (p/r/n/q): ").strip().lower()
                    if control == 'p':
                        player.pause()
                        console.print("[bold yellow]Paused. Press 'r' to resume, 'n' to move to the next song, or 'q' to quit.[/bold yellow]")
                    elif control == 'r':
                        player.play()
                        console.print("[bold yellow]Resumed. Press 'p' to pause, 'n' to move to the next song, or 'q' to quit.[/bold yellow]")
                    elif control == 'n':
                        player.stop()
                        break
                    elif control == 'q':
                        player.stop()
                        break
                    else:
                        console.print("[red]Invalid option. Please try again.[/red]")
            continue

        elif choice == '5':
            console.print("[bold yellow]Goodbye![/bold yellow]")
            break
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")
            continue

        output_format = input("Choose output format (mp3/mp4): ").strip().lower()
        sanitized_title = re.sub(r'[\/:*?"<>|]', "", title)
        output_path = os.path.join(os.getcwd(), sanitized_title)

        if output_format == 'mp3':
            quality = input("Choose audio quality (e.g., 128, 192, 320): ").strip()
            download_video(url, f"{output_path}.mp3", format='bestaudio', quality=quality)
        elif output_format == 'mp4':
            download_video(url, f"{output_path}.mp4", format='bestvideo+bestaudio')

        clear_screen()
        console.print(f"[bold green]Download complete! File saved at {output_path}.{output_format}[/bold green]")

if __name__ == "__main__":
    main()
