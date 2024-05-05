import argparse
import os
import subprocess

def create_thumbnail(image_path, thumb_path):
    """Generates a thumbnail for an image using FFmpeg."""
    cmd = [
        'ffmpeg', '-i', image_path,
        '-vf', 'scale=w=min(iw\\,500):h=min(ih\\,500):force_original_aspect_ratio=decrease',
        '-qscale:v', '2',  # Quality scale for JPEG and WebP
        thumb_path
    ]
    subprocess.run(cmd, check=True)

def create_html(directory, images):
    """Creates an index.html file in the specified directory based on the provided images."""
    if not images:
        return  # Do not create HTML if no images are processed
    
    html_path = os.path.join(directory, 'index.html')
    html_content = []
    html_header = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Photo Album</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lightgallery.js/dist/css/lightgallery.min.css" />
</head>
<body>
<div id="lightgallery">
'''
    html_footer = '''
</div>
<script src="https://cdn.jsdelivr.net/npm/lightgallery.js/dist/js/lightgallery.min.js"></script>
<script>
    lightGallery(document.getElementById('lightgallery'), {
        selector: 'a'
    });
</script>
</body>
</html>
'''

    for img, thumb in images:
        html_content.append(f'''
    <a href="{os.path.relpath(img, start=directory)}">
        <img src="{os.path.relpath(thumb, start=directory)}" alt="Thumbnail of {os.path.basename(img)}" style="max-width:100%;height:auto;">
    </a>
''')

    html_full = html_header + "\n".join(html_content) + html_footer
    with open(html_path, 'w') as file:
        file.write(html_full)

def process_directory(directory, recursive, dryrun):
    """Processes a single directory to create thumbnails and an HTML file."""
    images = []
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']  # Supported image extensions
    for filename in os.listdir(directory):
        extension = os.path.splitext(filename)[1].lower()
        if extension in image_extensions and not filename.startswith("thumb"):
            full_image_path = os.path.join(directory, filename)
            thumb_filename = f"thumb-500-{filename}"
            thumb_path = os.path.join(directory, thumb_filename)

            if not dryrun:
                if not os.path.exists(thumb_path):
                    create_thumbnail(full_image_path, thumb_path)
            images.append((full_image_path, thumb_path))
    
    # Sort images by filename to ensure they appear in alphabetical order
    images.sort(key=lambda x: os.path.basename(x[0]))

    if not dryrun:
        create_html(directory, images)
    else:
        for img, thumb in images:
            print(f'Will process image: {img}')
            print(f'Will create thumbnail: {thumb}')

def walk_directory(directory, recursive, dryrun):
    """Walks through the directory and processes each directory found."""
    if recursive:
        for root, dirs, files in os.walk(directory):
            process_directory(root, recursive, dryrun)
    else:
        process_directory(directory, recursive, dryrun)

def main():
    parser = argparse.ArgumentParser(description='Generate a simple image gallery using FFmpeg, optionally recursively.')
    parser.add_argument('directory', type=str, help='Directory containing images to process.')
    parser.add_argument('-r', '--recursive', action='store_true', help='Process images recursively in subdirectories.')
    parser.add_argument('--dryrun', action='store_true', help='Output the processing steps without creating files.')

    args = parser.parse_args()
    walk_directory(args.directory, args.recursive, args.dryrun)

if __name__ == "__main__":
    main()
