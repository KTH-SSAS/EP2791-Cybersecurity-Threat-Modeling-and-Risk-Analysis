from connection_gui import GUIConnection
from connection_blocks_gui import GUIConnectionTriangle


class GUIConnectionWithBlocks(GUIConnection):
    """Manages a directional connection in a setup view."""

    def __init__(self, model, view, *, start_coordinate=None, end_coordinate=None):
        self.__view = view

        start_block = GUIConnectionTriangle(model, view, "RIGHT", False)
        end_block = GUIConnectionTriangle(model, view, "RIGHT", True)

        super().__init__(model, view, start_block, "RIGHT",
                         end_block=end_block, end_direction="LEFT")

        self.__is_deleted = False

        if start_coordinate is not None:
            start_block.move_block(start_coordinate[0] - start_block.get_x(),
                                   start_coordinate[1] - start_block.get_y())
            start_block.put_down_block()

        if end_coordinate is not None:
            end_block.move_block(end_coordinate[0] - end_block.get_x(),
                                 end_coordinate[1] - end_block.get_y())
            end_block.put_down_block()

    def open_options(self):
        """System-view connections intentionally have no editable options."""
        return None

    def get_start_setup_class_gui(self):
        """Return the GUI setup class from which this connection starts."""
        return self.get_start_block().get_attached_setup_class_gui()

    def get_end_setup_class_gui(self):
        """Return the GUI setup class into which this connection points."""
        return self.get_end_block().get_attached_setup_class_gui()

    def get_start_setup_class(self):
        """Return the non-GUI setup class from which this connection starts."""
        start_setup_class_gui = self.get_start_setup_class_gui()
        if start_setup_class_gui is None:
            return None
        return start_setup_class_gui.get_setup_class()

    def get_end_setup_class(self):
        """Return the non-GUI setup class into which this connection points."""
        end_setup_class_gui = self.get_end_setup_class_gui()
        if end_setup_class_gui is None:
            return None
        return end_setup_class_gui.get_setup_class()

    def get_movable_items(self):
        """Return unattached endpoint blocks that move directly with the view."""
        return [block for block in (self.get_start_block(), self.get_end_block())
                if not block.is_attached()]

    def is_deleted(self):
        return self.__is_deleted

    def delete(self):
        if not self.__is_deleted:
            self.__is_deleted = True
            self.remove_corners()
            self.remove_lines()
            self.__view.remove_connection_with_blocks(self)
            self.get_start_block().delete()
            self.get_end_block().delete()

    def save_state(self):
        return {
            "start_block": self.get_start_block().save_state(),
            "end_block": self.get_end_block().save_state(),
        }
