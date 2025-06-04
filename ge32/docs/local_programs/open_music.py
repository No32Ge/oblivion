
import os
import platform

def play(file_path):
    system = platform.system()
    if system == 'Darwin':  # macOS
        os.system(f'open {file_path}')
    elif system == 'Windows':
        os.startfile(file_path)
    else:  # linux
        os.system(f'xdg-open {file_path}')

if __name__ == '__main__':
    import sys
    play(sys.argv[1])
