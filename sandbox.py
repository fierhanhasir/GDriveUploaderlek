from Core.DriveAPI import Manipulation
import os


pid = '1prL7ghxu56KOVaPMgyr-YGTuaeScvKye'
mnp = Manipulation(pid)
nm = 'cakamata'
path = os.path.join(os.getcwd()+"\Task\cakamata.jpg")

mnp.show_all()