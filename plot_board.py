#!/Applications/Kicad/kicad.app/Contents/Resources/python
'''

    https://github.com/aktos-io/kicad-tools/blob/master/kicad-gen-fabrication

    A python script example to create various plot files from a board:
    Fab files
    Doc files
    Gerber files

    Important note:
        this python script does not plot frame references.
        the reason is it is not yet possible from a python script because plotting
        plot frame references needs loading the corresponding page layout file
        (.wks file) or the default template.

        This info (the page layout template) is not stored in the board, and therefore
        not available.

        Do not try to change SetPlotFrameRef(False) to SetPlotFrameRef(true)
        the result is the pcbnew lib will crash if you try to plot
        the unknown frame references template.
'''
import os
import sys

PYTHON_PATH = os.environ.get("PYTHON_PATH")
if PYTHON_PATH != None:
    sys.path.insert(0, PYTHON_PATH)

import pcbnew
from pcbnew import *
import numpy as np

# COLOR4D(red, green, blue, alpha)
YELLOW = pcbnew.COLOR4D(1.00, 1.0, 0.0, 1.0)
GREEN = pcbnew.COLOR4D(0.0, 1.0, 0.0, 1.0)
RED = pcbnew.COLOR4D(1.0, 0.0, 0.0, 1.0)
BLUE = pcbnew.COLOR4D(0.0, 0.0, 1.0, 1.0)
ORANGE = pcbnew.COLOR4D(1.0, 0.50, 0.0, 1.0)
CYAN = pcbnew.COLOR4D(0.0, 0.75, 1.0, 1.0)
MAGENTA = pcbnew.COLOR4D(1.0, 0.0, 1.0, 1.0)
GREY =  pcbnew.COLOR4D(0.5, 0.5, 0.5, 1.0)
BLACK =  pcbnew.COLOR4D(0.0, 0.0, 0.0, 1.0)

F_Cu = 0
In1_Cu = 1
In2_Cu = 2
In3_Cu = 3
In4_Cu = 4
In5_Cu = 5
In6_Cu = 6
In7_Cu = 7
In8_Cu = 8
In9_Cu = 9
In10_Cu = 10
In11_Cu = 11
In12_Cu = 12
In13_Cu = 13
In14_Cu = 14
In15_Cu = 15
In16_Cu = 16
In17_Cu = 17
In18_Cu = 18
In19_Cu = 19
In20_Cu = 20
In21_Cu = 21
In22_Cu = 22
In23_Cu = 23
In24_Cu = 24
In25_Cu = 25
In26_Cu = 26
In27_Cu = 27
In28_Cu = 28
In29_Cu = 29
In30_Cu = 30
B_Cu = 31
B_Adhes = 32
F_Adhes = 33
B_Paste = 34
F_Paste = 35
B_SilkS = 36
F_SilkS = 37
B_Mask = 38
F_Mask = 39
Dwgs_User = 40
Cmts_User = 41
Eco1_User = 42
Eco2_User = 43
Edge_Cuts = 44
Margin = 45
B_CrtYd = 46
F_CrtYd = 47
B_Fab = 48
F_Fab = 49

MAX_LAYERS = 50
SCALE = 1000000.0

def get_active_layers(board):
    layer_dict = {BOARD_GetStandardLayerName(n):n for n in range(MAX_LAYERS)}
    layer_names = {s:n for n, s in layer_dict.iteritems()}
    plot_plan = []
    for n in layer_names:
         if board.IsLayerEnabled(n): plot_plan.append((layer_names[n], n, board.GetLayerName(n)))
    return plot_plan


def gen_pos_files(board, outdir="./tmp/", file_prefix=""):
    print 'create footprint pos files in %s' % outdir
    top_file = open(os.path.join(outdir,file_prefix+"-top-pos.csv"),"w+")
    bot_file = open(os.path.join(outdir,file_prefix+"-bot-pos.csv"),"w+")
    all_file = open(os.path.join(outdir,file_prefix+"-all-pos.csv"),"w+")

    origin = board.GetAuxOrigin()
    print "Board origin @:", origin
    i = 0
    for m in board.GetModules():
        i += 1
        line = ""
        pos = np.asarray(m.GetCenter() - origin)* 1e-6
        layer =  "Top" if m.GetLayerName() == "F.Cu" else "Bot"
        line += m.Reference().GetText()
        line += ","+str(m.GetFPID().GetLibItemName())
        line += ","+m.Value().GetText()
        line += ","+str(pos[0])
        line += ","+str(pos[1])
        line += ","+ str(m.GetOrientationDegrees())
        line += ","+ layer
        line += "\n"
        if m.GetLayerName() == "F.Cu":
            top_file.write(line)
        else:
            bot_file.write(line)
        all_file.write(line)
        print i,line
    top_file.close()
    bot_file.close()
    all_file.close()


def gen_gerbers(board, outdir="./tmp/"):
    pctl =  pcbnew.PLOT_CONTROLLER(board)
    popt = pctl.GetPlotOptions()
    popt.SetOutputDirectory(outdir)

    # Set some important plot options:
    popt.SetPlotFrameRef(False)     #do not change it
    popt.SetLineWidth(FromMM(0.35))
    popt.SetAutoScale(False)        #do not change it
    popt.SetScale(1)                #do not change it
    popt.SetMirror(False)
    popt.SetUseGerberAttributes(True)
    popt.SetUseGerberProtelExtensions(False)
    popt.SetExcludeEdgeLayer(False);
    popt.SetScale(1)
    popt.SetUseAuxOrigin(True)
    # This by gerbers only (also the name is truly horrid!)
    popt.SetSubtractMaskFromSilk(False)

    # Get all active layers
    plot_plan = get_active_layers(board)
    pctl = PLOT_CONTROLLER(board)
    popt = pctl.GetPlotOptions()
    popt.SetOutputDirectory(outdir)

    for layer_info in plot_plan:
        pctl.SetLayer(layer_info[1])
        pctl.OpenPlotfile(layer_info[0], PLOT_FORMAT_GERBER, layer_info[2])
        print 'Ploting: %s' % pctl.GetPlotFileName()
        if pctl.PlotLayer() == False:
            print "plot error"
    pctl.ClosePlot()


def gen_dril_files(board,outdir="./tmp/"):
    pctl =  pcbnew.PLOT_CONTROLLER(board)
    popt = pctl.GetPlotOptions()
    popt.SetOutputDirectory(outdir)
    popt.SetUseAuxOrigin(False)
    # Drill files.
    # sometimes a drill map file is asked (for verification purpose)
    drlwriter = EXCELLON_WRITER( board )
    drlwriter.SetMapFileFormat( PLOT_FORMAT_PDF )

    mirror = False
    minimalHeader = False
    offset = wxPoint(0,0)
    # False to generate 2 separate drill files (one for plated holes, one for non plated holes)
    # True to generate only one drill file
    mergeNPTH = False
    drlwriter.SetOptions( mirror, minimalHeader, offset, mergeNPTH )

    metricFmt = True
    drlwriter.SetFormat( metricFmt )

    genDrl = True
    genMap = True
    print 'create drill and map files in %s' % outdir
    drlwriter.CreateDrillandMapFilesSet( outdir, genDrl, genMap );

    # One can create a text file to report drill statistics
    rptfn = os.path.join(outdir,'drill_report.rpt')
    print 'report: %s' % rptfn
    drlwriter.GenDrillReportFile( rptfn );
    pctl.ClosePlot()

def gen_fab_files(board,outdir="./tmp/"):
    pctl =  pcbnew.PLOT_CONTROLLER(board)

    ## Assembly
    popt = pctl.GetPlotOptions()
    popt.SetOutputDirectory(outdir)
    popt.SetUseAuxOrigin(False)
    popt.SetSubtractMaskFromSilk(True)
    popt.SetPlotReference(True)
    popt.SetPlotValue(False)
    popt.SetPlotInvisibleText(False)
    popt.SetPlotReference(True)
    popt.SetPlotFrameRef(False)
    pctl.SetColorMode(True)
    #popt.SetReferenceColor(BLUE)

    for std_name, layer_id, user_name  in get_active_layers(board):
        print 'Ploting: %s' % pctl.GetPlotFileName()
        pctl.SetLayer(layer_id)
        pctl.OpenPlotfile(std_name, PLOT_FORMAT_PDF, user_name)
        pctl.SetColorMode(True)
        pctl.PlotLayer()
        pctl.ClosePlot()

    ## For documentation we want a general layout PDF
    popt = pctl.GetPlotOptions()
    popt.SetOutputDirectory(outdir)
    popt.SetUseAuxOrigin(False)
    popt.SetSubtractMaskFromSilk(False)
    popt.SetPlotReference(True)
    popt.SetPlotValue(False)
    popt.SetPlotInvisibleText(False)
    pctl.OpenPlotfile("General-Layout", PLOT_FORMAT_PDF, "General layout")
    pctl.SetColorMode(True)

    # User Comments
    popt.SetPlotReference(True)
    popt.SetPlotValue(False)
    popt.SetPlotInvisibleText(False)
    popt.SetPlotFrameRef(False)
    #pctl.SetLayer(Dwgs_User)
    #pctl.PlotLayer()

    popt.SetColor(GREEN)
    pctl.SetLayer(Cmts_User)
    pctl.PlotLayer()

    # Do the PCB edges in yellow
    popt.SetColor(YELLOW)
    pctl.SetLayer(Edge_Cuts)
    pctl.PlotLayer()

    # Bottom mask as lines only, in red
    #popt.SetMode(LINE)

    popt.SetColor(RED)
    pctl.SetLayer(B_Mask)
    pctl.PlotLayer()

    # Top mask as lines only, in blue
    popt.SetColor(BLUE)
    pctl.SetLayer(F_Mask)
    pctl.PlotLayer()

    # Top paste in light blue, filled
    popt.SetColor(BLUE)
    #popt.SetMode(FILLED)
    pctl.SetLayer(F_Paste)
    pctl.PlotLayer()

    # Top Silk in cyan, filled
    popt.SetColor(CYAN)
    pctl.SetLayer(F_SilkS)
    pctl.PlotLayer()
    pctl.ClosePlot()


def mkdir(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


if __name__ == '__main__':
    board =  pcbnew.LoadBoard(sys.argv[1])
    path = sys.argv[2]
    prefix = str(os.path.basename(sys.argv[1])).split('.')[0]
    path = os.path.join(sys.argv[2],"Gerbers")
    mkdir(path)
    gen_gerbers(board,outdir=path)
    path = os.path.join(sys.argv[2],"Drill_files")
    mkdir(path)
    gen_dril_files(board,outdir=path)
    path = os.path.join(sys.argv[2],"Assembly_files")
    mkdir(path)
    gen_fab_files(board,outdir=path)
    path = os.path.join(os.path.dirname(sys.argv[1]),sys.argv[2],"Footprint_Position_files")
    mkdir(path)
    gen_pos_files(board,outdir=path,file_prefix=prefix)
