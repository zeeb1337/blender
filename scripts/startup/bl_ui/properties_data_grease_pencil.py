# SPDX-FileCopyrightText: 2023 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
from bpy.types import Panel, Menu, UIList
from rna_prop_ui import PropertyPanel


class DataButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return hasattr(context, "grease_pencil") and context.grease_pencil


class LayerDataButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        grease_pencil = context.grease_pencil
        return grease_pencil and grease_pencil.layers.active


class GREASE_PENCIL_UL_masks(UIList):
    def draw_item(self, _context, layout, _data, item, icon, _active_data, _active_propname, _index):
        mask = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(mask, "name", text="", emboss=False, icon_value=icon)
            row.prop(mask, "invert", text="", emboss=False)
            row.prop(mask, "hide", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.prop(mask, "name", text="", emboss=False, icon_value=icon)


class GREASE_PENCIL_MT_layer_mask_add(Menu):
    bl_label = "Add Mask"

    def draw(self, context):
        layout = self.layout

        grease_pencil = context.grease_pencil
        active_layer = grease_pencil.layers.active
        found = False
        for layer in grease_pencil.layers:
            if layer == active_layer or layer.name in active_layer.mask_layers:
                continue

            found = True
            layout.operator("grease_pencil.layer_mask_add", text=layer.name).name = layer.name

        if not found:
            layout.label(text="No layers to add")


class DATA_PT_context_grease_pencil(DataButtonsPanel, Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout

        ob = context.object
        grease_pencil = context.grease_pencil
        space = context.space_data

        if ob:
            layout.template_ID(ob, "data")
        elif grease_pencil:
            layout.template_ID(space, "pin_id")


class GREASE_PENCIL_MT_grease_pencil_add_layer_extra(Menu):
    bl_label = "Add Extra"

    def draw(self, context):
        layout = self.layout
        grease_pencil = context.object.data
        space = context.space_data

        if space.type == 'PROPERTIES':
            layout.operator("grease_pencil.layer_group_add", text="Add Group")

        layout.separator()
        layout.operator("grease_pencil.layer_duplicate", text="Duplicate", icon='DUPLICATE')
        layout.operator("grease_pencil.layer_duplicate", text="Duplicate Empty Keyframes").empty_keyframes = True

        layout.separator()
        layout.operator("grease_pencil.layer_reveal", icon='RESTRICT_VIEW_OFF', text="Show All")
        layout.operator("grease_pencil.layer_hide", icon='RESTRICT_VIEW_ON', text="Hide Others").unselected = True

        layout.separator()
        layout.operator("grease_pencil.layer_lock_all", icon='LOCKED', text="Lock All")
        layout.operator("grease_pencil.layer_lock_all", icon='UNLOCKED', text="Unlock All").lock = False

        layout.separator()
        layout.prop(grease_pencil, "use_autolock_layers", text="Autolock Inactive Layers")


class DATA_PT_grease_pencil_layers(DataButtonsPanel, Panel):
    bl_label = "Layers"

    def draw(self, context):
        layout = self.layout

        grease_pencil = context.grease_pencil
        layer = grease_pencil.layers.active

        row = layout.row()
        row.template_grease_pencil_layer_tree()

        col = row.column()
        sub = col.column(align=True)
        sub.operator_context = 'EXEC_DEFAULT'
        sub.operator("grease_pencil.layer_add", icon='ADD', text="")
        sub.menu("GREASE_PENCIL_MT_grease_pencil_add_layer_extra", icon='DOWNARROW_HLT', text="")

        col.operator("grease_pencil.layer_remove", icon='REMOVE', text="")

        if not layer:
            return

        layout.use_property_split = True
        layout.use_property_decorate = True
        col = layout.column(align=True)

        # Layer main properties
        row = layout.row(align=True)
        row.prop(layer, "blend_mode", text="Blend Mode")

        row = layout.row(align=True)
        row.prop(layer, "opacity", text="Opacity", slider=True)


class DATA_PT_grease_pencil_layer_masks(LayerDataButtonsPanel, Panel):
    bl_label = "Masks"
    bl_parent_id = "DATA_PT_grease_pencil_layers"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        grease_pencil = context.grease_pencil
        layer = grease_pencil.layers.active

        self.layout.prop(layer, "use_masks", text="")

    def draw(self, context):
        layout = self.layout
        grease_pencil = context.grease_pencil
        layer = grease_pencil.layers.active

        layout = self.layout
        layout.enabled = layer.use_masks

        if not layer:
            return

        rows = 4
        row = layout.row()
        col = row.column()
        col.template_list("GREASE_PENCIL_UL_masks", "", layer, "mask_layers", layer.mask_layers,
                          "active_mask_index", rows=rows, sort_lock=True)

        col = row.column(align=True)
        col.menu("GREASE_PENCIL_MT_layer_mask_add", icon='ADD', text="")
        col.operator("grease_pencil.layer_mask_remove", icon='REMOVE', text="")

        col.separator()

        sub = col.column(align=True)
        sub.operator("grease_pencil.layer_mask_reorder", icon='TRIA_UP', text="").direction = 'UP'
        sub.operator("grease_pencil.layer_mask_reorder", icon='TRIA_DOWN', text="").direction = 'DOWN'


class DATA_PT_grease_pencil_layer_transform(LayerDataButtonsPanel, Panel):
    bl_label = "Transform"
    bl_parent_id = "DATA_PT_grease_pencil_layers"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        grease_pencil = context.grease_pencil
        layer = grease_pencil.layers.active
        layout.active = not layer.lock

        row = layout.row(align=True)
        row.prop(layer, "translation")

        row = layout.row(align=True)
        row.prop(layer, "rotation")

        row = layout.row(align=True)
        row.prop(layer, "scale")


class DATA_PT_grease_pencil_layer_relations(LayerDataButtonsPanel, Panel):
    bl_label = "Relations"
    bl_parent_id = "DATA_PT_grease_pencil_layers"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        grease_pencil = context.grease_pencil
        layer = grease_pencil.layers.active
        layout.active = not layer.lock

        row = layout.row(align=True)
        row.prop(layer, "parent", text="Parent")

        if layer.parent and layer.parent.type == 'ARMATURE':
            row = layout.row(align=True)
            row.prop_search(layer, "parent_bone", layer.parent.data, "bones", text="Bone")

        layout.separator()

        col = layout.row(align=True)
        col.prop(layer, "pass_index")

        col = layout.row(align=True)
        col.prop_search(layer, "viewlayer_render", context.scene, "view_layers", text="View Layer")


class DATA_PT_grease_pencil_settings(DataButtonsPanel, Panel):
    bl_label = "Settings"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        grease_pencil = context.grease_pencil
        col = layout.column(align=True)
        col.prop(grease_pencil, "stroke_depth_order", text="Stroke Depth Order")


class DATA_PT_grease_pencil_custom_props(DataButtonsPanel, PropertyPanel, Panel):
    _context_path = "object.data"
    _property_type = bpy.types.GreasePencilv3


classes = (
    GREASE_PENCIL_UL_masks,
    GREASE_PENCIL_MT_layer_mask_add,
    DATA_PT_context_grease_pencil,
    DATA_PT_grease_pencil_layers,
    DATA_PT_grease_pencil_layer_masks,
    DATA_PT_grease_pencil_layer_transform,
    DATA_PT_grease_pencil_layer_relations,
    DATA_PT_grease_pencil_settings,
    DATA_PT_grease_pencil_custom_props,
    GREASE_PENCIL_MT_grease_pencil_add_layer_extra,
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
