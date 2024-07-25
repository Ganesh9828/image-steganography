import argparse
from PIL import Image


class Steganography:

    BLACK_PIXEL = (0, 0, 0)

    def _int_to_bin(self, rgb_tuple):
        """Convert an integer tuple to a binary (string) tuple.

        :param rgb_tuple: An integer tuple like (220, 110, 96)
        :return: A string tuple like ("00101010", "11101011", "00010110")
        """
        red, green, blue = rgb_tuple
        return f'{red:08b}', f'{green:08b}', f'{blue:08b}'

    def _bin_to_int(self, bin_tuple):
        """Convert a binary (string) tuple to an integer tuple.

        :param bin_tuple: A string tuple like ("00101010", "11101011", "00010110")
        :return: Return an int tuple like (220, 110, 96)
        """
        red_bin, green_bin, blue_bin = bin_tuple
        return int(red_bin, 2), int(green_bin, 2), int(blue_bin, 2)

    def _merge_rgb(self, base_rgb, secret_rgb):
        """Merge two RGB tuples.

        :param base_rgb: An integer tuple like (220, 110, 96)
        :param secret_rgb: An integer tuple like (240, 95, 105)
        :return: An integer tuple with the two RGB values merged.
        """
        red_base, green_base, blue_base = self._int_to_bin(base_rgb)
        red_secret, green_secret, blue_secret = self._int_to_bin(secret_rgb)
        merged_rgb = red_base[:4] + red_secret[:4], green_base[:4] + green_secret[:4], blue_base[:4] + blue_secret[:4]
        return self._bin_to_int(merged_rgb)

    def _unmerge_rgb(self, merged_rgb):
        """Unmerge RGB.

        :param merged_rgb: An integer tuple like (220, 110, 96)
        :return: An integer tuple with the two RGB values unmerged.
        """
        red, green, blue = self._int_to_bin(merged_rgb)
        # Extract the last 4 bits (corresponding to the hidden image)
        # Concatenate 4 zero bits because we are working with 8 bit
        new_rgb = red[4:] + '0000', green[4:] + '0000', blue[4:] + '0000'
        return self._bin_to_int(new_rgb)

    def merge(self, base_image, secret_image):
        """Merge secret_image into base_image.

        :param base_image: First image
        :param secret_image: Second image
        :return: A new merged image.
        """
        # Check the images dimensions
        if secret_image.size[0] > base_image.size[0] or secret_image.size[1] > base_image.size[1]:
            raise ValueError('Secret image should be smaller than base image!')

        # Get the pixel map of the two images
        base_map = base_image.load()
        secret_map = secret_image.load()

        merged_image = Image.new(base_image.mode, base_image.size)
        merged_map = merged_image.load()

        for x in range(base_image.size[0]):
            for y in range(base_image.size[1]):
                is_within_bounds = lambda: x < secret_image.size[0] and y < secret_image.size[1]
                base_rgb = base_map[x, y]
                secret_rgb = secret_map[x, y] if is_within_bounds() else self.BLACK_PIXEL
                merged_map[x, y] = self._merge_rgb(base_rgb, secret_rgb)

        return merged_image

    def unmerge(self, merged_image):
        """Unmerge an image.

        :param merged_image: The input image.
        :return: The unmerged/extracted image.
        """
        pixel_map = merged_image.load()

        # Create the new image and load the pixel map
        extracted_image = Image.new(merged_image.mode, merged_image.size)
        extracted_map = extracted_image.load()

        for x in range(merged_image.size[0]):
            for y in range(merged_image.size[1]):
                extracted_map[x, y] = self._unmerge_rgb(pixel_map[x, y])

        return extracted_image


def main():
    parser = argparse.ArgumentParser(description='Steganography')
    subparser = parser.add_subparsers(dest='command')

    merge_parser = subparser.add_parser('merge')
    merge_parser.add_argument('--base_image', required=True, help='Base image path')
    merge_parser.add_argument('--secret_image', required=True, help='Secret image path')
    merge_parser.add_argument('--output', required=True, help='Output path')

    unmerge_parser = subparser.add_parser('unmerge')
    unmerge_parser.add_argument('--merged_image', required=True, help='Merged image path')
    unmerge_parser.add_argument('--output', required=True, help='Output path')

    args = parser.parse_args()

    if args.command == 'merge':
        base_image = Image.open(args.base_image)
        secret_image = Image.open(args.secret_image)
        Steganography().merge(base_image, secret_image).save(args.output)
    elif args.command == 'unmerge':
        merged_image = Image.open(args.merged_image)
        Steganography().unmerge(merged_image).save(args.output)


if __name__ == '__main__':
    main()
