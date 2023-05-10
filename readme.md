Call the script from the same directory where dataorc is installed, or change the subprocess command to include the full path to the binary

Script assumes the dicom path has folders for each session, with names starting with the subject name, and that dicom files end in .dcm. If your data is organized differently you may need to tweak the script a bit.

Otherwise just change the dicompath, siteid, project, and expected number of files to match your site.

The script requires the pydicom module.

You can enter the subject number without leading zeros.

You can safely hit ctrl-c when you see the message to kill the script. You won't reach the part of the script that optionally deletes the zip file if you do that.
