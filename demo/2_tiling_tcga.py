from gigapath.pipeline import tile_one_slide
import os
import argparse
import tqdm

parser = argparse.ArgumentParser(description='Tiling slides')
parser.add_argument('--slide_path', type=str, help='Path to the slide directory', 
                    default='/data/shaohua/tcga')
parser.add_argument('--output_dir_prefix', type=str, help='Path to the output directory prefix', 
                    default='/data/shaohua/tcga_tiles')
parser.add_argument('--mpp', type=float, help='Microns per pixel', 
                    default=0.5)
parser.add_argument('--level', type=int, help='Level to read from the slide (overrides --mpp)', 
                    default=-1)
args = parser.parse_args()

# NOTE: Prov-GigaPath is trained with 0.5 mpp preprocessed slides. 
# Please make sure to use the appropriate level for the 0.5 MPP.

# When we manually specify the level, we don't need to specify the mpp.
if args.level >= 0:
    args.mpp = None

if os.path.isdir(args.slide_path):
    slide_filenames = [ os.path.join(args.slide_path, f) for f in os.listdir(args.slide_path) ]
    svs_filepaths = []
    for slide_filename in slide_filenames:
        slide_path = os.path.join(args.slide_path, slide_filename)
        if os.path.isdir(slide_path):
            svs_filenames = [ os.path.join(slide_path, f) for f in os.listdir(slide_path) if f.endswith('.svs') ]
            svs_filepaths.extend(svs_filenames)
        elif slide_filename.endswith('.svs'):
            svs_filepaths.append(slide_path)
elif os.path.isfile(args.slide_path) and args.slide_path.endswith('.svs'):
    svs_filepaths = [args.slide_path]

print(f"Found {len(svs_filepaths)} slides in  {args.slide_path}")
output_dir = args.output_dir_prefix + f"_mpp_{args.mpp}_level_{args.level}"
os.makedirs(output_dir, exist_ok=True)
print(f"Saving tiles to {output_dir}")

total_filesize_gb = 0
for svs_filepath in svs_filepaths:
    file_size_bytes = os.path.getsize(svs_filepath)
    file_size_gb = file_size_bytes / (1024 * 1024 * 1024)
    total_filesize_gb += file_size_gb
print(f"Total size: {total_filesize_gb:.1f}GB")

processed_filesize_gb = 0
num_total_tiles = 0

for svs_filepath in tqdm.tqdm(svs_filepaths):
    # Get the file size of the slide
    file_size_bytes = os.path.getsize(svs_filepath)
    # Convert bytes to megabytes
    file_size_gb = file_size_bytes / (1024 * 1024 * 1024)
    processed_filesize_gb += file_size_gb
    filesize_percent = processed_filesize_gb / total_filesize_gb * 10000
    print(f"{filesize_percent:.1f}%% {int(num_total_tiles/1000)}K tiles  {file_size_gb:.1f}/{processed_filesize_gb:.1f}/{total_filesize_gb:.1f}GB {svs_filepath}")
    num_tiles = tile_one_slide(svs_filepath, save_dir=output_dir, mpp=args.mpp, level=args.level)
    num_total_tiles += num_tiles

# NOTE: tiling dependency libraries can be tricky to set up. 
# Please double check the generated tile images."


#import huggingface_hub
#assert "HF_TOKEN" in os.environ, "Please set the HF_TOKEN environment variable to your Hugging Face API token"
# huggingface_hub.hf_hub_download("prov-gigapath/prov-gigapath", filename="sample_data/PROV-000-000001.ndpi", local_dir=local_dir, force_download=True)
#slide_path = os.path.join(local_dir, "sample_data/PROV-000-000001.ndpi")
