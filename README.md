### This is an Enlarged version of Dirn [Yet Another Monochrome Icon Set](https://www.pling.com/p/2303161/)

## Yet Another Monochrome Icon Set For KDE Plasma ##

Yet Another Monochrome Icon Set is a clean, adaptive icon theme for KDE Plasma. It automatically adjusts its color based
on the background—white on dark backgrounds and black on light ones—for better visibility and a consistent look across
the desktop.

The set features major modifications to the SVG path structuring for improved consistency, all done using Inkscape.
While it is loosely based on the Orion icon theme by Seth Storm Rosenaa, a number of additional icons have been included
based on personal needs, helping to improve coverage and integration within the system.

### Few word about cropping

Cropping was performed with inkscape cli.

```shell
inkscape --batch-process $src_path --actions=select-all;transform-scale:1,2,1,2;export-filename:$dst_path;export-do'
```

Paths that were not cropped: 

> "/apps/scalable/"  
> "/places/scalable/"  
> "/mimetypes/scalable/"  
> "/emblems/scalable/"  
> "/devices/scalable/"  