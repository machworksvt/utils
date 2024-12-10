import openvsp as vsp



vsp.ReadVSPFile("geometry\icarus_mk2.vsp3")
vsp.ExportFile("Airfoil_Metadata.csv", vsp.SET_ALL, vsp.EXPORT_SELIG_AIRFOIL)