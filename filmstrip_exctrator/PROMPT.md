You are a python developer with very good knowledge of oiiotool and ffmpeg. You do have good knowledge of modern python libraries and frameworks. You write python code with typing annotations and use modern python practices. The code needs to be also universal and usable in python 3.9 version. Use pathlib for path operations. Do not exceed 80 characters per line. Add docstrings and comments where it is needed.

## You need to write python script doing following:
1. take input video file or image sequence and exctract image frames with defined resolution, output images should be PNG, 5 frames per second. These images should be exported into unique temporary directory and they are only imtermediate images for next process.
2. take all previously exported frames and combine them together into filmstrip where each image is connected together with side image frames. add padding between images with 5 pixels. Output image should be JPG.
3. remove all intermediate images from 1. step

## Here are the above function input parameters:
- input_file_or_sequence: str, the input video file or image sequence
- output_dir: str, the output directory for intermediate images
- resolution: tuple[int, int], the resolution of the output images
- padding: int, the padding between images in the filmstrip
- fps: int, the frames per second for the filmstrip
- output_filmstrip_image_path: str, the path to the output filmstrip image

## Constrains:
- stay only within context of `.\filmstrip_exctrator` projectroot folder.
- add __main__.py and __init__.py
- create simple testing file so you are able to validate code before you considering it ready for production. Use included testing dataset for filmstrip creation process.
- *./.env* is having environment variables which should be used by the script. Particularly `OIIOTOOL_PATH` is important for oiiotool executable to be used with the filmstrip creation process.
- *./testing_dataset* folder inside of root project folder is offering testing dataset for filmstrip creation process. Inside is *sequence* and *video* folder with files to be used for testing.
