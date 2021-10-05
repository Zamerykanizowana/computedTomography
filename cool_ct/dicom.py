import pydicom, random
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.sequence import Sequence

def save_dicom(image_data, output_file, patient_name):
    # File meta info data elements
    file_meta = FileMetaDataset()
    file_meta.FileMetaInformationGroupLength = 206
    file_meta.FileMetaInformationVersion = b'\x00\x01'
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
    file_meta.MediaStorageSOPInstanceUID = '1.2.826.0.1.3680043.8.498.51645380419494159785729751472725175471'
    file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1'
    file_meta.ImplementationClassUID = '1.2.826.0.1.3680043.8.498.1'
    file_meta.ImplementationVersionName = 'PYDICOM 2.0.0'

    image_rows, image_cols = image_data.shape

    # Main data elements
    ds = Dataset()
    ds.ImageType = ['ORIGINAL', 'PRIMARY', 'AXIAL']
    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
    ds.SOPInstanceUID = '1.2.826.0.1.3680043.8.498.51645380419494159785729751472725175471'
    ds.Modality = 'CT'
    ds.PatientName = patient_name
    ds.PatientID = str(random.randrange(1,100))
    ds.StudyInstanceUID = '1.2.826.0.1.3680043.8.498.75112040858074996916346159754932379994'
    ds.SeriesInstanceUID = '1.2.826.0.1.3680043.8.498.64119849432490865623274415908957426618'
    ds.InstanceNumber = '1'
    ds.FrameOfReferenceUID = '1.2.826.0.1.3680043.8.498.10194591012322579188814682575529857631'
    ds.ImagesInAcquisition = '1'
    ds.ImageComments = 'what a lovely image we have here...'
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = 'MONOCHROME2'
    ds.Rows = image_rows
    ds.Columns = image_cols
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = image_data.tobytes()

    ds.file_meta = file_meta
    ds.is_implicit_VR = False
    ds.is_little_endian = True
    ds.save_as(output_file, write_like_original=False)
