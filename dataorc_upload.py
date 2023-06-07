import pydicom
from pathlib import Path
import subprocess
import re
from zipfile import ZipFile

dicompath = Path('/gpfs/projects/lcni/dcm/lcni/Sabb/AMP-SCZ_Prisma_VE11C_32ch_2021.07.14/')
project = 'PronetOR_oregon'
siteid = 'OR'
expected = 2519

try:
	subno = int(input('Enter subject number (digits only): '))
except ValueError:
	print('Invalid input, expected an integer')
	exit()

subject_name = f'{siteid}{subno:05d}'

# Assumes that dicoms are organized into folders starting with the subject name
subject_paths = sorted(dicompath.glob(f'{subject_name}*'))

if len(subject_paths) == 0:
	print(f'No dicoms found for {subject_name}')
	exit()
elif len(subject_paths) == 1:
	sub_path = subject_paths[0]
else:
	print(f'Found {len(subject_paths)} paths for {subject_name}: ')
	for index, x in enumerate(subject_paths):
		print(f'{index+1}. {x.name}')

	try:
		pathno = int(input(f'Enter a choice between 1 and {len(subject_paths)}: '))
	except ValueError:
		pathno = 0

	if pathno > len(subject_paths) or pathno < 1:
		print('Invalid choice')
		exit()
	else:
		sub_path = subject_paths[pathno-1]

correct = input(f'Is {sub_path.name} correct? [y/n] ').lower()
if correct[0] != 'y':
	print('aborting')
	exit()
		
print(f'Checking dicoms in {sub_path.name}')
example_dicom = next(sub_path.rglob('*.dcm'))
dcm = pydicom.dcmread(str(example_dicom))
subject_id = dcm.PatientID
study_date = dcm.StudyDate

expected_id = f'{subject_name}_MR_{study_date[:4]}_{study_date[4:6]}_{study_date[6:]}_[0-9]'
if not re.match(expected_id, subject_id):
	print(f'Subject ID from dicom ({subject_id}) does not match format {expected_id}')
	exit()

zipfile = f'{sub_path.name}.zip'

if Path(zipfile).exists() and input(f'{zipfile} exists, recreate? [y/n] ').lower() == 'n':
	print('Reusing existing file')
else:
	print(f'Creating {zipfile}')
	counter = 0
	with ZipFile(zipfile, 'w') as z:
		for dcmfile in sub_path.rglob('*.dcm'):
			# python 3.6.8 doesn't take a pathlike
			# Until they update the default python on the server we need to convert to str
			z.write(str(dcmfile), arcname=dcmfile.name)
			counter = counter + 1

	
	print(f'{counter} files written to {zipfile}')
	if counter != expected:
		print(f'Warning, expected {expected} files.')

if input('Proceed with upload? [y/n] ').lower() == 'y':
	subprocess.run(['echo', './dataorc', 'xnat-upload-session', '--host=https://xnat.med.yale.edu',
		f'--project={project}', f'--subject={subject_name}', f'--session={subject_id}',
		f'--session-archive={zipfile}'])

	subprocess.run(['./dataorc', 'xnat-upload-session', '--host=https://xnat.med.yale.edu',
		f'--project={project}', f'--subject={subject_name}', f'--session={subject_id}',
		f'--session-archive={zipfile}'])

if input('Remove zip file? [y/n] ').lower() == 'y':
	Path(zipfile).unlink()
