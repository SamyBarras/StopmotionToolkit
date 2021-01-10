import os, collections
import common.user_settings as user_settings
import common.cam as cam

class Project():
    def __new__(cls, ostype, workingdir, video_device, outputdisplay): 
        print("Creating new project")
        cls.camera = cam.cam(video_device, ostype, user_settings.camera_codec)
        return super(Project, cls).__new__(cls) 

    def __init__(self, ostype, workingdir, video_device, outputdisplay):
        self.name = user_settings.project_name
        # files and dir
        self.os = ostype
        self.workingdir = workingdir
        self.hddir = os.path.join(self.workingdir, "HQ")
        # 
        self.take = 0
        self.fps = user_settings.FPS
        self.framerate = (1/user_settings.FPS)
        maxFramesBuffer = int(user_settings.PREVIEW_DURATION*user_settings.FPS)
        self.frames = collections.deque(maxlen=maxFramesBuffer)
        

