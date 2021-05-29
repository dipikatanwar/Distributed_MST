import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib.pyplot as plt

class plot():
    @staticmethod
    def createBarChart(fileName, data):
        barWidth = 0.15
        ghsProgram = data['ghsProgram']
        ghsAlgo = data['ghsAlgo']
        br1 = np.arange(len(ghsProgram))
        br2 = [x + barWidth for x in br1]
        plt.bar(br1, ghsProgram, color ='maroon', width = barWidth,label ='Our Implementation')
        plt.bar(br2, ghsAlgo, color ='blue', width = barWidth,label ='GHS Theory: 2E + 5NlogN')
        plt.xlabel('Graph Nodes')
        plt.ylabel('Message Count')
        plt.xticks([r + barWidth for r in range(len(ghsAlgo))],data['Xlabel'])
        plt.title('Comparission of Message Count- Edge Density '+ str(data['density']))
        plt.legend()
        filename = os.path.join(os.getcwd(),'fig', fileName + '.pdf')
        # plt.savefig(filename, bbox_inches='tight')
        plt.savefig(filename)
        plt.clf()

    @staticmethod
    def createLineComparissionChart(fileName, data):
        x = data['Xlabel']
        y = data['ghsAlgo']
        plt.plot(x, y, color='maroon', marker='o', label='GHS Theory: 2E + 5NlogN')
        y1 = data['ghsProgram']
        plt.plot(x, y1, color='blue', marker='*', label='Our Implementation')
        plt.xlabel("Number of Nodes")
        plt.ylabel("Message Count")
        plt.title('Comparission of Message Count- Edge Density ' + str(data['density']))
        filename = os.path.join(os.getcwd(),'fig', fileName + '.pdf')
        plt.legend()
        plt.savefig(filename)
        plt.clf()
