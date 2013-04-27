class HoverGroup(object):
    """Groups of objects that show a marker when they are hovered over with the cursor/mouse."""

    def __init__(self):
        self.under_cursor = {}
        self.markers = {}

    def hide_all(self):
        for map_object_ref, map_object in self.under_cursor.iteritems():
            self.markers[map_object_ref].hide()

    def set_over_objects(self, objects_under_cursor):
        under_cursor = {}

        for map_object in objects_under_cursor:
            if not type(map_object) == self.map_view_type:
                continue
            under_cursor[map_object] = map_object
            self.markers[map_object].show()

        for map_object_ref, map_object in self.under_cursor.iteritems():
            if under_cursor.has_key(map_object_ref):
                continue
            self.markers[map_object_ref].hide()

        self.under_cursor = under_cursor
    
    def handle_mouse_drag(self, *args):
        self.hide_all()
    
    def handle_mouse_scroll(self, *args):
        self.hide_all()
    
    def handle_resize(self, *args):
        self.hide_all()
