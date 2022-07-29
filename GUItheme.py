import dearpygui.dearpygui as dpg

dpg.create_context()

with dpg.theme() as PlotWindow_theme:
    with dpg.theme_component(dpg.mvPlot):
        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2, category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_PlotBg, (255,255,255), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_LegendText, (255,255,255), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_TitleText, (0,0,0), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_XAxis, (0,0,0), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_YAxis, (0,0,0), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_XAxisGrid, (75,75,75), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_YAxisGrid, (75,75,75), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_LegendText, (0,0,0), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_LegendBg, (240,240,240), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_FrameBg, (240,240,240), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_InlayText, (0,0,0), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_style(dpg.mvPlotStyleVar_FitPadding, 0.05, 0.05, category=dpg.mvThemeCat_Plots)