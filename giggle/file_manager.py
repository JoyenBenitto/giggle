import os
from enum import Enum
from .types import *

class ParseInputDir:
    def __init__(self, dir_path):
        self.dir_path:str= dir_path
        self.toprocess: List[SrcMeta] = []

    def __walker(self, path):
        """
        Walks through and builds collective datastructure for post processing
        and html generation.
        """
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file[-3:] == ".md":
                        path= os.path.join(root, file)
                        base_name= os.path.basename(path)
                        to_process= SrcMeta(
                                node_name=base_name,
                                path= path,
                                build_type=BuildType.HTML) # by default will be filtered later
                        self.toprocess.append(to_process)

    def normalize(self):
        self.__walker(self.dir_path)
        return self.toprocess

