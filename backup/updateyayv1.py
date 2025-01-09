import os
import json
import re
import time
import vlc
from youtubesearchpython import VideosSearch
import yt_dlp
from rich.console import Console
from rich.text import Text
from rich.table import Table

# Initialize console for rich text
console = Console()
playlist_file = "playlists.json"
songs_directory = "songs"  # Directory to save downloaded songs

# Ensure songs directory exists
if not os.path.exists(songs_directory):
    os.makedirs(songs_directory)

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

def load_playlists():
    """Load playlists from a file."""
    if os.path.exists(playlist_file):
        with open(playlist_file, 'r') as file:
            return json.load(file)
    return {}

def save_playlists(playlists):
    """Save playlists to a file."""
    with open(playlist_file, 'w') as file:
        json.dump(playlists, file, indent=4)

def create_playlist(playlists):
    """Create a new playlist."""
    name = input("Enter the name of the new playlist: ").strip()
    if name in playlists:
        console.print("[red]Playlist already exists.[/red]")
        return
    playlists[name] = []
    save_playlists(playlists)
    console.print(f"[bold green]Playlist '{name}' created.[/bold green]")

def add_song_to_playlist(playlists):
    """Add a song to a playlist."""
    playlist_name = input("Enter the playlist name to add a song: ").strip()
    if playlist_name not in playlists:
        console.print("[red]Playlist not found.[/red]")
        return
    
    song_title = input("Enter the song title to add: ").strip()
    playlists[playlist_name].append(song_title)
    save_playlists(playlists)
    console.print(f"[bold green]Song added to playlist '{playlist_name}'.[/bold green]")

def list_playlists(playlists):
    """List all playlists and their songs."""
    if not playlists:
        console.print("[red]No playlists found.[/red]")
        return

    for playlist_name, songs in playlists.items():
        console.print(f"[bold cyan]{playlist_name}[/bold cyan]")
        if songs:
            for song in songs:
                console.print(f"  - {song}")
        else:
            console.print("  [dim]No songs in this playlist.[/dim]")

def list_songs():
    """List all downloaded songs."""
    songs = [f for f in os.listdir(songs_directory) if f.endswith('.mp3') or f.endswith('.wav')]
    if not songs:
        console.print("[red]No songs found.[/red]")
        return

    table = Table(title="Downloaded Songs", header_style="bold blue")
    table.add_column("No.", style="bold cyan")
    table.add_column("Title", style="bold magenta")
    for idx, song in enumerate(songs, 1):
        table.add_row(str(idx), song)

    console.print(table)

    return songs

def play_song(song_path):
    """Play a song using VLC."""
    player = vlc.MediaPlayer(song_path)
    player.play()
    while player.get_state() != vlc.State.Ended:
        time.sleep(1)
    player.release()

def play_playlist(playlists):
    """Play songs from a playlist one by one."""
    playlist_name = input("Enter the playlist name to play: ").strip()
    if playlist_name not in playlists:
        console.print("[red]Playlist not found.[/red]")
        return

    songs = playlists[playlist_name]
    for song in songs:
        song_path = os.path.join(songs_directory, song)
        if os.path.exists(song_path):
            console.print(f"[bold green]Playing {song}...[/bold green]")
            play_song(song_path)
        else:
            console.print(f"[red]Song '{song}' not found.[/red]")

def main():
    playlists = load_playlists()

    while True:
        clear_screen()  # Clear screen while keeping the banner
        display_banner()
        console.print("\n[bold green]Welcome to the YaYtube CLI[/bold green]")
        console.print("[cyan]1. Search for a song by name[/cyan]")
        console.print("[cyan]2. Search for songs by artist[/cyan]")
        console.print("[cyan]3. Paste a YouTube URL to download[/cyan]")
        console.print("[cyan]4. Create a new playlist[/cyan]")
        console.print("[cyan]5. Add a song to a playlist[/cyan]")
        console.print("[cyan]6. List all playlists[/cyan]")
        console.print("[cyan]7. List downloaded songs[/cyan]")
        console.print("[cyan]8. Play a song[/cyan]")
        console.print("[cyan]9. Play songs from a playlist[/cyan]")
        console.print("[cyan]10. Exit[/cyan]")
        
        choice = input("Enter your choice (1-10): ").strip()

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
            url = input("Enter the YouTube URL: ").strip()
            if url:
                print("Choose output format (mp3/mp4): ", end="")
                output_format = input().strip()
                if output_format not in ['mp3', 'mp4']:
                    console.print("[red]Invalid format.[/red]")
                    continue
                title = input("Enter the title for the downloaded song: ").strip()
                sanitized_title = re.sub(r'[\/:*?"<>|]', "", title)  # Remove invalid characters for filenames
                output_path = os.path.join(songs_directory, sanitized_title)  # Save in the songs directory

                if output_format == 'mp3':
                    quality = input("Choose audio quality (e.g., 128, 192, 320): ").strip()
                    download_video(url, f"{output_path}.mp3", format='bestaudio', quality=quality)
                elif output_format == 'mp4':
                    download_video(url, f"{output_path}.mp4", format='bestvideo+bestaudio')

                clear_screen()  # Clear screen after download but keep the banner
                console.print(f"[bold green]Download complete! File saved at {output_path}.{output_format}[/bold green]")

        elif choice == '4':
            create_playlist(playlists)

        elif choice == '5':
            add_song_to_playlist(playlists)

        elif choice == '6':
            list_playlists(playlists)

        elif choice == '7':
            songs = list_songs()

        elif choice == '8':
            songs = list_songs()
            if songs:
                song_choice = input("Enter the number of the song to play (or 'c' to cancel): ").strip()
                if song_choice.isdigit() and 1 <= int(song_choice) <= len(songs):
                    song_path = os.path.join(songs_directory, songs[int(song_choice) - 1])
                    console.print(f"[bold green]Playing {songs[int(song_choice) - 1]}...[/bold green]")
                    play_song(song_path)
                else:
                    console.print("[red]Invalid choice.[/red]")

        elif choice == '9':
            play_playlist(playlists)

        elif choice == '10':
            console.print("[bold red]Exiting...[/bold red]")
            break

        else:
            console.print("[red]Invalid choice. Please select a number between 1 and 10.[/red]")

if __name__ == "__main__":
    main()
