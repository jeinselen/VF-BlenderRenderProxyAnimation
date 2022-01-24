bl_info = {
	"name": "VF Render Proxy Animation", # VF Render Proxy Animation is probably better
	"author": "John Einselen - Vectorform LLC, based on work by tstscr(florianfelix)",
	"version": (0, 1),
	"blender": (2, 80, 0),
	"location": "Render > Render Proxy Animation",
	"description": "Temporarily overrides render settings with custom proxy preferences and renders a sequence",
	"warning": "inexperienced developer, use at your own risk",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Render"}

# https://devtalk.blender.org/t/addon-shortcuts/2410/7

import bpy
from bpy.app.handlers import persistent

###########################################################################
# Render Proxy Animation primary functionality classes

class VF_proxyStart(bpy.types.Operator):
	bl_idname = "vfproxystart.offset"
	bl_label = "Render Proxy Animation"
	bl_description = "Temporarily reduce render quality for quickly creating animation proxies"

	def execute(self, context):
	# Save original render engine settings
		bpy.context.scene.proxy_render_settings.original_renderEngine = bpy.data.scenes["Scene"].render.engine
		bpy.context.scene.proxy_render_settings.original_renderSamples = bpy.data.scenes["Scene"].eevee.taa_render_samples
	# Save original file format settings
		bpy.context.scene.proxy_render_settings.original_format = bpy.data.scenes["Scene"].render.image_settings.file_format
		bpy.context.scene.proxy_render_settings.original_colormode = bpy.data.scenes["Scene"].render.image_settings.color_mode
		bpy.context.scene.proxy_render_settings.original_colordepth = bpy.data.scenes["Scene"].render.image_settings.color_depth
	# Save original resolution multiplier settings
		bpy.context.scene.proxy_render_settings.original_resolutionMultiplier = bpy.data.scenes["Scene"].render.resolution_percentage
	# Save original nodal compositing settings
		bpy.context.scene.proxy_render_settings.original_compositing = bpy.data.scenes["Scene"].use_nodes

	# Set proxy start variable
		bpy.context.scene.proxy_render_settings.proxy_started = True

	# Override render engine settings
		bpy.data.scenes["Scene"].render.engine = str(bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_renderEngine)
		bpy.data.scenes["Scene"].eevee.taa_render_samples = bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_renderSamples
	# Override original file format settings
		if bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_format == 'JPEG':
			bpy.data.scenes["Scene"].render.image_settings.file_format = 'JPEG'
		elif bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_format == 'PNG':
			bpy.data.scenes["Scene"].render.image_settings.file_format = 'PNG'
		elif bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_format == 'OPEN_EXR_MULTILAYER':
			bpy.data.scenes["Scene"].render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
	# Override original resolution multiplier settings
		bpy.data.scenes["Scene"].render.resolution_percentage = bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_resolutionMultiplier
	# Override original nodal compositing settings
		if bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_compositing == "ON":
			bpy.data.scenes["Scene"].use_nodes = True
		elif bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_compositing == "OFF":
			bpy.data.scenes["Scene"].use_nodes = False

	# Now render!
		print("VF_proxyEnd-1")
		bpy.ops.render.render(animation=True, use_viewport=True)
		print("VF_proxyEnd-2")

	# Restore original render engine settings
		bpy.data.scenes["Scene"].render.engine = bpy.context.scene.proxy_render_settings.original_renderEngine
		bpy.data.scenes["Scene"].eevee.taa_render_samples = bpy.context.scene.proxy_render_settings.original_renderSamples
	# Restore original file format settings
		bpy.data.scenes["Scene"].render.image_settings.file_format = bpy.context.scene.proxy_render_settings.original_format
		bpy.data.scenes["Scene"].render.image_settings.color_mode = bpy.context.scene.proxy_render_settings.original_colormode
		bpy.data.scenes["Scene"].render.image_settings.color_depth = bpy.context.scene.proxy_render_settings.original_colordepth
	# Restore original resolution multiplier settings
		bpy.data.scenes["Scene"].render.resolution_percentage = bpy.context.scene.proxy_render_settings.original_resolutionMultiplier
	# Restore original nodal compositing settings
		bpy.data.scenes["Scene"].use_nodes = bpy.context.scene.proxy_render_settings.original_compositing

	# Set proxy start variable to false, we're done now and everything should be restored correctly
		bpy.context.scene.proxy_render_settings.proxy_started = False

		return {'FINISHED'}

class VF_proxyEnd(bpy.types.Operator):
	bl_idname = "vfproxyend.offset"
	bl_label = "Proxy Animation Finished"
	bl_description = "Restore original render quality settings"

	def execute(self, context):
		print("VF_proxyEnd-1")
		if bpy.context.scene.proxy_render_settings.proxy_started:
		# Restore original render engine settings
			bpy.data.scenes["Scene"].render.engine = bpy.context.scene.proxy_render_settings.original_renderEngine
			bpy.data.scenes["Scene"].eevee.taa_render_samples = bpy.context.scene.proxy_render_settings.original_renderSamples
		# Restore original file format settings
			bpy.data.scenes["Scene"].render.image_settings.file_format = bpy.context.scene.proxy_render_settings.original_format
			bpy.data.scenes["Scene"].render.image_settings.color_mode = bpy.context.scene.proxy_render_settings.original_colormode
			bpy.data.scenes["Scene"].render.image_settings.color_depth = bpy.context.scene.proxy_render_settings.original_colordepth
		# Restore original resolution multiplier settings
			bpy.data.scenes["Scene"].render.resolution_percentage = bpy.context.scene.proxy_render_settings.original_resolutionMultiplier
		# Restore original nodal compositing settings
			bpy.data.scenes["Scene"].use_nodes = bpy.context.scene.proxy_render_settings.original_compositing

		# Set proxy start variable to false, we're done now and everything should be restored correctly
			bpy.context.scene.proxy_render_settings.proxy_started = False

		print("VF_proxyEnd-2")
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
		if bpy.context.preferences.addons['VF_renderProxyAnimation'].preferences.proxy_renderEngine == "EEVEE":
			grid.prop(self, "proxy_renderSamples")
		grid.prop(self, "proxy_format")
		grid.prop(self, "proxy_compositing")
		grid.prop(self, "proxy_resolutionMultiplier")


###########################################################################
# Project settings and UI rendering classes

class ProxyRenderSettings(bpy.types.PropertyGroup):
	# Hidden per-project values
	# Proxy start: this is important to prevent resetting of settings that weren't updated by starting a proxy render!
	proxy_started: bpy.props.BoolProperty(
		name="Proxy Started",
		description="Indicates if proxy rendering was started (disables render setting restoration when false)",
		default=False)

	# Render engine settings
	original_renderEngine: bpy.props.StringProperty(
		name="Original Render Engine",
		description="Stores the scene setting so it can be restored after proxy rendering is completed or cancelled",
		default="")
	original_renderSamples: bpy.props.IntProperty(
		name="Original Render Engine Samples",
		description="Stores the scene setting so it can be restored after proxy rendering is completed or cancelled",
		default=8)

	# File format settings
	original_format: bpy.props.StringProperty(
		name="Original Output Format",
		description="Stores the scene setting so it can be restored after proxy rendering is completed or cancelled",
		default="")
	original_colormode: bpy.props.StringProperty(
		name="Original Color Mode",
		description="Stores the scene setting so it can be restored after proxy rendering is completed or cancelled",
		default="")
	original_colordepth: bpy.props.StringProperty(
		name="Original Color Depth",
		description="Stores the scene setting so it can be restored after proxy rendering is completed or cancelled",
		default="")

	# Resolution settings
	original_resolutionMultiplier: bpy.props.IntProperty(
		name="Original Resolution Multiplier",
		description="Stores the scene setting so it can be restored after proxy rendering is completed or cancelled",
		default=100)

	# Compositing settings
	original_compositing: bpy.props.BoolProperty(
		name="Original Color Depth",
		description="Stores the scene setting so it can be restored after proxy rendering is completed or cancelled",
		default=True)

def vf_prepend_menu_renderProxyAnimation(self,context):
	try:
		layout = self.layout
		layout.operator(VF_proxyStart.bl_idname, text="Render Proxy Animation", icon='RENDER_ANIMATION')
	except Exception as exc:
		print(str(exc) + " | Error in Topbar Mt Render when adding to menu")

classes = (ProxyRenderPreferences, ProxyRenderSettings, VF_proxyStart)# , VF_proxyEnd)

###########################################################################
# Addon registration functions
addon_keymaps = []

def register():
	# register classes
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.proxy_render_settings = bpy.props.PointerProperty(type=ProxyRenderSettings)
	bpy.types.TOPBAR_MT_render.prepend(vf_prepend_menu_renderProxyAnimation)
	bpy.app.handlers.render_cancel.append(VF_proxyEnd)
	bpy.app.handlers.render_complete.append(VF_proxyEnd)
	# handle the keymap
	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon
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
	del bpy.types.Scene.proxy_render_settings
	bpy.types.TOPBAR_MT_render.remove(vf_prepend_menu_renderProxyAnimation)
	bpy.app.handlers.render_cancel.remove(VF_proxyEnd)
	bpy.app.handlers.render_complete.remove(VF_proxyEnd)

if __name__ == "__main__":
	register()
