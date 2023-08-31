![Plugin Banner](https://i.imgur.com/zisJ10P.png)

## Description
This project aims to enable Runescape content creators to import 3D assets from Runescape into blender. 

## Support

For support using this plugin, feedback, suggestions please join our discord server.
[![Click to Join](https://i.imgur.com/9dYHk5P.png)](https://discord.gg/Fj7kaZJa9U)


## Features


- **Format Compatibility:** The plugin supports all OSRS formats and baisc support for RS3 models.
- **Accurate Color Representation:** The plugin loads the color table directly from the game as a texture, ensuring that the imported models retain the exact colors found in Runescape.
- **Transparency Support:** The plugin handles transparent faces by generating a new material with applied transparency using the palette image.
- **Vertex Grouping:** For models made using their in-house Jaged tool editor, the plugin automatically creates vertex groups.
- **Armature Creation(WIP):** The plugin creates an armature (skeleton) for models created with the new animation system.
- **Textures(WIP):** Has some support for osrs textures.



**Note:** 

- Back face culling is applied by default.
- Skeletons are still a work in progress, some will be okay, bust most will not. 

## Downloading


Go to [releases](https://github.com/tamateea/RuneBlend/releases) section to download the zipped addon.


## Usage Instructions


1. **Installation:** Download the plugin and install it in Blender following the standard plugin installation process.
2. **Importing Models:** Select file->import->Runescape Model (.dat)
2. **Importing Skeletons:** Select file->import->Runescape Skeleton (.dat)

## Installing Plugins in Blender


To import custom plugins into Blender:
1. Launch Blender and open the "Preferences" window.
2. Navigate to the "Add-ons" section.
3. Click "Install" and select the custom plugin file.
4. Enable the installed plugin by checking the checkbox next to its name.
5. Save the preferences to retain the plugin's activation.



## Contributing


Feel free to contribute to this project by making a pull request, join the discord if you'd like to discuss development.

---

*This plugin is developed independently and is not affiliated with Blender, Jagex or Runescape in any way.*
