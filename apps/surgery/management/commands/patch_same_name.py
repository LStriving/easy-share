import os
from django.core.management.base import BaseCommand

from EasyShare.settings.base import EXTRACT_OUTPUT_DIR, OAD_FILE_OUTPUT_DIR, PRE_DUR_FILE_POSTFIX, PRE_FILE_POSTFIX, SEG_FILE_OUTPUT_DIR, SEG_IMG_OUTPUT_DIR, SEG_VIDEO_OUTPUT_DIR, TARGET_DIR
from sharefiles.models import File

class Command(BaseCommand):
    help = '[Patch] Fix the same name issue,\
        change the finished task output name/url from video name to md5'
    
    def handle(self, *args, **options):
        # get all tasks
        files = File.objects.all()

        to_rename = {}
        for file in files:
            # change the output name
            # change the extracted frames output name
            video_names = os.listdir(EXTRACT_OUTPUT_DIR)
            for video_name in video_names:
                if file.name.split(".")[0] == video_name:
                    to_rename[video_name] = file.md5
        for old_name, new_name in to_rename.items():
            # rename for extracted frames
            os.rename(os.path.join(EXTRACT_OUTPUT_DIR, old_name), os.path.join(EXTRACT_OUTPUT_DIR, new_name))
            self.stdout.write(self.style.SUCCESS(f'Extracted frames: {old_name} --> {new_name}'))
            
        seg_img_dirs = os.listdir(SEG_IMG_OUTPUT_DIR)
        for seg in seg_img_dirs:
            if seg in to_rename:
                os.rename(os.path.join(SEG_IMG_OUTPUT_DIR, seg), os.path.join(SEG_IMG_OUTPUT_DIR, to_rename[seg]))
                self.stdout.write(self.style.SUCCESS(f'Segmented images: {seg} --> {to_rename[seg]}'))
            else:
                for file in files:
                    if file.name.split(".")[0] == seg:
                        new_name = file.md5
                        os.rename(os.path.join(SEG_IMG_OUTPUT_DIR, seg), os.path.join(SEG_IMG_OUTPUT_DIR, new_name))
                        to_rename[seg] = new_name
                        self.stdout.write(self.style.SUCCESS(f'Segmented images: {seg} --> {new_name}'))
                        break
        
        # rename video
        for seg_vid in os.listdir(SEG_VIDEO_OUTPUT_DIR):
            postfix = seg_vid.split(".")[-1]
            if seg_vid.split(".")[0] in to_rename:
                os.rename(os.path.join(SEG_VIDEO_OUTPUT_DIR, seg_vid), os.path.join(SEG_VIDEO_OUTPUT_DIR, to_rename[seg_vid.split(".")[0]] +"." + postfix))
                self.stdout.write(self.style.SUCCESS(f'Segmented video: {seg_vid} --> {to_rename[seg_vid]}'))
            else:
                for file in files:
                    if file.name == seg_vid:
                        new_name = file.md5
                        os.rename(os.path.join(SEG_VIDEO_OUTPUT_DIR, seg_vid), os.path.join(SEG_VIDEO_OUTPUT_DIR, new_name + "." + postfix))
                        to_rename[seg_vid.split(".")[0]] = new_name
                        self.stdout.write(self.style.SUCCESS(f'Segmented video: {seg_vid} --> {new_name}'))
                        break
        
        # rename seg output
        try:
            for res in os.listdir(SEG_FILE_OUTPUT_DIR):
                video_name = res.split('_interact')[0]
                postfix = res.split(video_name)[-1]
                if video_name in to_rename:
                    os.rename(os.path.join(SEG_FILE_OUTPUT_DIR, res), os.path.join(SEG_FILE_OUTPUT_DIR, to_rename[video_name] + postfix))
                    self.stdout.write(self.style.SUCCESS(f'Segmented output: {res} --> {to_rename[video_name]+postfix}'))
                else:
                    for file in files:
                        if file.name.split(".")[0] == video_name:
                            new_name = file.md5
                            os.rename(os.path.join(SEG_FILE_OUTPUT_DIR, res), os.path.join(SEG_FILE_OUTPUT_DIR, new_name + postfix))
                            to_rename[video_name] = new_name
                            self.stdout.write(self.style.SUCCESS(f'Segmented output: {res} --> {new_name}'))
                            break
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error renaming segmented output: {str(e)}'))
        
        # rename oad target and output
        try:
            for npy in os.listdir(os.path.join(EXTRACT_OUTPUT_DIR, TARGET_DIR)):
                video_name = npy.split('.')[0]
                postfix = '.npy'
                if video_name in to_rename:
                    os.rename(os.path.join(EXTRACT_OUTPUT_DIR, TARGET_DIR, npy), os.path.join(EXTRACT_OUTPUT_DIR,TARGET_DIR, to_rename[video_name] + postfix))
                    self.stdout.write(self.style.SUCCESS(f'Target file: {npy} --> {to_rename[video_name]+postfix}'))
                else:
                    for file in files:
                        if file.name.split(".")[0] == video_name:
                            new_name = file.md5
                            os.rename(os.path.join(EXTRACT_OUTPUT_DIR, TARGET_DIR, npy), os.path.join(EXTRACT_OUTPUT_DIR, TARGET_DIR, new_name + postfix))
                            to_rename[video_name] = new_name
                            self.stdout.write(self.style.SUCCESS(f'Target file: {npy} --> {new_name}'))
                            break
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error renaming target file: {str(e)}'))
        
        try:
            for file in os.listdir(OAD_FILE_OUTPUT_DIR):
                video_name = file.split(PRE_FILE_POSTFIX)[0].split(PRE_DUR_FILE_POSTFIX)[0]
                postfix = file.split(video_name)[-1]
                if video_name in to_rename:
                    os.rename(os.path.join(OAD_FILE_OUTPUT_DIR, file), os.path.join(OAD_FILE_OUTPUT_DIR, to_rename[video_name] + postfix))
                    self.stdout.write(self.style.SUCCESS(f'OAD output: {file} --> {to_rename[video_name]+postfix}'))
                else:
                    for i in files:
                        if i.name.split(".")[0] == video_name:
                            new_name = i.md5
                            os.rename(os.path.join(OAD_FILE_OUTPUT_DIR, file), os.path.join(OAD_FILE_OUTPUT_DIR, new_name + postfix))
                            self.stdout.write(self.style.SUCCESS(f'OAD output: {file} --> {new_name}'))
                            break
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING('No OAD output found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error renaming oad output: {str(e)}'))