#  ------------------------------------------------------------------------
#  File Name   : PO_GUI.py
#  Description : Graphical User Interface for Product Operator Formalism of spin-1/2
#  Tested      : Python 3.8.5, SymPy 1.11.1, NumPy 1.23.3, Tkinter 8.6.9, PO 1.3.0
#  Developer   : Dr. Kosuke Ohgo
#  ULR         : https://github.com/ohgo1977/PO_GUI_Python
#  Version     : 1.2.0
# 
#  Please read the manual (PO_GUI_Manual.pdf) for details.
# 
#  ------------------------------------------------------------------------
# 
# MIT License
#
# Copyright (c) 2023 Kosuke Ohgo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Version 1.2.0 on 8/23/2023
#  A default value of rho_str is automatically generated from the values in SpinLabel
#
# Version 1.1.1 on 8/22/2023
# rho was initialize as 0 to get rid out of unkonwn variable warninings.
#
# Version 1.1.0 on 8/21/2023
# Undo, Clear, and Save buttons were added.
#
# Version 1.0.0 on 8/18/2023

# Version Information
ver_str = 'version 1.2.0'
print('PO_GUI, ', ver_str)

# Import GUI library
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# Function to create undefined symbols. 
def check_symbols(val):
    # Replacing operators, parenthesis, and decimal point to comma. 
    val = val.replace('*',',')
    val = val.replace('/',',')
    val = val.replace('+',',')
    val = val.replace('-',',')
    val = val.replace('.',',')
    val = val.replace('(',',')
    val = val.replace(')',',')
    val = val.replace(' ','')
    sym_list = val.split(',') # Splitting to commponents separted by comma.

    # Creating new symbolic parameters
    for varname in sym_list:
        if varname != 'pi' and varname != '' and not varname.isnumeric() and varname not in globals():
            cmd_s = varname + " = symbols('" + varname + "')"
            exec(cmd_s, locals(), globals())

# Input Parameters
simp = input('Enter Method for Simplification (simplify, TR8, fu, Default: simplify): ')
if len(simp) == 0:
    simp = 'simplify'
print('Simplification: ', simp)

val = input('Enter Spin Labels Separated by Commas (Default: I,S): ')
if len(val) == 0:
    val = 'I,S'
val = val.replace(' ','')
print('Spin Labels: ', val)
SpinLabel = val.split(',')

rho_str_ini = ''
for ii in range(len(SpinLabel)):
    rho_str_ini = rho_str_ini + SpinLabel[ii] + 'z'
    if ii < len(SpinLabel) -1:
        rho_str_ini = rho_str_ini + ' + '
    elif ii == len(SpinLabel) -1:
        break
rho_str = input('Enter Initial Density Operator (Default: ' +  rho_str_ini + '):')
if len(rho_str) == 0:
    rho_str = rho_str_ini

# Import Product Operator
from PO import *
PO.create(SpinLabel)
from PO import * # Need this line to access Ix, Iy, ... created by PO.create().

# This line should be after PO.create()
check_symbols(rho_str)

# Initial Density Operator
rho = 0 # Dummy to get rid of errors
exec('rho = ' + rho_str, locals(), globals())
print('Initial Density Operator:')
print(rho)

# Set the simplification method
PO.simp = simp

rho_cell = [rho]

# Define Default Parameters as lists
# Pulse
FA = ['pi/4', 'pi/2', 'pi*3/4', 'pi', 'b']# Flip Angle
PH = ['x', 'y', '-x', '-y', 'f']# Phase

# Chemical Shift
CS = ['pi/2', 'pi', 'q']# Angle
for SL in SpinLabel:
    CS_tmp = 'o' + SL + '*t'
    CS.append(CS_tmp)

# J-coupling
JC_pair =[]
for ii, SL1 in enumerate(SpinLabel):
    for jj, SL2 in enumerate(SpinLabel):
        if jj > ii:
            JC_tmp = SL1 + SL2
            JC_pair.append(JC_tmp)

JC = ['pi/8', 'pi/4', 'pi/2', 'pi']# Angle
for ii, SL1 in enumerate(SpinLabel):
    for jj, SL2 in enumerate(SpinLabel):
        if jj > ii:
            JC_tmp = 'pi*J' + SL1[-1] + SL2[-1] + '*t'
            JC.append(JC_tmp)

JC_label = ['1/(8J)', '1/(4J)', '1/(2J)', '1/(J)']


class CalcGui(object):
    def __init__(self, app=None):

        # Window Setting
        app.title('PO_GUI '+ ver_str) # Window Title
        app.geometry('1150x700+10+10') # Window size and position, W x H + X + Y        
        app.lift()
        app.attributes('-topmost', True)
        app.after_idle(app.attributes, '-topmost', False)

        # Window Size
        PS_width = 500
        PS_height = 300
        CS_width = 500
        CS_height = 250
        JC_width = 600
        JC_height = 300
        Disp_width = 600
        Disp_height = 500
        Edit_width = 500
        Edit_height = 100

        padx_v=5
        pady_v=5

        Disp_text_height=15
        Disp_text_width=80

        # Font Size
        PS_font_size = 10
        CS_font_size = 10
        JC_font_size = 10
        Disp_font_size = 10
        Edit_font_size = 10

        # Switches
        PS_switch = 1
        CS_switch = 1
        JC_switch = 0
        if len(JC_pair) > 0:
            JC_switch = 1
        global Disp_switch
        Disp_switch = 1
        Edit_switch = 1

        ###### Pulse Section Starts #######
        if PS_switch == 1:
            
            # LabelFrame for Pulse
            PS_label_frame = ttk.LabelFrame(app, text='Pulse', width=PS_width, height=PS_height)
            PS_label_frame.propagate(False)
            PS_label_frame.grid(row=0, column=0, padx=padx_v, pady=pady_v)

            # Define
            self.FA_var = tk.StringVar()
            self.FA_var.set('pi/2')

            self.PH_var = tk.StringVar()
            self.PH_var.set('x')

            # Frame for Phase
            PH_frame = ttk.Frame(PS_label_frame)
            PH_frame.propagate(False)
            PH_frame.pack(anchor=tk.NW, padx=padx_v, pady=pady_v)

            # Label for Phase
            label = tk.Label(PH_frame, text='Phase', font=('Helvetica', PS_font_size))
            label.grid(row=0, column=0)
            label = tk.Label(PH_frame, text='Type-in', font=('Helvetica', PS_font_size))
            label.grid(row=0, column=len(PH))
            label = tk.Label(PH_frame, text='Selected', font=('Helvetica', PS_font_size))
            label.grid(row=0, column=len(PH)+1)

            # Button for Phase
            for x, num in enumerate(PH):
                button = tk.Button(PH_frame, text=num, font=('Helvetica', PS_font_size), width=6, height=3)
                button.grid(row=1, column=x)
                button.bind('<Button-1>', self.click_PH_button)

            button = tk.Entry(PH_frame, font=('Helvetica',PS_font_size), width=6, textvariable=self.PH_var)
            button.grid(row=1, column=x+1)

            button = tk.Label(PH_frame, textvariable=self.PH_var, font=('Helvetica',PS_font_size), width=6, height=3)
            button.grid(row=1, column=x+2)

            # Frame for Flip Angle
            FA_frame = ttk.Frame(PS_label_frame)
            FA_frame.propagate(False)
            FA_frame.pack(anchor=tk.W, padx=padx_v, pady=pady_v)

            # Label for Flip Angle
            label = tk.Label(FA_frame, text='Flip Angle', font=('Helvetica', PS_font_size))
            label.grid(row=0, column=0)
            label = tk.Label(FA_frame, text='Type-in', font=('Helvetica', PS_font_size))
            label.grid(row=0, column=len(FA))
            label = tk.Label(FA_frame, text='Selected', font=('Helvetica', PS_font_size))
            label.grid(row=0, column=len(FA)+1)

            # Button for Flip Angle
            for x, num in enumerate(FA):
                button = tk.Button(FA_frame, text=num, font=('Helvetica', PS_font_size), width=6, height=3)
                button.grid(row=1, column=x)
                button.bind('<Button-1>', self.click_FA_button)

            button = tk.Entry(FA_frame, font=('Helvetica',PS_font_size), width=8, textvariable=self.FA_var)
            button.grid(row=1, column=x+1)

            button = tk.Label(FA_frame, textvariable=self.FA_var, font=('Helvetica',PS_font_size), width=8, height=3)
            button.grid(row=1, column=x+2)

            # Frame for Pulse
            Pulse_frame = ttk.Frame(PS_label_frame)
            Pulse_frame.propagate(False)
            Pulse_frame.pack(anchor=tk.SW, padx=padx_v, pady=pady_v)

            # Label for Pulse
            label = tk.Label(Pulse_frame, text='Apply Pulse to', font=('Helvetica', PS_font_size))
            label.grid(row=0, column=0)

            # Button for Pulse
            for x, num in enumerate(SpinLabel):
                button = tk.Button(Pulse_frame, text=num, font=('Helvetica', PS_font_size),  width=10, height=3)
                button.grid(row=1, column=x)
                button.bind('<Button-1>', self.click_PULSE_button)
        ####### Pulse Section Ends ####### 

        ####### Cheimical Shift Section Starts #######
        if CS_switch == 1:
            # LabelFrame for Chemical Shift
            CS_label_frame = ttk.LabelFrame(app, text='Chemical Shift', width=CS_width, height=CS_height)
            CS_label_frame.propagate(False) 
            CS_label_frame.grid(row=1, column=0, padx=padx_v, pady=pady_v, sticky=tk.N)

            # Define
            self.CS_var = tk.StringVar()
            self.CS_var.set('q')

            # Frame for CS Angle
            CSAngle_frame = ttk.Frame(CS_label_frame)
            CSAngle_frame.propagate(False)
            CSAngle_frame.pack(anchor=tk.NW, padx=padx_v, pady=pady_v)

            # Label for CS Angle
            label = tk.Label(CSAngle_frame, text='Angle', font=('Helvetica', CS_font_size))
            label.grid(row=0, column=0)
            label = tk.Label(CSAngle_frame, text='Type-in', font=('Helvetica', CS_font_size))
            label.grid(row=0, column=len(CS))
            label = tk.Label(CSAngle_frame, text='Selected', font=('Helvetica', CS_font_size))
            label.grid(row=0, column=len(CS)+1)

            # Button for CS Angle
            for x, num in enumerate(CS):
                button = tk.Button(CSAngle_frame, text=num, font=('Helvetica', CS_font_size), width=6, height=3)
                button.grid(row=1, column=x, sticky='nsew')
                button.bind('<Button-1>', self.click_CSAngle_button)

            button = tk.Entry(CSAngle_frame, font=('Helvetica',CS_font_size), width=8, textvariable=self.CS_var)
            button.grid(row=1, column=x+1)

            button = tk.Label(CSAngle_frame, textvariable=self.CS_var, font=('Helvetica',CS_font_size), width=8, height=3)
            button.grid(row=1, column=x+2)

            # Frame for CS
            CS_frame = ttk.Frame(CS_label_frame)
            CS_frame.propagate(False)
            CS_frame.pack(anchor=tk.SW, padx=padx_v, pady=pady_v)

            # Label for CS
            label = tk.Label(CS_frame, text='Apply CS to', font=('Helvetica', CS_font_size))
            label.grid(row=0, column=0)

            # Button for CS
            for x, num in enumerate(SpinLabel):
                button = tk.Button(CS_frame, text=num, font=('Helvetica', CS_font_size),  width=10, height=3)
                button.grid(row=1, column=x)
                button.bind('<Button-1>', self.click_CS_button)

        ####### Cheimical Shift Section Ends #######

        ####### J-coupling Section Starts #######
        if JC_switch == 1:
            
            # LabelFrame for J-coupling
            JC_label_frame = ttk.LabelFrame(app, text='J-Coupling', width=JC_width, height=JC_height)
            JC_label_frame.propagate(False)
            JC_label_frame.grid(row=0, column=1, padx=padx_v, pady=pady_v)

            # Define
            self.JC_var = tk.StringVar()
            self.JC_var.set('pi/2')

            # Frame for JC Angle
            JCAngle_frame = ttk.Frame(JC_label_frame)
            JCAngle_frame.propagate(False)
            JCAngle_frame.pack(anchor=tk.NW, padx=padx_v, pady=pady_v)

            # Label for JC Label
            label = tk.Label(JCAngle_frame, text='Angle', font=('Helvetica', JC_font_size))
            label.grid(row=0, column=0)

            for x, num in enumerate(JC_label):
                label = tk.Label(JCAngle_frame, text=num, font=('Helvetica', JC_font_size), width=6, height=3)
                label.grid(row=1, column=x, sticky='nsew')

            label = tk.Label(JCAngle_frame, text='Type-in', font=('Helvetica', JC_font_size))
            label.grid(row=1, column=len(JC))
            label = tk.Label(JCAngle_frame, text='Selected', font=('Helvetica', JC_font_size))
            label.grid(row=1, column=len(JC)+1)

            # Button for JC Angle
            for x, num in enumerate(JC):
                button = tk.Button(JCAngle_frame, text=num, font=('Helvetica', JC_font_size), width=6, height=3)
                button.grid(row=2, column=x, sticky='nsew')
                button.bind('<Button-1>', self.click_JCAngle_button)

            button = tk.Entry(JCAngle_frame, font=('Helvetica',JC_font_size), width=8, textvariable=self.JC_var)
            button.grid(row=2, column=x+1)

            button = tk.Label(JCAngle_frame, textvariable=self.JC_var, font=('Helvetica',JC_font_size), width=8, height=3)
            button.grid(row=2, column=x+2)

            # Frame for JC pairs
            JC_frame = ttk.Frame(JC_label_frame)
            JC_frame.propagate(False)
            JC_frame.pack(anchor=tk.SW, padx=padx_v, pady=pady_v)

            # Label for JC pairs
            label = tk.Label(JC_frame, text='Apply JC to', font=('Helvetica', JC_font_size))
            label.grid(row=0, column=0)

            # Button for JC
            for x, num in enumerate(JC_pair):
                button = tk.Button(JC_frame, text=num, font=('Helvetica', JC_font_size),  width=10, height=3)
                button.grid(row=1, column=x)
                button.bind('<Button-1>', self.click_JC_button)

        ####### J-coupling Section Ends #######

        ###### Display Section Starts #######
        if Disp_switch == 1:

            # Define
            self.prev_logs = rho.logs
            self.disp_logs = str(self.prev_logs) # Initilize self.disp_logs

            # LabelFrame for Display
            Disp_label_frame = ttk.LabelFrame(app, text='Spin Dynamics', width=Disp_width, height=Disp_height)
            Disp_label_frame.propagate(False)
            Disp_label_frame.grid(row=1, column=1, padx=padx_v, pady=pady_v)

            self.Disp_text = tk.Text(Disp_label_frame, 
                                    font=('Helvetica', Disp_font_size), wrap='word',
                                    width=Disp_text_width, height=Disp_text_height)

            self.Disp_text.propagate(False)
            self.Disp_text.insert('1.0', 'Simplification: ' + simp + '\n' + 'Initial Density Operator: ' + rho.logs)
            self.Disp_text.config(state='disabled')
            self.Disp_text.grid(row=0, column=0)

            scrollbar = tk.Scrollbar(Disp_label_frame, orient=tk.VERTICAL, command=self.Disp_text.yview)
            self.Disp_text["yscrollcommand"] = scrollbar.set
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        ###### Display Section Ends #######

        ####### Edit Section Starts #######
        if Edit_switch == 1:
            # LabelFrame for Chemical Shift
            Edit_label_frame = ttk.LabelFrame(app, text='Edit', width=Edit_width, height=Edit_height)
            Edit_label_frame.propagate(False) 
            Edit_label_frame.grid(row=2, column=0, padx=padx_v, pady=pady_v, sticky=tk.NW)

            button = tk.Button(Edit_label_frame, text='Undo', font=('Helvetica', Edit_font_size), width=6, height=3)
            button.grid(row=0, column=0, sticky='nsew')
            button.bind('<Button-1>', self.Undo_button)

            button = tk.Button(Edit_label_frame, text='Clear', font=('Helvetica', Edit_font_size), width=6, height=3)
            button.grid(row=0, column=1, sticky='nsew')
            button.bind('<Button-1>', self.Clear_button)

            button = tk.Button(Edit_label_frame, text='Save', font=('Helvetica', Edit_font_size), width=6, height=3)
            button.grid(row=0, column=2, sticky='nsew')
            button.bind('<Button-1>', self.Save_button)

        ####### Edit Section Ends #######

    ####### Pulse ####### 
    def click_FA_button(self, event):
        check = event.widget['text']
        self.FA_var.set(check)

    def click_PH_button(self, event):
        check = event.widget['text']
        self.PH_var.set(check)

    def click_PULSE_button(self, event):
        FA_str = self.FA_var.get()
        check_symbols(FA_str)
        PH_str = self.PH_var.get()
        check_symbols(PH_str)
        check = event.widget['text']

        if PH_str in PH[0:4]: # Quadrature Phase
            cmd_s = 'rho = rho.pulse(["' + check + '"], ["' + PH_str + '"], [' + FA_str + '])'
        else: # Arbitrary phase 
            cmd_s = 'rho = rho.pulse_phshift(["' + check + '"], [' + PH_str + '], [' + FA_str + '])'

        exec(cmd_s, locals(), globals())
        rho_cell.append(rho)
        
        CalcGui.update_Disp_text(self)
    ####### Pulse #######

    ####### Chemical Shift ####### 
    def click_CSAngle_button(self, event):
        check = event.widget['text']
        self.CS_var.set(check)

    def click_CS_button(self, event):
        CS_str = self.CS_var.get()
        check_symbols(CS_str)
        check = event.widget['text']
        cmd_s = 'rho = rho.cs(["' + check + '"], [' + CS_str + '])'

        exec(cmd_s, locals(), globals())
        rho_cell.append(rho)

        CalcGui.update_Disp_text(self)
    ####### Chemical Shift ####### 

    ####### J-coupling ####### 
    def click_JCAngle_button(self, event):
        check = event.widget['text']
        self.JC_var.set(check)

    def click_JC_button(self, event):
        JC_str = self.JC_var.get()
        check_symbols(JC_str)
        check = event.widget['text']
        cmd_s = 'rho = rho.jc(["' + check + '"], [' + JC_str + '])'
        exec(cmd_s, locals(), globals())
        rho_cell.append(rho)

        CalcGui.update_Disp_text(self)
    ####### J-coupling #######

    ####### Display #######
    def update_Disp_text(self):
        if Disp_switch == 1:
            new_logs = '\n' + rho.logs[len(self.prev_logs):]
            self.disp_logs = self.disp_logs + new_logs
            CalcGui.reset_Disp_text(self)
            self.prev_logs = rho.logs

    ####### Display #######

    ####### Edit #######
    def Undo_button(self, event):
        if len(rho_cell) > 1:
            len_tmp = len(rho_cell[-1].logs) - len(rho_cell[-2].logs)
            self.disp_logs = self.disp_logs[:-len_tmp-1]# Include \n
            if len(rho_cell) == 2: # Initial condition
                self.prev_logs = rho_cell[-2].logs
            else:
                self.prev_logs = rho_cell[-3].logs
            exec('rho = rho_cell[-2]', locals(), globals()) # Update rho. exec() should be used.
            exec('rho_cell = rho_cell[:-1]', locals(), globals()) # Delete the last element of rho_cell. exec() should be used.
            # ele = rho_cell.pop() # Delete the last element, this line also works.
            CalcGui.reset_Disp_text(self)

    def Clear_button(self, event):
            self.prev_logs = rho_cell[0].logs
            self.disp_logs = str(self.prev_logs) # Initilize self.disp_logs
            exec('rho = rho_cell[0]', locals(), globals()) # Update rho as globals
            exec('rho_cell = [rho]', locals(), globals())
            CalcGui.reset_Disp_text(self)

    def Save_button(self, event):
        file = filedialog.asksaveasfilename(
                            filetypes=[("txt file", ".txt")],
                            defaultextension=".txt",
                            initialfile="PO_Result.txt")
        fob=open(file,'w')
        fob.write('Simplification: ' + simp + '\n' + 'Initial Density Operator: ' + self.disp_logs)
        fob.close()
        return "break"# Without this line, Save_button has been sunken
        
    ####### Edit #######

    ####### Utility #######
    def reset_Disp_text(self):
        self.Disp_text.config(state='normal')
        self.Disp_text.delete('1.0',self.Disp_text.index(tk.END))
        self.Disp_text.insert('1.0', 'Simplification: ' + simp + '\n' + 'Initial Density Operator: ' + self.disp_logs)
        self.Disp_text.config(state='disabled')
        self.Disp_text.see('end')
    ####### Utility #######

####### Main #######
def main():
    # Window Setting
    app = tk.Tk()

    # Window size non resizable
    app.resizable(width=False, height=False)
    CalcGui(app)

    # Display
    app.mainloop()

if __name__ == '__main__':
    main()