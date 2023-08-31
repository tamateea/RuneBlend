import os


bl_info = {
    "name":         "RuneBlend",
    "author":       "Tamatea",
    "blender": (3, 0, 0),
    "version": (1, 0, 0),
    "location":     "File > Import-Export",
    "description":  "Import Runescape data format",
    "category":     "Import-Export",
}

import bpy
from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.types import Operator


# ################################################################
# Import Model
# ################################################################

class ImportDAT(Operator, ImportHelper):
    bl_idname = "import.model"
    bl_label = "Import Model"

    filename_ext = ".dat"
    filter_glob = StringProperty( default="*.dat", options={"HIDDEN"})
    
    def execute( self, context ):
        import runeblend.import_model
        return runeblend.import_model.load(self)


# ################################################################
# Import Skeleton
# ################################################################
class ImportSkeleton(Operator, ImportHelper):
    bl_idname = "import.skeleton"
    bl_label = "Import skeleton"

    filename_ext = ".dat"
    filter_glob = StringProperty( default="*.dat", options={"HIDDEN"})

    def execute( self, context ):
        pass
        import runeblend.import_skeleton
        return runeblend.import_skeleton.load(self)


# ################################################################
# Common
# ################################################################
def menu_func_import( self, context ):
    self.layout.operator(ImportDAT.bl_idname, text="Runescape Model (.dat)")
    self.layout.operator(ImportSkeleton.bl_idname, text="Runescape Skeleton (.dat)")


# Register classes
classes = (
    ImportDAT,
    ImportSkeleton,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()