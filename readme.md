![Plugin Banner](https://i.imgur.com/zisJ10P.png)

## Description
This project aims to enable Runescape content creators to import 3D assets from Runescape into blender. 

## Features
- **Format Compatibility:** The plugin supports all OSRS formats and baisc support for RS3 models.
- **Accurate Color Representation:** The plugin loads the color table directly from the game as a texture, ensuring that the imported models retain the exact colors found in Runescape.
- **Transparency Support:** The plugin handles transparent faces by generating a new material with applied transparency using the palette image.
- **Vertex Grouping:** For models made using their in-house Jaged tool editor, the plugin automatically creates vertex groups.
- **Armature Creation:** The plugin creates an armature (skeleton) for models created with the new animation system.

## Usage Instructions
1. **Installation:** Download the plugin and install it in Blender following the standard plugin installation process.
2. **Importing Models:** Select file->import->Runescape Model (.dat)
2. **Importing Skeletons:** Select file->import->Runescape Skeleton (.dat)

## Custom Plugins in Blender
To import custom plugins into Blender:
1. Launch Blender and open the "Preferences" window.
2. Navigate to the "Add-ons" section.
3. Click "Install" and select the custom plugin file.
4. Enable the installed plugin by checking the checkbox next to its name.
5. Save the preferences to retain the plugin's activation.

**Note:** Back face culling is applied by default.


---

*This plugin is developed independently and is not affiliated with Jagex or Runescape in any way.*
