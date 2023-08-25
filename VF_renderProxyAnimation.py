bl_info = {
	"name": "VF Render Proxy Animation", # VF Render Proxy Animation is probably better
	"author": "John Einselen - Vectorform LLC, based on work by tstscr(florianfelix)",
	"version": (0, 5),
	"blender": (2, 83, 0),
	"location": "Render > Render Proxy Animation",
	"description": "Temporarily overrides render settings with custom proxy preferences and renders a sequence",
	"warning": "inexperienced developer, use at your own risk",
	"doc_url": "https://github.com/jeinselenVF/VF-BlenderRenderProxyAnimation",
	"tracker_url": "https://github.com/jeinselenVF/VF-BlenderRenderProxyAnimation/issues",
	"category": "Render"}

# https://devtalk.blender.org/t/addon-shortcuts/2410/7

import bpy
from bpy.app.handlers import persistent

###########################################################################
# Render Proxy Animation primary functionality classes

class VF_proxyStart(bpy.types.Operator):
	bl_idname = "render.vf_render_proxy_animation"
	bl_label = "Render Proxy Animation"
	bl_description = "Temporarily reduce render quality for quickly creating animation proxies"

	def execute(self, context):
	# Save original render engine settings
		original_renderEngine = bpy.context.scene.render.engine
		original_renderSamples = bpy.context.scene.eevee.taa_render_samples
	# Save original file format settings
		original_format = bpy.context.scene.render.image_settings.file_format
		original_colormode = bpy.context.scene.render.image_settings.color_mode
		original_colordepth = bpy.context.scene.render.image_settings.color_depth
	# Save original resolution multiplier settings
		original_resolutionMultiplier = bpy.context.scene.render.resolution_percentage
	# Save original nodal compositing settings
		original_compositing = bpy.context.scene.use_nodes

	# Override render engine settings
		bpy.context.scene.render.engine = str(bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_renderEngine)
		bpy.context.scene.eevee.taa_render_samples = bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_renderSamples
	# Override original file format settings
		if bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_format == 'JPEG':
			bpy.context.scene.render.image_settings.file_format = 'JPEG'
		elif bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_format == 'PNG':
			bpy.context.scene.render.image_settings.file_format = 'PNG'
		elif bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_format == 'OPEN_EXR_MULTILAYER':
			bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
	# Override original resolution multiplier settings
		bpy.context.scene.render.resolution_percentage = bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_resolutionMultiplier
	# Override original nodal compositing settings
		if bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_compositing == "ON":
			bpy.context.scene.use_nodes = True
		elif bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_compositing == "OFF":
			bpy.context.scene.use_nodes = False

	# Now render!
		bpy.ops.render.render(animation=True, use_viewport=True)

	# Restore original render engine settings
		bpy.context.scene.render.engine = original_renderEngine
		bpy.context.scene.eevee.taa_render_samples = original_renderSamples
	# Restore original file format settings
		bpy.context.scene.render.image_settings.file_format = original_format
		bpy.context.scene.render.image_settings.color_mode = original_colormode
		bpy.context.scene.render.image_settings.color_depth = original_colordepth
	# Restore original resolution multiplier settings
		bpy.context.scene.render.resolution_percentage = original_resolutionMultiplier
	# Restore original nodal compositing settings
		bpy.context.scene.use_nodes = original_compositing

		return {'FINISHED'}

###########################################################################
# User preferences and UI rendering class

class ProxyRenderPreferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	# Render engine overrides
	proxy_renderEngine: bpy.props.EnumProperty(
		name='Render Engine',
		description='Render engine to use for proxy renders',
		items=[
			('BLENDER_WORKBENCH', 'Workbench', 'Use the Workbench render engine for proxy animations'),
			('BLENDER_EEVEE', 'Eevee', 'Use the Eevee render engine for proxy animations'),
			],
		default='BLENDER_WORKBENCH')
	proxy_renderSamples: bpy.props.IntProperty(
		name="Render Samples",
		description="Render engine to use for proxy renders",
		default=16)

	proxy_format: bpy.props.EnumProperty(
		name='File Format',
		description='Image format used for the proxy render files',
		items=[
			('SCENE', 'Project Setting', 'Same format as set in output panel'),
			('PNG', 'PNG', 'Save as png'),
			('JPEG', 'JPEG', 'Save as jpeg'),
			('OPEN_EXR_MULTILAYER', 'OpenEXR MultiLayer', 'Save as multilayer exr'),
			],
		default='JPEG')

	proxy_resolutionMultiplier: bpy.props.IntProperty(
		name="Resolution Multiplier",
		description="Render engine to use for proxy renders",
		default=100)

	proxy_compositing: bpy.props.EnumProperty(
		name='Node Compositing',
		description='Image format used for the proxy render files',
		items=[
			('SCENE', 'Project Setting', 'Same setting as the project'),
			('ON', 'On', 'Force nodal compositing on when rendering proxies'),
			('OFF', 'Off', 'Force nodal compositing off when rendering proxies'),
			],
		default='OFF')

	def draw(self, context):
		layout = self.layout
		# layout.label(text="Addon Default Preferences")

		grid = layout.grid_flow(row_major=True)
		grid.prop(self, "proxy_renderEngine")
		if bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_renderEngine == "BLENDER_EEVEE":
			grid.prop(self, "proxy_renderSamples")
		grid.prop(self, "proxy_format")
		grid.prop(self, "proxy_compositing")
		grid.prop(self, "proxy_resolutionMultiplier")

###########################################################################
# UI rendering classes

def vf_prepend_menu_renderProxyAnimation(self,context):
	try:
		layout = self.layout
		layout.operator(VF_proxyStart.bl_idname, text="Render Proxy Animation", icon='RENDER_ANIMATION')
	except Exception as exc:
		print(str(exc) + " | Error in Topbar Mt Render when adding to menu")

classes = (ProxyRenderPreferences, VF_proxyStart)

###########################################################################
# Addon registration functions
addon_keymaps = []

def register():
	# register classes
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.TOPBAR_MT_render.prepend(vf_prepend_menu_renderProxyAnimation)
	# handle the keymap
	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon
	if kc:
		km = wm.keyconfigs.addon.keymaps.new(name='Screen Editing', space_type='EMPTY')
		kmi = km.keymap_items.new(VF_proxyStart.bl_idname, 'RET', 'PRESS', ctrl=True, alt=True, shift=True)
		addon_keymaps.append((km, kmi))
	if kc:
		km = wm.keyconfigs.addon.keymaps.new(name='Screen Editing', space_type='EMPTY')
		kmi = km.keymap_items.new(VF_proxyStart.bl_idname, 'RET', 'PRESS', oskey=True, alt=True, shift=True)
		addon_keymaps.append((km, kmi))

def unregister():
	# handle the keymap
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()
	# unregister classes
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	bpy.types.TOPBAR_MT_render.remove(vf_prepend_menu_renderProxyAnimation)

if __name__ == "__main__":
	register()