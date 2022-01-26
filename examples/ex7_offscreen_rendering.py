from occwl.solid import Solid
from occwl.viewer import OffscreenRenderer


v = OffscreenRenderer()
ex = Solid.make_box(1, 2, 1)
v.display(ex)
v.fit()
v.save_image("image.png")
