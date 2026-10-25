### This is an Enlarged version of Dirn [Yet Another Monochrome Icon Set](https://www.pling.com/p/2303161/)

## Yet Another Monochrome Icon Set For KDE Plasma ##

Yet Another Monochrome Icon Set is a clean, adaptive icon theme for KDE Plasma. It automatically adjusts its color based
on the background—white on dark backgrounds and black on light ones—for better visibility and a consistent look across
the desktop.

The set features major modifications to the SVG path structuring for improved consistency, all done using Inkscape.
While it is loosely based on the Orion icon theme by Seth Storm Rosenaa, a number of additional icons have been included
based on personal needs, helping to improve coverage and integration within the system.

### Few word about cropping

Icons are enlarged 1.2x around the center of their visible bounding box. Instead of transforming the drawing, the root
`viewBox` is shrunk around that center, which renders the same and takes about a second for the whole set.
The bounding box comes from librsvg.

```shell
python3 tools/enlarge.py path/to/upstream/checkout .
```

Requires PyGObject and librsvg typelib (`python-gobject librsvg` on Arch, `python3-gi gir1.2-rsvg-2.0` on Debian/Ubuntu).

Paths that are not cropped (see `SKIP_DIRS` in `tools/enlarge.py`):

> "/apps/scalable/"  
> "/places/scalable/" (and "-outlined")  
> "/mimetypes/scalable/" (and "-outlined")  
> "/emblems/scalable/"  
> "/devices/scalable/"  

### Updates

`.github/workflows/sync.yml` checks [upstream](https://bitbucket.org/dirn-typo/yet-another-monochrome-icon-set) daily,
rebuilds the theme and commits the result. Each new upstream version also gets a GitHub release with a tarball.
If the theme is installed as a clone of this repository, `git pull` is enough to update it.