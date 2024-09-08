import json

PALETTE_PATH = 'json/colors.json'


class ColorPalette:
    def __init__(self, colors: json):
        for color in colors:
            color_name = color['name'].replace(' ', '_').lower()
            setattr(self, color_name, color['hex'])

    def __repr__(self):
        return f"<ColorPalette {self.palette_name}: {', '.join([f'{attr}={getattr(self, attr)}' for attr in self.__dict__ if attr != 'palette_name'])}>"

    def __getitem__(self, item):
        return getattr(self, item)


def grab_palette(palette_name: str) -> ColorPalette:
    with open(PALETTE_PATH, 'r') as f:
        data = json.load(f)
    return ColorPalette(data[palette_name])


if __name__ == '__main__':
    print(grab_palette('Chromatic'))
