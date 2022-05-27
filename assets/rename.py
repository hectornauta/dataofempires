import os

DIR = os.path.dirname(__file__)

def main():
    folder = f'{DIR}/civ_icons'
    for count, filename in enumerate(os.listdir(folder)):
        src = f'{folder}/{filename}'
        dst = src.replace('menu_techtree_', '')
        os.rename(src, dst)

if __name__ == '__main__':
    main()
