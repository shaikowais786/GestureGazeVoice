import os
import sys
import subprocess

def run_voice():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    voice_dir = os.path.join(base_dir, "GestureGaze_Voice")
    voice_script = "main.py"
    voice_path = os.path.join(voice_dir, voice_script)
    
    if not os.path.exists(voice_path):
        print(f"\n[Error] Voice entry point not found at: {voice_path}")
        return

    print("\n" + "=" * 50)
    print("Starting Smart Voice Mode...")
    print("Press Ctrl+C to stop Smart Voice Mode and return to Launcher.")
    print("=" * 50 + "\n")
    
    try:
        # Launch main.py with the current Python executable inside the GestureGaze_Voice directory
        subprocess.run([sys.executable, voice_script], cwd=voice_dir)
    except KeyboardInterrupt:
        print("\n[Info] Smart Voice Mode interrupted.")
    except Exception as e:
        print(f"\n[Error] Failed to run Smart Voice Mode: {e}")

def run_cursor():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cursor_dir = os.path.join(base_dir, "Smart_Cursor")
    cursor_script = "app.py"
    cursor_path = os.path.join(cursor_dir, cursor_script)
    
    if not os.path.exists(cursor_path):
        print(f"\n[Error] Smart Cursor entry point not found at: {cursor_path}")
        return

    print("\n" + "=" * 50)
    print("Starting Smart Cursor Mode...")
    print("Press Ctrl+C to stop Smart Cursor Mode and return to Launcher.")
    print("=" * 50 + "\n")
    
    try:
        # Launch app.py with the current Python executable inside the Smart_Cursor directory
        subprocess.run([sys.executable, cursor_script], cwd=cursor_dir)
    except KeyboardInterrupt:
        print("\n[Info] Smart Cursor Mode interrupted.")
    except Exception as e:
        print(f"\n[Error] Failed to run Smart Cursor Mode: {e}")

def main():
    while True:
        try:
            print("\n" + "=" * 40)
            print("      GestureGazeVoice Launcher")
            print("=" * 40)
            print("1. Smart Voice Mode")
            print("2. Smart Cursor Mode")
            print("3. Exit")
            print("=" * 40)
            
            choice = input("Select an option (1-3): ").strip()
            
            if choice == "1":
                run_voice()
            elif choice == "2":
                run_cursor()
            elif choice == "3":
                print("\nExiting GestureGazeVoice. Goodbye!")
                break
            else:
                print("\n[Invalid Selection] Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            # Handle Ctrl+C at the launcher prompt level
            print("\n\nUse option 3 to exit the application.")
        except Exception as e:
            print(f"\n[Unexpected Error] {e}")

if __name__ == "__main__":
    main()
