#!/bin/bash

# Function to display usage help
function show_help {
    echo "Usage: $(basename "$0") [DIRECTORY]"
    echo
    echo "Converts all JPEG and PNG images in the specified DIRECTORY to WebP format (lossless) using FFmpeg,"
    echo "preserving color space based on metadata."
    echo "If no directory is specified, the current directory is used."
    echo
    echo "Options:"
    echo "  -h, --help       Show this help message and exit"
    echo "  --dry-run        Show the files that would be converted without performing the actual conversion"
    echo
    echo "Examples:"
    echo "  $(basename "$0")                # Convert images in the current directory"
    echo "  $(basename "$0") /path/to/dir    # Convert images in a specific directory"
    echo "  $(basename "$0") --dry-run       # Show files to be converted in the current directory"
    echo "  $(basename "$0") /path/to/dir --dry-run   # Show files to be converted in a specific directory"
}

# Function to check for required dependencies
function check_dependencies {
    if ! command -v ffmpeg &> /dev/null; then
        echo "Error: ffmpeg is not installed. Please install it and try again."
        exit 1
    fi
    if ! command -v exiftool &> /dev/null; then
        echo "Error: exiftool is not installed. Please install it and try again."
        exit 1
    fi
}

# Function to get color profile information
function get_color_profile {
    local img="$1"
    local colorspace=$(exiftool -ColorSpace -s "$img")
    local profile=$(exiftool -ICC_Profile:ProfileDescription -s "$img")
    echo "$colorspace" "$profile"
}

# Check dependencies
check_dependencies

# Default values
DIR="."
DRY_RUN=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        -h|--help)
            show_help
            exit 0
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            DIR="$arg"
            shift
            ;;
    esac
done

# Loop through each .jpeg, .jpg, .JPEG, .JPG, .png, and .PNG file in the specified directory
for img in "$DIR"/*.{jpeg,jpg,JPEG,JPG,png,PNG}; do
    if [[ -f "$img" ]]; then
        # Extract color space and profile information
        read colorspace profile < <(get_color_profile "$img")

        # Determine FFmpeg options based on color space and profile
        ffmpeg_options="-c:v libwebp -lossless 1"
        
        if [[ "$colorspace" == "sRGB" ]]; then
            ffmpeg_options+=" -colorspace 1 -color_primaries 1 -color_trc 1"
        elif [[ "$colorspace" == "AdobeRGB" || "$profile" == *"Adobe RGB"* ]]; then
            ffmpeg_options+=" -colorspace 2 -color_primaries 1 -color_trc 1"
        fi

        # Get filename without extension
        filename=$(basename "$img" .jpeg)
        filename=${filename%.jpg}
        filename=${filename%.png}
        filename=${filename%.JPEG}
        filename=${filename%.JPG}
        filename=${filename%.PNG}

        # Check if dry run is enabled
        if [ "$DRY_RUN" = true ]; then
            echo "Dry Run: Would convert $img to $DIR/$filename.webp with color settings: $colorspace $profile"
        else
            # Perform the actual conversion
            ffmpeg -i "$img" $ffmpeg_options "$DIR/$filename.webp"
            echo "Converted $img to $filename.webp with color settings: $colorspace $profile"
        fi
    fi
done

echo "Operation completed."
if [ "$DRY_RUN" = true ]; then
    echo "Dry run only; no files were actually converted."
fi
