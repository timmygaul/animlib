"""Creates a Maya user interface for the animlib toolset."""

import maya.cmds as cmds
import animlib.defaults
import animlib.file
import animlib.apply

#======================================================================
def build():
    """Builds a UI for the animlib toolset."""
    
    # Create the window.
    if cmds.window("animlib_ui", exists=True):
        cmds.deleteUI("animlib_ui")
    window = cmds.window("animlib_ui", width=500, title="Animlib UI")
    
    # Create layouts.
    form = cmds.formLayout('animlib_form', numberOfDivisions=100)
    
    # Create the file selection controls.
    file_frame = cmds.frameLayout(label='Import File',
                                  borderStyle='in',
                                  parent=form,
                                  labelVisible=False)
    cmds.formLayout(form,
                    edit=True,
                    attachForm=[(file_frame, 'left', 0),
                                (file_frame, 'right', 0),
                                (file_frame, 'top', 0),])
    form_file = cmds.formLayout('file_form', numberOfDivisions=100)
    lbl_file = cmds.text(label='File: ', height=20)
    txt_file = cmds.textField('animlib_filepath',
                              changeCommand=file_update)
    btn_file = cmds.button('btn_filepath',
                            label = '...',
                            width = 30,
                            height = 20,
                            command=open_file)
    cmds.formLayout(form_file,
                    edit=True,
                    attachForm=[(lbl_file, 'left', 5),
                                (lbl_file, 'bottom', 3),
                                (lbl_file, 'top', 3),
                                (btn_file, 'right', 5),
                                (btn_file, 'top', 3),
                                (btn_file, 'bottom', 3),
                                (txt_file, 'bottom', 3),
                                (txt_file, 'top', 3),],
                    attachControl=[(txt_file, 'left', 0, lbl_file),
                                   (txt_file, 'right', 2, btn_file),],)
                                   
                                
    # Create the apply buttons
    apply_row = cmds.formLayout(parent = form)
    cmds.formLayout(form,
                    edit=True,
                    attachForm=[(apply_row, 'left', 0),
                                (apply_row, 'right', 0),
                                (apply_row, 'bottom', 0),])
    btn_apply = cmds.button('btn_apply',
                            label = 'Apply',
                            height = 30,
                            command=apply_file)
    cmds.formLayout(apply_row,
                    edit=True,
                    attachForm=[(btn_apply, 'left', 0),
                                (btn_apply, 'right', 0),
                                (btn_apply, 'bottom', 0),])
    
    
    # Create the options
    options_scr = cmds.scrollLayout(parent = form, childResizable=True)
    cmds.formLayout(form,
                    edit=True,
                    attachForm=[(options_scr, 'left', 0),
                                (options_scr, 'right', 0),],
                    attachControl=[(options_scr, 'top', 0, file_frame),
                                   (options_scr, 'bottom', 2, apply_row),],)
    col = cmds.columnLayout(adjustableColumn=True, parent=options_scr, columnAttach = ('both',0))
    
    # Create the Info frame
    cmds.frameLayout('info',
                     label='File information',
                     borderStyle='out',
                     collapsable=True,
                     parent=col,)
    form_info = cmds.formLayout('file_form', numberOfDivisions=100)
    lbl_date = cmds.text(label='Date: ', height=20)
    txt_date = cmds.textField('animlib_date', editable=False)
    cmds.formLayout(form_info,
                    edit=True,
                    attachForm=[(lbl_date, 'left', 5),
                                (lbl_date, 'top', 3),
                                (txt_date, 'right', 5),
                                (txt_date, 'top', 3),],
                    attachControl=[(txt_date, 'left', 0, lbl_date),],)
    
    ref_frame = cmds.frameLayout('animlib_ref_frame',
                                 label='Reference Remap',
                                 borderStyle='out',
                                 collapsable=True,
                                 parent=col,)
    cmds.frameLayout('time_frame',
                     label='Animation Curve Remap',
                     borderStyle='out',
                     collapsable=True,
                     parent=col,)
    
    # Prove it's working.
    if cmds.dockControl('animlib_ui_dock', exists=True):
        cmds.deleteUI('animlib_ui_dock')
    cmds.dockControl('animlib_ui_dock',
                     label = 'Animlib UI',
                     area='right',
                     content=window,
                     width=427,
                     allowedArea=['right', 'left'] )
    file_update('')
                     
    
    
#======================================================================
def file_update(filepath):
    try:
        data = animlib.file.read(filepath)
    except:
        cmds.textField('animlib_filepath',
                        edit=True,
                       backgroundColor=[0.2,0,0],
                       enableBackground = True)
        cmds.textField('animlib_date', edit=True, text='')
        populate_ref_remap([])
        return
    cmds.textField('animlib_filepath',
                    edit=True,
                       backgroundColor=[0.15,0.2,0.15],
                       enableBackground = True)
    (info_data,
     dependency_data,
     reference_data,
     anim_curve_data,
     constraint_data,
     pairblend_data,
     channel_data,) = data
    if 'time' in info_data:
        cmds.textField('animlib_date',
                        edit=True,
                        text=info_data['time'])
    else:
        cmds.textField('animlib_date', edit=True, text='')
    if 'references' in info_data:
        populate_ref_remap(info_data['references'].keys())
        
        
#======================================================================
def populate_ref_remap(namespaces):
    if cmds.columnLayout('animlib_ref_col', exists=True):
        cmds.deleteUI('animlib_ref_col')
    ref_col = cmds.columnLayout('animlib_ref_col',
                                adjustableColumn=True, 
                                parent='animlib_ref_frame',
                                columnAttach = ('both',0))
    for namespace in namespaces:
        cmds.setParent('animlib_ref_col')
        
        nsp_form = cmds.formLayout('animlib_ref_'+namespace+'_frm',
                                   numberOfDivisions=100)
        lbl_nsp = cmds.text(label=namespace, height=20, align='right')
        txt_nsp = cmds.textField('animlib_ref_'+namespace+'_txt',
                                  editable=True,
                                  text=namespace)
        cmds.formLayout(nsp_form,
                        edit=True,
                        attachForm=[(lbl_nsp, 'top', 3),
                                    (txt_nsp, 'right', 5),
                                    (txt_nsp, 'top', 3),],
                        attachPosition=[(txt_nsp, 'left', 0, 33),
                                        (lbl_nsp, 'right', 5, 33)],) 
    nsp_form = cmds.formLayout('animlib_ref_checkbox_frm',
                                   numberOfDivisions=100,
                  parent=ref_col)   
    cbx = cmds.checkBox('animlib_force_build',
                        label='Build Next Available Namespace',)
    cmds.formLayout(nsp_form,
                    edit=True,
                    attachForm=[(cbx, 'top', 5),
                                (cbx, 'bottom', 5),],
                    attachPosition=[(cbx, 'left', 0, 33),],) 
                  
                        
#======================================================================
def read_ref_map(namespaces):
    remap = {}
    for namespace in namespaces:
        text = cmds.textField('animlib_ref_'+namespace+'_txt',
                              query=True,
                              text=True)
        if not text.startswith(':'):
            text = ':' + text
        remap[namespace] = (text, 'connections')
        
    return remap
                        
                        
#======================================================================
def check_ref_map(input):
    remap = {}
    for namespace in namespaces:
        text = cmds.textField('animlib_ref_'+namespace+'_txt',
                              query=True,
                              text=True)
        if not text.startswith(':'):
            text = ':' + text
        remap[namespace] = (text, 'connections')
        
    return remap
                        

        
#======================================================================
def apply_file(input):
    filepath = cmds.textField('animlib_filepath', query=True, text=True)
    data = animlib.file.read(filepath)
    (info_data,
     dependency_data,
     reference_data,
     anim_curve_data,
     constraint_data,
     pairblend_data,
     channel_data,) = data
    if 'references' in info_data:
        reference_remap = read_ref_map(info_data['references'].keys())
    else:
        reference_remap = None
    force_build_state = cmds.checkBox('animlib_force_build', query=True, value=True)
    result = animlib.apply.build(data,
                                 force_build=force_build_state,
                                 reference_filter=reference_remap)
    
#======================================================================
def open_file(input):
    if not cmds.textField('animlib_filepath', exists=True):
        cmds.error('Could not find UI filepath text field:' + txt_file)
    basicFilter = "*.anim"
    new_path = cmds.fileDialog2(startingDirectory =                         animlib.defaults.DEFAULT_FILEPATH,
                                fileFilter=basicFilter,
                                dialogStyle=2,
                                fileMode = 1)[0]
    cmds.textField('animlib_filepath',
                    edit=True,
                    text=str(new_path))
    file_update(new_path)