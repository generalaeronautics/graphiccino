import dearpygui.dearpygui as dpg
from numpy import tile
import polars
from DataFlash import DataFlash
from GUItheme import PlotWindow_theme
import ctypes

try:
    user32 = ctypes.windll.user32
    #screensize to initialize the GUI window
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
except:
    #Incase above method got any error means then window will use this
    screensize = (1400, 600)

#Initializing DataFrame decoder
DF = DataFlash()

app_title = 'Graphiccino'

#Initializing GUI
dpg.create_context()
dpg.create_viewport(title=app_title,
                    width=int(screensize[0]*0.9), height=int(screensize[1]*0.9) , 
                    x_pos=int(screensize[0]*0.05), y_pos=int(screensize[1]*0.05))

#To filter data types in data window
def filter_callback(sender, filter_string):
    dpg.set_value("filter_id", filter_string)

#To clear plot window only
def clear_plot():
    dpg.delete_item(PlotWindow, children_only=True)
    plot_window()

#To reset all GUI window
def clear_all():
    dpg.delete_item(dtypeslist, children_only=True)
    dpg.delete_item(PARMS_Window, children_only=True)
    dpg.delete_item(DataExportWindow, children_only=True)
    dpg.delete_item(PlotWindow, children_only=True)
    dpg.set_viewport_title(app_title)
    plot_window()

#Function to auto resize window if user change window size.
def viewport_resize():
    if dpg.get_viewport_width() != int(screensize[0]*0.9) or dpg.get_viewport_height() != int(screensize[1]*0.9):
        dpg.configure_item('Data_Window', width=int(dpg.get_viewport_width() * 0.20))
        dpg.configure_item('Data_Window', height=int(dpg.get_viewport_height() * 0.935))
        dpg.configure_item('Plot_Window', width=int(dpg.get_viewport_width() * 0.789))
        dpg.configure_item('Plot_Window', height=int(dpg.get_viewport_height() * 0.935))
        dpg.configure_item('Plot_Window', pos=(int(dpg.get_viewport_width() * 0.20), 1))

#Function to export Data type into as CSV
def csv_export(sender, app_data, user_data):
    dpg.configure_item("loading_popup", show=True)
    DF.DFcsvexport(dpg.get_value('DataExport')).write_csv(f"{DF.filename}_{dpg.get_value('DataExport')}.csv", sep=",")
    dpg.configure_item("loading_popup", show=False)

def drop_plotter(sender, app_data, user_data):
    plotable = None
    dpg.configure_item("loading_popup", show=True)
    if DF.DFDict[app_data[0]].shape[0] == 0:
        plotable = DF.DFextract(app_data[0])
    if plotable != False:
        if app_data[3]['multi_id'] != None:
            xaxis_list = ((DF.DFDict[app_data[0]].filter(polars.col("I") == app_data[3]['multi_id'])['TimeUS']) * 
            (DF.DFcolumn_multiplier[app_data[0]]['TimeUS'])).to_list()
            if DF.DFcolumn_multiplier[app_data[0]][app_data[1]] == 0:
                yaxis_list = DF.DFDict[app_data[0]].filter(polars.col("I") == app_data[3]['multi_id'])[app_data[1]].to_list()
            else:
                yaxis_list = ((DF.DFDict[app_data[0]].filter(polars.col("I") == app_data[3]['multi_id'])[app_data[1]]) 
                                        * (DF.DFcolumn_multiplier[app_data[0]][app_data[1]])).to_list()
        else:
            xaxis_list = ((DF.DFDict[app_data[0]]['TimeUS']) * (DF.DFcolumn_multiplier[app_data[0]]['TimeUS'])).to_list()
            if DF.DFcolumn_multiplier[app_data[0]][app_data[1]] == 0:
                yaxis_list = DF.DFDict[app_data[0]][app_data[1]].to_list()
            else:
                yaxis_list = ((DF.DFDict[app_data[0]][app_data[1]]) * (DF.DFcolumn_multiplier[app_data[0]][app_data[1]])).to_list()
        dplot = dpg.get_item_info(sender)["children"][1][0]
        dplot_axis = dpg.get_item_user_data(dpg.get_item_info(dplot)['parent'])
        dpg.add_line_series(xaxis_list, yaxis_list, label=f'{app_data[0]} - {app_data[2]}', parent=dplot)
        dpg.fit_axis_data(dplot_axis['x'])
        dpg.fit_axis_data(dplot_axis['y'])
        dpg.set_item_label(dplot_axis['x'], 'Time(Sec)')
        dpg.set_item_label(dplot_axis['y'], f'{app_data[1]}({DF.DFcolumn_unit[app_data[0]][app_data[1]]})')
        dpg.add_button(label="Delete Series", user_data = dpg.last_item(), parent=dpg.last_item(), callback=lambda s, a, u: dpg.delete_item(u))
        dpg.configure_item("loading_popup", show=False)
    else:
        dpg.configure_item("loading_popup", show=False)
        dpg.set_value("error_text", f'{app_data[0]} is not Plottable or Empty')
        dpg.configure_item('error_window', show=True)

def plot_window(_='',__='', plottype='1x1'):
    if plottype == '1x1':
        dpg.delete_item(PlotWindow, children_only=True)
        with dpg.plot(label='Plot', width=-1, height=-1, user_data={'x': 'x_axis', 'y': 'y_axis'}, 
                        drop_callback=drop_plotter, payload_type="plotting", tag='1x1', parent=PlotWindow, no_title=True):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="x", tag='x_axis')
            dpg.add_plot_axis(dpg.mvYAxis, label="y", tag='y_axis')
    elif plottype == '1x2':
        dpg.delete_item(PlotWindow, children_only=True)
        with dpg.subplots(1,2, label="", width=-1, height=-1, link_all_x=True, tag='1x2', parent=PlotWindow):
            for i in range(2):
                with dpg.plot(label=' ', user_data={'x': f'x_axis_{i}', 'y': f'y_axis_{i}'}, 
                                drop_callback=drop_plotter, payload_type="plotting"):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="x", tag=f'x_axis_{i}')
                    dpg.add_plot_axis(dpg.mvYAxis, label="y", tag=f'y_axis_{i}')
    elif plottype == '2x2':
        dpg.delete_item(PlotWindow, children_only=True)
        with dpg.subplots(2,2, label="", width=-1, height=-1, link_all_x=True, tag='2x2', parent=PlotWindow):
            for i in range(4):
                with dpg.plot(label=' ', user_data={'x': f'x_axis_{i}', 'y': f'y_axis_{i}'}, 
                                drop_callback=drop_plotter, payload_type="plotting"):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="x",  tag=f'x_axis_{i}')
                    dpg.add_plot_axis(dpg.mvYAxis, label="y", tag=f'y_axis_{i}')

def params_update():
    if DF.DFDict['PARM'].shape[0] == 0:
            DF.DFextract('PARM')
    with dpg.table(header_row=False, row_background=True,
                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True, parent=PARMS_Window):       
        dpg.add_table_column()
        dpg.add_table_column()
        for name, value in zip(DF.DFDict['PARM'].sort('Name')['Name'], DF.DFDict['PARM'].sort('Name')['Value']):
            with dpg.table_row():
                for i in range(0, 2):
                    if i == 0:
                        dpg.add_text(name)
                    elif i == 1:
                        dpg.add_text(value)

#Function to initialize the BIN file with DataFlash decoder
def dtypeslist_update(binfile):
    dpg.configure_item("loading_popup", show=True)
    try:
        DF.initialize(binfile)
    except FileNotFoundError:
        dpg.configure_item("loading_popup", show=False)
        clear_all()
        dpg.set_viewport_title(app_title)
        dpg.set_value("error_text", 'Unsupported file or File is not properly selected!')
        dpg.configure_item('error_window', show=True)
    else:
        dpg.configure_item("loading_popup", show=False)
        clear_all()
        dpg.set_viewport_title(binfile)
        for dtype in DF.DFDict.keys():
            with dpg.tree_node(label=dtype, filter_key=dtype, parent=dtypeslist):
                if 'I' in DF.DFDict[dtype].columns and len(DF.DFcheckmulti(dtype)) > 1:
                    for multi in range(len(DF.DFcheckmulti(dtype))):
                        with dpg.tree_node(label=multi):
                            for columns in DF.DFDict[dtype].columns:
                                if DF.DFDict[dtype][columns].dtype != polars.datatypes.Utf8 and columns != 'TimeUS':
                                    dpg.add_button(label=columns, user_data={'dtype': dtype, 'column': columns})
                                    with dpg.drag_payload(parent=dpg.last_item(), drag_data=(dtype, columns, f'{columns}[{multi}]', {'multi_id': multi}), 
                                                            payload_type="plotting"):
                                        dpg.add_text(columns)
                else:
                    for columns in DF.DFDict[dtype].columns:
                        if DF.DFDict[dtype][columns].dtype != polars.datatypes.Utf8 and columns != 'TimeUS':
                            dpg.add_button(label=columns, user_data={'dtype': dtype, 'column': columns})
                            with dpg.drag_payload(parent=dpg.last_item(), drag_data=(dtype, columns, columns, {'multi_id': None}), 
                                                    payload_type="plotting"):
                                dpg.add_text(columns)
        params_update()
        dpg.add_text("Select Data", parent=DataExportWindow)
        dpg.add_combo(sorted(list(DF.DFcolumn_list.keys())), 
                            height_mode=dpg.mvComboHeight_Regular, parent=DataExportWindow, tag='DataExport')
        dpg.add_button(label='Export', callback=csv_export, parent=DataExportWindow)

#File Dialog popup
with dpg.file_dialog(label="File Dialog", 
                    width=600, height=400 , show=False, 
                    callback=lambda s, a, u: dtypeslist_update(a['file_path_name']), tag="filedialog"):
            dpg.add_file_extension(".bin", color=(255, 255, 0, 255))
            dpg.add_file_extension(".BIN", color=(255, 255, 0, 255))
            dpg.add_file_extension(".*", color=(255, 255, 255, 255))

#Menu
with dpg.viewport_menu_bar():
    dpg.add_menu_item(label="Open File", callback=lambda: dpg.configure_item("filedialog", show=True))
    with dpg.menu(label="Plot Window"):
        dpg.add_menu_item(label="1 row x 1 column", user_data='1x1', callback=plot_window)
        dpg.add_menu_item(label="1 row x 2 column", user_data='1x2', callback=plot_window)
        dpg.add_menu_item(label="2 row x 2 column", user_data='2x2', callback=plot_window) 
    dpg.add_menu_item(label="Clear Plot", callback=clear_plot)
    dpg.add_menu_item(label="Clear All", callback=clear_all)

#Data Window
with dpg.window(label='Data Window', 
                width=int(dpg.get_viewport_width() * 0.20), 
                height=int(dpg.get_viewport_height() * 0.930), 
                pos=(0, 0), no_move=True, no_close=True, no_collapse=True, tag='Data_Window'):
    with dpg.tab_bar():
        with dpg.tab(label="Data"):
            dpg.add_input_text(label="Filter",callback=filter_callback)
            with dpg.child_window(label='Datas', autosize_y=True) as SelectWindow:
                with dpg.filter_set(id="filter_id") as dtypeslist:
                    pass
        with dpg.tab(label="PARM"):
            with dpg.child_window(label='PARM"', autosize_y=True) as PARMS_Window:
                pass

        with dpg.tab(label='Export') as ExportWindow:
            with dpg.child_window(label='Datas', autosize_y=True) as DataExportWindow:
                pass

#Plot Window
with dpg.window(label='Plot Window', 
                width=int(dpg.get_viewport_width() * 0.789), 
                height=int(dpg.get_viewport_height() * 0.930), 
                pos=(int(dpg.get_viewport_width() * 0.20), 1), 
                no_move=True, no_close=True, no_collapse=True, tag='Plot_Window') as PlotWindow:
   plot_window()

#Loading Popup
#Usage:
# dpg.configure_item("loading_popup", show=True) #To show error popup and show=False to close the Loading popup
with dpg.window(label="Loading Popup", modal=True, show=False, tag="loading_popup", no_title_bar=True, pos=(750, 250)):
    dpg.add_text("\n\n  Loading")

#Error Popup
#Usage:
# dpg.set_value("error_text", '{user_error_message}') #Replace {user_error_message} with what ever we needed.
# dpg.configure_item('error_window', show=True) #To  show error popup and show=False to close the Error popup
with dpg.window(label="Error/Warning", modal=True, 
                height=75,show=False, pos=(550, 75), 
                no_title_bar=False, no_close=True, no_collapse=True, tag="error_window") as ErrorWindow:
    dpg.add_text('Error Message', tag='error_text')
    dpg.add_button(label='Close', pos=(150, 60), callback= lambda: dpg.configure_item('error_window', show=False))

#Binding theme and Window
dpg.bind_item_theme(PlotWindow, PlotWindow_theme)

#Autoresize window if user changed.
dpg.set_viewport_resize_callback(viewport_resize)

#Starting GUI
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()