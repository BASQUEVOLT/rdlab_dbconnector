# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 10:00:42 2024

@author: EugenioCalandrini
"""

import matplotlib.pyplot as plt
import numpy as np
from DBconnector import DBConnector
from matplotlib.lines import Line2D

class Cell:
    def __init__(self, id):
        
        if "BQV" in id and '-' in id:
            self.id = id.split('-')[1][:3]+str(int(id.split('-')[1][3:]))
        else:
            self.id = id
        self.status = DBConnector().fetch_status(id)
        self.cycle = DBConnector().fetch_cycle(id)
        self.step = DBConnector().fetch_step(id)
        self.schedule = DBConnector().fetch_schedule(id)
        # self.parameters = DBConnector().fetch_cell_parameters(id)
        # self.formation = DBConnector().fetch_formation(id)
        self.test_id_dict = {}
        self.color = self.generate_random_color()
        
    def generate_random_color(self):
        """
        Generate a random RGB color.
        """
        color = np.random.randint(256, size=(1, 3))/255
        return color
                
        
    def split_data(self):
        for builder in self.schedule.Builder.unique():
            test_id = self.schedule.loc[self.schedule['Builder'] == builder, 'test_id'].iloc[0]
            self.test_id_dict[builder] = test_id
            
    def calculate_cycling(self):
        self.cycle["ce"] = self.cycle.specific_discharge_capacity/self.cycle.specific_charge_capacity*100
        self.cycle["rte"] = self.cycle.specific_discharge_energy/self.cycle.specific_charge_energy*100
        self.cycle["soh"] = self.cycle.specific_discharge_capacity/self.cycle[self.cycle.cycle_id == 5].specific_discharge_capacity*100
        # self.formation["specific_discharge_capacity"] = self.formation['capacity']/self.formation["active_material"]
        
    def get_cycles(self):
        # if self.status.
        print(self.cycle[self.cycle.soh < 80].cycle_id.iloc[1])
        
    def plot_cycling(self):
      
        df = self.cycle[self.cycle.test_id == self.test_id_dict["CY"]]
        df = df[['cycle_id', 'specific_discharge_capacity', 'ce', 'rte']]
        
        # Calculate the value at 80% of the 5th 'specific_discharge_capacity'
        value_80_percent = df.loc[5, 'specific_discharge_capacity'] * 0.8
        
        # Create figure and first axis
        fig, ax1 = plt.subplots()
        
        # Scatter plot for 'specific_discharge_capacity' on the first axis
        ax1.scatter(df['cycle_id'], df['specific_discharge_capacity'], color='blue', label='Specific Discharge Capacity')
        ax1.set_ylabel('Specific Discharge Capacity', color='blue')
        
        # Create second axis
        ax2 = ax1.twinx()
        
        # Scatter plot for 'ce' and 'rte' on the second axis
        ax2.scatter(df['cycle_id'], df['ce'], color='red', label='CE')
        ax2.scatter(df['cycle_id'], df['rte'], color='green', label='RTE')
        ax2.set_ylabel('CE / RTE', color='black')
        ax2.set_ylim(0, 125)
        
        # Plot horizontal dotted line at 80% of the 5th 'specific_discharge_capacity' value
        ax1.axhline(y=value_80_percent, color='black', linestyle=':', label='80% of SOH')
        
        # Get handles and labels for both axes
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        
        # Combine the handles and labels
        handles = handles1 + handles2
        labels = labels1 + labels2
        
        # Create the legend with combined handles and labels
        plt.legend(handles, labels, loc='lower left')
        
        plt.show()
        
    def plot_cycling2(self):
      
        df = self.cycle[self.cycle.test_id == self.test_id_dict["CY"]]
        df = df[['cycle_id', 'specific_discharge_capacity', 'ce', 'rte']]
        
        # Calculate the value at 80% of the 5th 'specific_discharge_capacity'
        value_80_percent = df.loc[5, 'specific_discharge_capacity'] * 0.8
    
        # Create a figure with two vertically stacked subplots
        fig, (ax2, ax1) = plt.subplots(2, 1, figsize=(8, 10), gridspec_kw={'height_ratios': [1, 3]}, sharex=True)
        
        # Plot 'specific_discharge_capacity' on the first subplot
        ax1.scatter(df['cycle_id'], df['specific_discharge_capacity'], color='blue', label='Specific Discharge Capacity')
        ax1.set_ylabel('Specific Discharge Capacity', color='blue')
        
        # Plot horizontal dotted line at 80% of the 5th 'specific_discharge_capacity' value on the first subplot
        ax1.axhline(y=value_80_percent, color='black', linestyle=':', label='80% of SOH')
        
        # Plot 'ce' and 'rte' on the second subplot
        ax2.scatter(df['cycle_id'], df['ce'], color='red', label='CE')
        ax2.scatter(df['cycle_id'], df['rte'], color='green', label='RTE')
        ax2.set_ylabel('CE / RTE', color='black')
        ax2.set_ylim(95, 105)
        ax1.set_xlabel('Cycles')
        
        # Set y-label for 'CE' with green color
        ax2.set_ylabel('CE', color='green')
        
        # Create a twin y-axis
        ax3 = ax2.twinx()
        ax3.set_ylim(95, 105)
        ax2.set_title(self.id)
        
        # Set y-label for 'RTE' with red color
        ax3.set_ylabel('RTE', color='red')
        
        # Adjust layout
        plt.tight_layout()
        
        # Get handles and labels for both subplots
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        
        # Combine the handles and labels
        handles = handles1 + handles2
        labels = labels1 + labels2
        
        # Create the legend with combined handles and labels on the first subplot
        ax1.legend(handles, labels, loc='lower left')
        
        plt.show()
        
    
class Cells:
    def __init__(self, ids):
        self.cells = []
        for id in ids:
            self.cells.append(Cell(id))
        self.preprocessing()    
        
    def preprocessing(self):
        cell_screen = []
        print("Passed ID", [cell.id for cell in self.cells])
        for i, cell in enumerate(self.cells):
            cell.split_data()
            # print(cell.id, cell.test_id_dict.keys())
            if ("CY" in cell.test_id_dict.keys() or "FMCY" in cell.test_id_dict.keys()) and cell.cycle.cycle_id.max() > 5:
                # print(cell.test_id_dict.keys())
                cell.calculate_cycling()
            else:
                cell_screen.append(i)
        for i in sorted(cell_screen, reverse=True): 
            popped = self.cells.pop(i)
            print("removed ID ", popped.id)

            
    def plot_cycling(self):
        
        legend_markers = [Line2D([0], [0], marker='v', color='k', linewidth=0), Line2D([0], [0], marker='s', color='k', markerfacecolor='none', linewidth=0)]
        fig, (ax2, ax1) = plt.subplots(2, 1, figsize=(6, 8), gridspec_kw={'height_ratios': [1, 4]}, sharex=True)
        
        value_80_percent = []
        # Plot 'specific_discharge_capacity' on the first subplot
        for cell in self.cells:
                
                if "BQV" in cell.id:
                    df = cell.cycle[cell.cycle.test_id == cell.test_id_dict["CY"]]
                elif "RDCC" in cell.id:
                    df = cell.cycle[cell.cycle.test_id == cell.test_id_dict["FMCY"]]
                df = df[['cycle_id', 'specific_discharge_capacity', 'ce', 'rte']]
                print(df[df.cycle_id == 5].cycle_id, df[df.cycle_id == 5].specific_discharge_capacity)
                value_80_percent.append(df[df.cycle_id == 5].specific_discharge_capacity.values * 0.8)
            
                ax1.scatter(df['cycle_id'], df['specific_discharge_capacity'],  edgecolor=cell.color, marker='o', facecolor='none', label=cell.id)
                
                # Plot 'ce' and 'rte' on the second subplot
                ax2.scatter(df['cycle_id'], df['ce'], c=cell.color, marker='v', label='CE')
                ax2.scatter(df['cycle_id'], df['rte'], edgecolor=cell.color, marker='s', facecolor='none', label='RTE')

        print(value_80_percent)
        # Plot horizontal dotted line at 80% of the 5th 'specific_discharge_capacity' value on the first subplot
        # ax1.axhline(y=np.array(value_80_percent).min(), color='black', linestyle=':', label='80% of SOH')
        
        # Set y-label for 'CE' with green color
        ax2.set_ylabel('CE / RTE (%)')
        ax2.set_ylim(90, 102)
        ax1.set_ylim(bottom=0)
        ax1.set_xlabel('Cycles')
        ax1.set_ylabel('Specific Discharge Capacity (mAh/g)')
        
        # Adjust layout
        plt.tight_layout()
        
        # Get handles and labels for both subplots
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        
        # Combine the handles and labels
        handles = handles1 + handles2
        labels = labels1 + labels2
        
        # Create the legend with combined handles and labels on the first subplot
        # ax1.legend(handles, labels, loc='lower left')
        ax1.legend(loc='lower left')
        # ax2.legend(handles=handles2, labels=labels2, loc='lower left', scatterpoints=1)
        ax2.legend(legend_markers, ["CE", "RTE"], loc='lower left', scatterpoints=1)
        
        plt.show()
        
    def plot_formation(self):
        
        legend_markers = [Line2D([0], [0], marker='v', color='k', linewidth=0), Line2D([0], [0], marker='s', color='k', markerfacecolor='none', linewidth=0)]
        fig, (ax2, ax1) = plt.subplots(2, 1, figsize=(8, 10), gridspec_kw={'height_ratios': [1, 1]}, sharex=True)
        
        # value_80_percent = []
        # Plot 'specific_discharge_capacity' on the first subplot
        for cell in self.cells:
            df = cell.formation
            # df = df[['cycle_id', 'specific_discharge_capacity', 'ce', 'rte']]
            # value_80_percent.append(df.loc[5, 'specific_discharge_capacity'] * 0.8)
        
            ax1.plot(df['TotalTime']/3600, df['voltage'], c=cell.color, label=cell.id)
            
            # Plot 'ce' and 'rte' on the second subplot
            ax2.plot(df['TotalTime']/3600, df['current'], c=cell.color)#, label='CE')
            # ax2.scatter(df['cycle_id'], df['rte'], edgecolor=color, marker='s', facecolor='none', label='RTE')

        
        # Plot horizontal dotted line at 80% of the 5th 'specific_discharge_capacity' value on the first subplot
        # ax1.axhline(y=value_80_percent[0], color='black', linestyle=':', label='80% of SOH')
        
        # Set y-label for 'CE' with green color
        ax2.set_ylabel('Current (Ah)')
        # ax2.set_ylim(90, 105)
        # ax1.set_ylim(bottom=0)
        ax1.set_xlabel('Time (h)')
        ax1.set_ylabel('Voltage (V)')
        
        # Adjust layout
        plt.tight_layout()
        
        # Get handles and labels for both subplots
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        
        # Combine the handles and labels
        handles = handles1 + handles2
        labels = labels1 + labels2
        
        # Create the legend with combined handles and labels on the first subplot
        # ax1.legend(handles, labels, loc='lower left')
        ax1.legend(loc='lower left')
        # ax2.legend(handles=handles2, labels=labels2, loc='lower left', scatterpoints=1)
        # ax2.legend(legend_markers, ["CE", "RTE"], loc='lower left', scatterpoints=1)
        
        plt.show()