"""Creates a Maya user interface for the animlib toolset."""

import maya.cmds as cmds
import re
import animlib.defaults
import animlib.file
import animlib.apply

#======================================================================
def build():
    """Builds a UI for the animlib toolset."""
    
    # Create the window.
    if cmds.window("animlib_ui", exists=True):
        cmds.deleteUI("animlib_ui")
    window = cmds.window("animlib_ui", title="Animlib UI")
    
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
                     area='left',
                     width=427,
                     content=window,
                     allowedArea=['right', 'left'] )
    file_update('')
                     
    
    
#======================================================================
def file_update(filepath):
    try:
        data = animlib.file.read(filepath)
    except:
        cmds.textField('animlib_filepath',
                        edit=True,
                       backgroundColor=[0.8,0.4,0.4],
                       enableBackground = True)
        cmds.textField('animlib_date', edit=True, text='')
        populate_ref_remap([])
        return
    cmds.textField('animlib_filepath',
                    edit=True,
                       backgroundColor=[0.4,0.8,0.4],
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
def ref_menu_item(nsp, new_nsp):
    print ('Menu item update received: '+nsp+' - '+new_nsp)
    if new_nsp == 'Custom...':
        cmds.setFocus('animlib_ref_'+nsp+'_txt')
        return
    if new_nsp == 'Default':
        cmds.textField('animlib_ref_'+nsp+'_txt',
                       edit=True,
                       text = nsp)
    else:
        cmds.textField('animlib_ref_'+nsp+'_txt',
                       edit=True,
                       text = new_nsp)
    ref_update(None)
        
    
#======================================================================
def ref_menu_update(value):
    cmds.popupMenu('animlib_ref_'+value+'_menu',
                   edit=True,
                   deleteAllItems=True)
        
    cmds.menuItem(label='None',         
                  parent='animlib_ref_'+value+'_menu',
                  command=lambda x, y=value, z='':ref_menu_item(y, z),)
    cmds.menuItem(label='Custom',         
                  parent='animlib_ref_'+value+'_menu',
                  command=lambda x, y=value, z='Custom...':ref_menu_item(y, z),)
        
    cmds.menuItem(label='Default',         
                  parent='animlib_ref_'+value+'_menu',
                  command=lambda x, y=value, z='Default':ref_menu_item(y, z),)
    scn_nsps = all_ref_namespaces()
    cmds.menuItem(label='-----------------------',         
                  parent='animlib_ref_'+value+'_menu',
                  command=lambda x, y=value, z='':ref_menu_item(y, z),)
    if scn_nsps:
        scn_nsps.sort()
        for scn_nsp in scn_nsps:      
            if not scn_nsp.startswith(':'):
                scn_nsp = ':' + scn_nsp
            cmds.menuItem(label=scn_nsp,         
                          parent='animlib_ref_'+value+'_menu',
                          command=lambda x, y=value, z=scn_nsp:ref_menu_item(y, z),)
        
    else:
        cmds.menuItem(label='No referenced rigs found',         
                      parent='animlib_ref_'+value+'_menu',
                      enable=False)

#======================================================================
def ref_mode_update(*args):
    print args
    
#======================================================================
def ref_update(value):
    build_colour = [0.4,0.8,0.4]
    apply_colour = [0.3,0.55,1]
    skip_colour = [0.8,0.4,0.4]
    force_build_state = cmds.radioButton('animlib_force_build',
                                      query=True,
                                      select=True)
    build_unfound_state = cmds.radioButton('animlib_build_unfound',
                                      query=True,
                                      select=True)
                                      
                                      
    namespaces = cmds.text('animlib_ref_nsp_list', query=True,
                         label=True).split('#')
    for namespace in namespaces:
        if namespace:
            field = 'animlib_ref_'+namespace+'_txt'
            
            new_nsp = cmds.textField(field,
                                     query=True,
                                     text=True)    
                                         
            if not new_nsp.startswith(':'):
                new_nsp = ':' + new_nsp
                cmds.textField(field,
                               edit=True,
                               text = new_nsp)
                               
            if new_nsp==':':
                cmds.textField(field,
                               edit=True,
                               text = '',
                               backgroundColor = skip_colour)
                continue
            
            if force_build_state:      
                cmds.textField(field,
                               edit=True,
                               backgroundColor = build_colour)
                continue
                    
                
            if cmds.namespace(exists=new_nsp):
                cmds.textField(field,
                               edit=True,
                               backgroundColor = apply_colour)
                continue
                
            if build_unfound_state:
                cmds.textField(field,
                               edit=True,
                               backgroundColor = build_colour)
                continue
                
            cmds.textField(field,
                           edit=True,
                           backgroundColor = skip_colour)
        
    
#======================================================================
def populate_ref_remap(namespaces):
    radio_state = None
    if cmds.radioCollection('animlib_ref_radio', query=True, exists=True):
        radio_state = cmds.radioCollection('animlib_ref_radio', 
                                            query=True, select=True)
                                            
    if cmds.columnLayout('animlib_ref_col', exists=True):
        cmds.deleteUI('animlib_ref_col')
    ref_col = cmds.columnLayout('animlib_ref_col',
                                adjustableColumn=True, 
                                parent='animlib_ref_frame',
                                columnAttach = ('both',0))
    for namespace in namespaces:
        cmds.setParent('animlib_ref_col')
        
        nsp_form = cmds.formLayout('animlib_ref_'+namespace+'_frm',
                                   numberOfDivisions=100,
                                   width=420)
        lbl_nsp = cmds.text(label=namespace+'  > ', height=20, align='right')
        cmd = '"{0}"'.format(namespace)
        txt_nsp = cmds.textField('animlib_ref_'+namespace+'_txt',
                                  editable=True,
                                  text=namespace,
                                  placeholderText='None',
                                  changeCommand=lambda x, y=namespace:ref_update(y),
                                  enterCommand=lambda x, y=namespace:ref_update(y),
                                  receiveFocusCommand=lambda x, y=namespace:ref_update(y),)
        cmds.popupMenu('animlib_ref_'+namespace+'_menu',
                       postMenuCommand=lambda x, y, z=namespace:ref_menu_update(z),
                )
        

        mnu_mod = cmds.optionMenu('animlib_ref_'+namespace+'_mode',
                                  changeCommand=lambda x, y=namespace:ref_mode_update(x,y) )
        cmds.menuItem( label='All Inputs' )
        cmds.menuItem( label='Values' )
        cmds.menuItem( label='Curves/Values' )
        cmds.menuItem( label='Constraints' )
        cmds.menuItem( label='No Inputs' )
        cmds.formLayout(nsp_form,
                        edit=True,
                        attachForm=[(lbl_nsp, 'top', 3),
                                    (mnu_mod, 'top', 3),
                                    (mnu_mod, 'right', 5),
                                    (txt_nsp, 'right', 120),
                                    (txt_nsp, 'top', 3),],
                        attachControl=[
                                    (mnu_mod, 'left', 5, txt_nsp),],
                        attachPosition=[(txt_nsp, 'left', 0, 33),
                                        (lbl_nsp, 'right', 5, 33)],) 
    nsp_form = cmds.formLayout('animlib_ref_radioButton_frm',
                                   numberOfDivisions=100,
                  parent=ref_col)   
    sep = cmds.separator( height=10, style='in' )
    lbl_nsp = cmds.text(label='Bring new referenced rigs into the scene:', height=20, align='right')
    radcol = cmds.radioCollection('animlib_ref_radio')
    rad1 = cmds.radioButton('animlib_build_unfound',
                        label='If the rig\'s namespace does not exist yet',
                        collection = radcol)
    rad2 = cmds.radioButton('animlib_force_build',
                        label='Whether the namespace exists or not',
                        collection = radcol,)
    rad3 = cmds.radioButton('animlib_no_new',
                        label='Never, only apply to existing namespaces',
                        collection = radcol,)
    nsp_list = cmds.text('animlib_ref_nsp_list',
                         label='#'.join(namespaces), visible=False)
    cmds.formLayout(nsp_form,
                    edit=True,
                    attachForm=[(sep, 'top', 3),
                                (sep, 'left', 3),
                                (sep, 'right', 3),
                                (lbl_nsp, 'top', 10),
                                (rad3, 'bottom', 5),],
                    attachControl=[(rad1, 'top', 5, lbl_nsp,),
                                   (rad2, 'top', 5, rad1),
                                   (rad3, 'top', 5, rad2),],
                    attachPosition=[(lbl_nsp, 'left', -80, 33),
                                    (rad1, 'left', 0, 33),
                                    (rad2, 'left', 0, 33),
                                    (rad3, 'left', 0, 33),],) 
    if radio_state and cmds.radioButton(radio_state, query=True, exists=True):
        cmds.radioButton(radio_state, edit=True, select=True)
    else:
        cmds.radioButton('animlib_build_unfound',
                        edit=True,
                        select=True)
    for rad in (rad1, rad2, rad3):
        cmds.radioButton(rad, edit=True, changeCommand = lambda x, y=None:ref_update(y),)
    ref_update(None)
                   
#======================================================================
def read_ref_map(namespaces):
    remap = {}
    for namespace in namespaces:
        text = cmds.textField('animlib_ref_'+namespace+'_txt',
                              query=True,
                              text=True)
        if not text.startswith(':'):
            text = ':' + text
            remap[namespace] = (namespace, 'skip')
        if text != ':':
            mode = cmds.optionMenu('animlib_ref_'+namespace+'_mode',
                                   query=True,
                                   value=True)
            mode_convert = {'No Inputs': 'pass',
                            'Values': 'values',
                            'Curves/Values': 'curves',
                            'Constraints': 'constraints',
                            'All Inputs': 'connections'}
            remap[namespace] = (text, mode_convert[mode])
    return remap
                        
                        
#======================================================================
def check_ref_map(input):
    remap = {}
        
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
    if 'references' in info_data.keys():
        reference_remap = read_ref_map(info_data['references'].keys())
    else:
        reference_remap = None
    print '!!!!!'+str(reference_remap)
    force_build_state = cmds.radioButton('animlib_force_build',         
                                         query=True,
                                         select=True)
    build_unfound = cmds.radioButton('animlib_build_unfound',         
                                         query=True,
                                         select=True)
    result = animlib.apply.build(data,
                                 force_build=force_build_state,
                                 reference_filter=reference_remap,
                                 reference_unfound=build_unfound)
    ref_update(None)
    
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
    
    
    
    
#=======
def all_ref_namespaces():
    all_refs = cmds.file(query=True, list=True)
    ref_re = re.compile(r'[a-zA-Z0-9._\-:/\\]*\.(ma|mb)(\{\d\})?')
    file_refs = [x for x in all_refs if re.match( ref_re, x)]
    #! Need to let this account for numbered references
    namespaces = [cmds.file(x, query=True, namespace=True) for x in file_refs]
    return namespaces
    
    