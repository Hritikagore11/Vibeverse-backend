import os 
import random
import pygame
import sqlite3

class MusicPlayer:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        pygame.init()
        pygame.mixer.init()

    def play_music_for_emotion(self, emotion):
        self.cursor.execute("SELECT filepath FROM mood_music_map WHERE mood=?", (emotion,))
        results = self.cursor.fetchall()

        if not results:
            print(f"⚠️ No music found for emotion: {emotion}")
            return

        print(f"\n🎵 Songs available for emotion '{emotion}':")
        for idx, res in enumerate(results):
            print(f"{idx + 1}. {os.path.basename(res[0])}")

        selection = input("\nEnter song number to play or type 'all' to play entire playlist: ").strip().lower()

        if selection == 'all':
            shuffle_choice = input("Shuffle songs? (y/n): ").strip().lower()
            playlist = results.copy()
            if shuffle_choice == 'y':
                random.shuffle(playlist)
        else:
            try:
                index = int(selection) - 1
                playlist = [results[index]]
            except:
                print("Invalid selection. Playing first song by default.")
                playlist = [results[0]]

        index = 0
        while index < len(playlist):
            music_path = playlist[index][0]
            if not os.path.exists(music_path):
                print(f"⚠️ File not found: {music_path}")
                index += 1
                continue

            song_name = os.path.basename(music_path)
            print(f"\n🎶 Now playing: {song_name}")
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play()
            paused = False

            while True:
                if not pygame.mixer.music.get_busy() and not paused:
                    break
                cmd = input("\nType 'pause', 'resume', 'next', 'replay' or 'stop': ").strip().lower()

                if cmd == 'pause':
                    pygame.mixer.music.pause()
                    paused = True

                elif cmd == 'resume':
                    pygame.mixer.music.unpause()
                    paused = False

                elif cmd == 'replay':
                    pygame.mixer.music.stop()
                    pygame.mixer.music.play()
                    paused = False
                    print(f"🔁 Replaying: {song_name}")

                elif cmd == 'next':
                    pygame.mixer.music.stop()
                    paused = False
                    index += 1
                    break

                elif cmd == 'stop':
                    pygame.mixer.music.stop()
                    return

            index += 1

    def get_songs_by_mood(self, mood):
        self.cursor.execute("SELECT title, artist, preview_url FROM mood_music_map WHERE mood=?", (mood,))
        results = self.cursor.fetchall()
        songs = []
        for row in results:
            songs.append({
                "title": row[0],
                "artist": row[1],
                "preview_url": row[2]
            })
        return songs
